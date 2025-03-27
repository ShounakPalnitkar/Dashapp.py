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
# Firebase Configuration with Direct Credentials
# =============================================

def initialize_firebase():
    """Initialize Firebase with direct credentials (for development)"""
    try:
        if not firebase_admin._apps:
            firebase_config = {
                "type": "service_account",
                "project_id": "smartaid-6c5c0",
                "private_key_id": "4ca2f01452ce8893c8723ed1b746c9d0d2c86445",
                "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDC9pRncbYZNLbj
2+6W7UOxNvCsOD2g2lFZcrhyuPkYAsQTrMZP5heBGQB7Y3jqU10McPxJ1l/7Y1cm
CVmjz1ea8yTjXk7dJr3IThlZt2uc5BzY82NyktwvpSqwbn9MpXRy3jE/AYfAj0gk
IfW7bxb6T+14Ybi+LbcjjSlTOv93Pof6Znwo+z//XIVBIfdMVui0+4qg/DKm0o3S
I260Q6s1jIy7bYRahSxfQRRqF0ru/NznJwRMmcKpkt9/8LzgK4E79VqUh1XJ2ruA
4oUVYbO+4EYm66MBjDEL+e15pGGmn+XOxep7MsTDtz393HvEKAVsq+gOlHpD8zoQ
XspzUlt7AgMBAAECggEAMOICc61fKxK8iIUsXUtAHb7YuVWgniQfIX5SIPGgAxUu
dIBteLsISaYrKMTYHGiqe+QYXasShcVypGbTwu7J2F/+b8PFok2EaCSs1oHWyY+o
a/0agi+wZYHUIkiSQnV5rRNo5ZNMpktGm0iohEZmTHyd3gEigQyVTqSmJ+gzBYKH
3f26nAhw2tIodtZ4dzeqgEeT1/k9fbBGg1kr5jbzpAbQWoPKcuJYK++XmRpy5Bwo
zT7SPrVXKms1kikOSE8Z/vsOR2WggVg8KU/VrEWWdY8HMPVT9XnyNdp0XxTWiEZr
vNXTqc67TAWy1SMqRaiJgM+OT3xcq0kzZGAsUp4rgQKBgQDwsq+qPgswHZT9OhNJ
shVXejDm5t6bPj+4uKJAqJl8FrTskzM8wuWJghd5AWDJBuETQGYnKmblIjEkmN31
+Y7+QV7DMIUBrOUxmtNNKI3+iFyKHMq3SK5eZc/anSw9yReCWUrDttJJe3tNID73
ZpOgIRTh1H1WksMsUn87LUqsdwKBgQDPW5GLeLmFPLdHE8lkWnDm2spTeBrDq6lz
VFZRM8C2zSsQDvyh+SNT30j1wis6Y4MIkfH6Vi2KBviJ1mTHoJt6iJfhYrOvfIrj
3GZ6inB0ukrzoH4SMMxBFCTt0hsTNZKLyjVZIBIhoHXKD2A0tgbS1AxxrVYD6m2k
1j8E4qg+HQKBgQCRVwRVoxM0YZh2c9vzsxHJ+aGPu7aNPUBS9UIcEvJjCH8FHzlg
JjteFezAh4F+waWk70z/t03cbBIKjDfy8FdU1fo3mJOn2FOo6VlQDP34xTRDvXD2
zW9k1st0sVVmlYeZkPthRIKkFmj0wFTlJM5dcbxfROTOIt6xY7sp64ZcrwKBgELt
neke7Gp4/n6RoZYtniaNpoP5Z+MGJSbM42HdzLdOS20BepfodsOJkYmc4Wb2J2wRM
Hv8/C4nOgC/1LCgm1agyKFuOARM2LponTEhnIK78Zi7GcYqrh3HF77l3JFgJ5ZgL
FzcCG/gQk5Q5bEL3MbKg0LdsTCQNaYBXypVoFwedAoGAcYjcBY+rCpvapxqmZ9JZ
Whj1zxY3mARNzRM1C4n4Z2E33PRcHe6YjyEaZNU2xbW5A05F6/Dhcs6jiu0P5z8R
1I0NyLm6Vh6F8mQh74wTjiKwvRCP9floCqhopkvxHBSfq77ZWG40xsEefu2jvuoX
Udk2n0xMbl1l/aNMLaZTi+8=
-----END PRIVATE KEY-----""",
                "client_email": "firebase-adminsdk-fbsvc@smartaid-6c5c0.iam.gserviceaccount.com",
                "client_id": "117085127067358398910",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40smartaid-6c5c0.iam.gserviceaccount.com"
            }
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase initialized successfully")
        
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
