import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os
import json

# Initialize Firebase
def initialize_firebase():
    try:
        # Load Firebase credentials from environment variable
        firebase_json = os.getenv("FIREBASE_CREDENTIALS")

        if not firebase_json:
            raise ValueError("Firebase credentials not found in environment variables")

        cred_dict = json.loads(firebase_json)
        
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://smartaid-6c5c0-default-rtdb.firebaseio.com/'
            })
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

# Initialize Firebase connection
firebase_initialized = initialize_firebase()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

def fetch_firebase_data():
    """Fetch data from Firebase Realtime Database"""
    try:
        if not firebase_initialized:
            return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                      'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])
        
        # Get reference to the database
        ref = db.reference('/detections')  # Adjust this path based on your Firebase structure
        
        # Fetch data
        data = ref.get()
        
        # Convert to DataFrame
        if data:
            # Convert the dictionary to a list of records
            records = []
            for timestamp, values in data.items():
                record = values.copy()
                record['timestamp'] = datetime.fromtimestamp(float(timestamp))
                records.append(record)
            
            df = pd.DataFrame(records)
            
            # Ensure all expected columns are present
            expected_columns = ['timestamp', 'event_type', 'label', 'confidence',
                               'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP']
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Clean temperature data if needed
            if 'TEMP' in df.columns and df['TEMP'].dtype == object:
                df['TEMP'] = df['TEMP'].astype(str).str.replace('°C', '').astype(float)
            
            return df
        else:
            return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                      'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])
    except Exception as e:
        print(f"Error fetching Firebase data: {e}")
        return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                   'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])

# =============================================
# Dashboard Layout
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    # Title
    dbc.Row([
        dbc.Col(html.H1("Smart Hat Analytics Dashboard", 
                       className="text-center my-4"))
    ]),
    
    # Refresh interval
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),
    
    # Connection status indicator
    dbc.Row([
        dbc.Col(html.Div(id='connection-status', className="text-center mb-3"))
    ]),
    
    # System Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("CPU Usage (%)", className="h5"),
            dbc.CardBody(dcc.Graph(id='cpu-graph'))
        ], className="shadow"), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Memory Usage (%)", className="h5"),
            dbc.CardBody(dcc.Graph(id='mem-graph'))
        ], className="shadow"), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Temperature (°C)", className="h5"),
            dbc.CardBody(dcc.Graph(id='temp-graph'))
        ], className="shadow"), md=4)
    ], className="mb-4"),
    
    # Detection Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Frequency", className="h5"),
            dbc.CardBody(dcc.Graph(id='detection-freq'))
        ], className="shadow"), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Confidence", className="h5"),
            dbc.CardBody(dcc.Graph(id='confidence-hist'))
        ], className="shadow"), md=6)
    ], className="mb-4"),
    
    # Distance and Performance Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Object Distance (cm)", className="h5"),
            dbc.CardBody(dcc.Graph(id='distance-graph'))
        ], className="shadow"), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Frames Per Second", className="h5"),
            dbc.CardBody(dcc.Graph(id='fps-graph'))
        ], className="shadow"), md=6)
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Event Log", className="h5"),
            dbc.CardBody(
                dash_table.DataTable(
                    id='data-table',
                    columns=[{"name": i, "id": i} for i in [
                        'timestamp', 'event_type', 'label', 'confidence',
                        'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'
                    ]],
                    page_size=10,
                    style_table={'overflowX': 'auto', 'height': '300px'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'backgroundColor': 'rgba(0,0,0,0)',
                        'color': 'white',
                        'border': '1px solid #444'
                    },
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'fontWeight': 'bold'
                    },
                    filter_action="native",
                    sort_action="native"
                )
            )
        ], className="shadow"), width=12)
    ])
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
     Output('data-table', 'data'),
     Output('connection-status', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = fetch_firebase_data()
    
    # Create connection status indicator
    if firebase_initialized:
        status = dbc.Alert("Connected to Firebase Realtime Database", color="success")
    else:
        status = dbc.Alert("Failed to connect to Firebase", color="danger")
    
    if df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            margin={'l': 40, 'r': 40, 't': 30, 'b': 30},
            xaxis={'gridcolor': '#444'},
            yaxis={'gridcolor': '#444'}
        )
        empty_fig.add_annotation(text="No data available",
                                xref="paper", yref="paper",
                                x=0.5, y=0.5, showarrow=False)
        
        return (
            empty_fig, empty_fig, empty_fig,
            empty_fig, empty_fig,
            empty_fig, empty_fig,
            [],
            status
        )
    
    # Filter data
    system_stats = df[df['event_type'] == 'system_stats'].copy()
    detections = df[df['event_type'] == 'detection'].copy()
    
    # Create figures
    cpu_fig = px.line(
        system_stats, x='timestamp', y='CPU',
        title='', labels={'CPU': 'Usage %'},
        color_discrete_sequence=['#1f77b4']
    )
    
    mem_fig = px.line(
        system_stats, x='timestamp', y='MEM',
        title='', labels={'MEM': 'Usage %'},
        color_discrete_sequence=['#ff7f0e']
    )
    
    temp_fig = px.line(
        system_stats, x='timestamp', y='TEMP',
        title='', labels={'TEMP': '°C'},
        color_discrete_sequence=['#d62728']
    ).add_hline(y=80, line_dash="dash", line_color="red")
    
    detection_freq = px.histogram(
        detections, x='timestamp', 
        title='', labels={'timestamp': 'Time'},
        color_discrete_sequence=['#2ca02c']
    )
    
    confidence_hist = px.histogram(
        detections, x='confidence',
        title='', labels={'confidence': 'Score'},
        color_discrete_sequence=['#9467bd']
    )
    
    distance_fig = px.scatter(
        detections, x='timestamp', y='estimated_distance_cm',
        color='confidence',
        title='', labels={'estimated_distance_cm': 'Distance (cm)'},
        color_continuous_scale='Viridis'
    )
    
    fps_fig = px.scatter(
        detections, x='timestamp', y='FPS',
        title='', labels={'FPS': 'Frames Per Second'},
        color_discrete_sequence=['#17becf']
    )
    
    # Apply consistent styling
    for fig in [cpu_fig, mem_fig, temp_fig, detection_freq, 
               confidence_hist, distance_fig, fps_fig]:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            margin={'l': 40, 'r': 40, 't': 30, 'b': 30},
            xaxis={'gridcolor': '#444'},
            yaxis={'gridcolor': '#444'}
        )
    
    return (
        cpu_fig, mem_fig, temp_fig,
        detection_freq, confidence_hist,
        distance_fig, fps_fig,
        df.to_dict('records'),
        status
    )

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
