import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# =============================================
# Firebase Configuration with Enhanced Error Handling
# =============================================

def initialize_firebase():
    """Initialize Firebase with proper error handling"""
    try:
        if not firebase_admin._apps:
            # Get environment variables with validation
            required_vars = [
                'FIREBASE_PROJECT_ID',
                'FIREBASE_PRIVATE_KEY_ID',
                'FIREBASE_PRIVATE_KEY',
                'FIREBASE_CLIENT_EMAIL',
                'FIREBASE_CLIENT_ID',
                'FIREBASE_CLIENT_CERT_URL'
            ]
            
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            if missing_vars:
                raise ValueError(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
            
            firebase_config = {
                "type": "service_account",
                "project_id": os.environ["FIREBASE_PROJECT_ID"],
                "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
                "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
                "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
                "client_id": os.environ["FIREBASE_CLIENT_ID"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ["FIREBASE_CLIENT_CERT_URL"]
            }
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    
    except Exception as e:
        print(f"🔥 Firebase initialization failed: {str(e)}")
        return None

# Initialize Firebase connection
db = initialize_firebase()

# =============================================
# Data Loading from Firebase
# =============================================

def load_data_from_firebase():
    """Fetch data from Firebase Firestore with error handling"""
    try:
        if not db:
            raise ConnectionError("No Firebase connection available")
            
        # Get all documents from the collection
        docs = db.collection('detection_data').stream()
        
        # Convert to list of dictionaries
        data = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id  # Include document ID
            data.append(doc_data)
        
        # Convert to DataFrame with proper column handling
        columns = ['timestamp', 'event_type', 'label', 'confidence',
                  'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP']
        
        df = pd.DataFrame(data, columns=columns)
        
        # Convert timestamp if it exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        return df
    
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                   'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])

# =============================================
# Dashboard Layout
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col(html.H1("SmartAID Analytics Dashboard", className="text-center mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='cpu-graph'), md=6),
        dbc.Col(dcc.Graph(id='mem-graph'), md=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='temp-graph'), md=6),
        dbc.Col(dcc.Graph(id='detection-freq'), md=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='confidence-hist'), md=6),
        dbc.Col(dcc.Graph(id='distance-graph'), md=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='fps-graph'), width=12)
    ]),
    
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in [
                    'timestamp', 'event_type', 'label', 'confidence',
                    'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'
                ]],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'minWidth': '100px', 'width': '100px', 'maxWidth': '180px',
                    'whiteSpace': 'normal'
                },
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white'
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                }
            ),
            width=12
        )
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every 1 minute
        n_intervals=0
    )
])

# =============================================
# Callbacks
# =============================================

@app.callback(
    [Output('cpu-graph', 'figure'),
     Output('mem-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('detection-freq', 'figure'),
     Output('confidence-hist', 'figure'),
     Output('distance-graph', 'figure'),
     Output('fps-graph', 'figure'),
     Output('data-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = load_data_from_firebase()
    
    if df.empty:
        empty_fig = px.scatter(title="No Data Available")
        return [empty_fig] * 7 + [df.to_dict('records')]
    
    # Filter data for different visualizations
    system_stats = df[df['event_type'] == 'system_stats'].dropna(subset=['CPU', 'MEM', 'TEMP'])
    detections = df[df['event_type'] == 'detection'].dropna(subset=['confidence', 'estimated_distance_cm'])
    
    # Create figures with error handling
    try:
        cpu_fig = px.line(
            system_stats, x='timestamp', y='CPU',
            title='CPU Usage Over Time',
            labels={'CPU': 'CPU Usage (%)', 'timestamp': 'Time'},
            template='plotly_dark'
        ) if not system_stats.empty else px.scatter(title="No System Stats Available")
        
        mem_fig = px.line(
            system_stats, x='timestamp', y='MEM',
            title='Memory Usage Over Time',
            labels={'MEM': 'Memory Usage (%)', 'timestamp': 'Time'},
            template='plotly_dark'
        ) if not system_stats.empty else px.scatter(title="No System Stats Available")
        
        temp_fig = px.line(
            system_stats, x='timestamp', y='TEMP',
            title='Temperature Over Time',
            labels={'TEMP': 'Temperature (°C)', 'timestamp': 'Time'},
            template='plotly_dark'
        ) if not system_stats.empty else px.scatter(title="No System Stats Available")
        
        detection_freq = px.histogram(
            detections, x='timestamp',
            title='Detection Frequency',
            labels={'timestamp': 'Time', 'count': 'Detections'},
            template='plotly_dark'
        ) if not detections.empty else px.scatter(title="No Detections Available")
        
        confidence_hist = px.histogram(
            detections, x='confidence',
            title='Confidence Distribution',
            labels={'confidence': 'Confidence Score', 'count': 'Count'},
            template='plotly_dark'
        ) if not detections.empty else px.scatter(title="No Detections Available")
        
        distance_fig = px.scatter(
            detections, x='timestamp', y='estimated_distance_cm',
            title='Estimated Distance Over Time',
            labels={'estimated_distance_cm': 'Distance (cm)', 'timestamp': 'Time'},
            template='plotly_dark'
        ) if not detections.empty else px.scatter(title="No Detections Available")
        
        fps_fig = px.line(
            df[df['FPS'].notna()], x='timestamp', y='FPS',
            title='Frames Per Second Over Time',
            labels={'FPS': 'FPS', 'timestamp': 'Time'},
            template='plotly_dark'
        ) if 'FPS' in df.columns and not df[df['FPS'].notna()].empty else px.scatter(title="No FPS Data Available")
        
        return (
            cpu_fig, mem_fig, temp_fig,
            detection_freq, confidence_hist,
            distance_fig, fps_fig,
            df.to_dict('records')
        )
    
    except Exception as e:
        print(f"Error generating figures: {e}")
        error_fig = px.scatter(title=f"Error: {str(e)}")
        return [error_fig] * 7 + [df.to_dict('records')]

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
