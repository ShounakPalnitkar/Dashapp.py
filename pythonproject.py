import dash
from dash import dcc, html, Input, Output, dash_table, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import time
import logging
from typing import Tuple, Dict, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase
def initialize_firebase() -> bool:
    """Initialize Firebase connection with credentials."""
    try:
        firebase_credentials = {
            "type": "service_account",
            "project_id": "smartaid-6c5c0",
            "private_key_id": "4ca2f01452ce8893c8723ed1b746c9d0d2c86445",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDC9pRncbYZNLbj\n2+6W7UOxNvCsOD2g2lFZcrhyuPkYAsQTrMZP5heBGQB7Y3jqU10McPxJ1l/7Y1cm\nCVmjz1ea8yTjXk7dJr3IThlZt2uc5BzY82NyktwvpSqwbn9MpXRy3jE/AYfAj0gk\nIfW7bxb6T+14Ybi+LbcjjSlTOv93Pof6Znwo+z//XIVBIfdMVui0+4qg/DKm0o3S\nI260Q6s1jIy7bYRahSxfQRRqF0ru/NznJwRMmcKpkt9/8LzgK4E79VqUh1XJ2ruA\n4oUVYbO+4EYm66MBjDEL+e15pGGmn+XOxep7MsTDtz393HvEKAVsq+gOlHpD8zoQ\nXspzUlt7AgMBAAECggEAMOICc61fKxK8iIUsXUtAHb7YuVWgniQfIX5SIPGgAxUu\ndIBteLsISaYrKMTYHGiqe+QYXasShcVypGbTwu7J2F/+b8PFok2EaCSs1oHWyY+o\na/0agi+wZYHUIkiSQnV5rRNo5ZNMpktGm0iohEZmTHyd3gEigQyVTqSmJ+gzBYKH\n3f26nAhw2tIodtZ4dzeqgEeT1/k9fbBGg1kr5jbzpAbQWoPKcuJYK++XmRpy5Bwo\nzT7SPrVXKms1kikOSE8Z/vsOR2WggVg8KU/VrEWWdY8HMPVT9XnyNdp0XxTWiEZr\nvNXTqc67TAWy1SMqRaiJgM+OT3xcq0kzZGAsUp4rgQKBgQDwsq+qPgswHZT9OhNJ\nshVXejDm5t6bPj+4uKJAqJl8FrTskzM8wuWJghd5AWDJBuETQGYnKmblIjEkmN31\n+Y7+QV7DMIUBrOUxmtNNKI3+iFyKHMq3SK5eZc/anSw9yReCWUrDttJJe3tNID73\nZpOgIRTh1H1WksMsUn87LUqsdwKBgQDPW5GLeLmFPLdHE8lkWnDm2spTeBrDq6lz\nVFZRM8C2zSsQDvyh+SNT30j1wis6Y4MIkfH6Vi2KBviJ1mTHoJt6iJfhYrOvfIrj\n3GZ6inB0ukrzoH4SMMxBFCTt0hsTNZKLyjVZIBIhoHXKD2A0tgbS1AxxrVYD6m2k\n1j8E4qg+HQKBgQCRVwRVoxM0YZh2c9vzsxHJ+aGPu7aNPUBS9UIcEvJjCH8FHzlg\nJjteFezAh4F+waWk70z/t03cbBIKjDfy8FdU1fo3mJOn2FOo6VlQDP34xTRDvXD2\nzW9k1st0sVVmlYeZkPthRIKkFmj0wFTlJM5dcbxfROTOIt6xY7sp64ZcrwKBgELt\neke7Gp4/n6RoZYtniaNpoP5Z+MGJSbM42HdzLdOS20BepfodsOJkYmc4Wb2J2wRM\nHv8/C4nOgC/1LCgm1agyKFuOARM2LponTEhnIK78Zi7GcYqrh3HF77l3JFgJ5ZgL\nFzcCG/gQk5Q5bEL3MbKg0LdsTCQNaYBXypVoFwedAoGAcYjcBY+rCpvapxqmZ9JZ\nWhj1zxY3mARNzRM1C4n4Z2E33PRcHe6YjyEaZNU2xbW5A05F6/Dhcs6jiu0P5z8R\n1I0NyLm6Vh6F8mQh74wTjiKwvRCP9floCqhopkvxHBSfq77ZWG40xsEefu2jvuoX\nUdk2n0xMbl1l/aNMLaZTi+8=\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-fbsvc@smartaid-6c5c0.iam.gserviceaccount.com",
            "client_id": "117085127067358398910",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40smartaid-6c5c0.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://smartaid-6c5c0-default-rtdb.firebaseio.com/'
        })
        logger.info("Firebase initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        return False

# Initialize Firebase connection
firebase_initialized = initialize_firebase()

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

def create_empty_figure(message: str = "No data available") -> go.Figure:
    """Create an empty figure with a message."""
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{
            'text': message,
            'showarrow': False,
            'font': {'size': 16}
        }]
    )
    return fig

def fetch_firebase_data() -> pd.DataFrame:
    """Fetch and process data from Firebase Realtime Database."""
    if not firebase_initialized:
        logger.warning("Firebase not initialized")
        return pd.DataFrame()
    
    try:
        ref = db.reference('notifications')
        data = ref.get()
        
        if not data:
            logger.info("No data received from Firebase")
            return pd.DataFrame()
            
        records = []
        for timestamp, values in data.items():
            try:
                # Convert timestamp to datetime
                if isinstance(timestamp, str):
                    timestamp = float(timestamp)
                record = {'timestamp': datetime.fromtimestamp(timestamp)}
                
                # Validate and clean values
                cleaned_values = {}
                for key, value in values.items():
                    if isinstance(value, str):
                        value = value.strip()
                        if value.replace('.', '', 1).isdigit():
                            value = float(value)
                    cleaned_values[key] = value
                
                record.update(cleaned_values)
                records.append(record)
            except Exception as e:
                logger.warning(f"Error processing record {timestamp}: {e}")
                continue
                
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        logger.info(f"DataFrame created with {len(df)} records")
        
        # Ensure all expected columns are present
        expected_cols = [
            'timestamp', 'event_type', 'label', 'confidence',
            'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'
        ]
        
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
                
        # Convert numeric columns with better error handling
        numeric_cols = ['confidence', 'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Replace NaN with None for JSON serialization
                df[col] = df[col].where(pd.notnull(df[col]), None)
        
        # Filter to only keep recent data
        cutoff_time = datetime.now() - timedelta(hours=24)
        df = df[df['timestamp'] >= cutoff_time]
        
        return df.sort_values('timestamp', ascending=False)
        
    except Exception as e:
        logger.error(f"Error fetching Firebase data: {e}")
        return pd.DataFrame()

# =============================================
# Dashboard Layout
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    # Title and status indicator
    dbc.Row([
        dbc.Col(html.H1("Smart Hat Analytics Dashboard", 
                      className="text-center my-4"), width=10),
        dbc.Col(html.Div(id='firebase-status', className="text-right my-4"), width=2)
    ], justify="between"),
    
    # Refresh interval and data storage
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),
    dcc.Store(id='data-store'),
    dcc.Store(id='last-update', data=time.time()),
    
    # System Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("CPU Usage (%)", className="h5"),
            dbc.CardBody(dcc.Graph(id='cpu-graph', config={'displayModeBar': False}))
        ], className="shadow"), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Memory Usage (%)", className="h5"),
            dbc.CardBody(dcc.Graph(id='mem-graph', config={'displayModeBar': False}))
        ], className="shadow"), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Temperature (°C)", className="h5"),
            dbc.CardBody(dcc.Graph(id='temp-graph', config={'displayModeBar': False}))
        ], className="shadow"), md=4)
    ], className="mb-4"),
    
    # Detection Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Frequency", className="h5"),
            dbc.CardBody(dcc.Graph(id='detection-freq', config={'displayModeBar': False}))
        ], className="shadow"), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Confidence", className="h5"),
            dbc.CardBody(dcc.Graph(id='confidence-hist', config={'displayModeBar': False}))
        ], className="shadow"), md=6)
    ], className="mb-4"),
    
    # Distance and Performance Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Object Distance (cm)", className="h5"),
            dbc.CardBody(dcc.Graph(id='distance-graph', config={'displayModeBar': False}))
        ], className="shadow"), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Frames Per Second", className="h5"),
            dbc.CardBody(dcc.Graph(id='fps-graph', config={'displayModeBar': False}))
        ], className="shadow"), md=6)
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Event Log", className="h5"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.Small("Last updated: ", id='last-update-text'), width=6),
                    dbc.Col(dbc.Button("Refresh Now", id='refresh-button', color="primary", size="sm"), width=6, className="text-right")
                ]),
                dash_table.DataTable(
                    id='data-table',
                    columns=[{"name": i, "id": i} for i in [
                        'timestamp', 'event_type', 'label', 'confidence',
                        'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'
                    ]],
                    page_size=10,
                    style_table={'overflowX': 'auto', 'height': '300px', 'overflowY': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'backgroundColor': 'rgba(0,0,0,0)',
                        'color': 'white',
                        'border': '1px solid #444',
                        'maxWidth': '150px',
                        'whiteSpace': 'normal'
                    },
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgba(50, 50, 50, 0.1)'
                        }
                    ],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native"
                )
            ])
        ], className="shadow"), width=12)
    ])
])

# =============================================
# Callbacks
# =============================================

@app.callback(
    [Output('data-store', 'data'),
     Output('firebase-status', 'children'),
     Output('last-update', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')],
    prevent_initial_call=False
)
def update_data_store(n_intervals: int, n_clicks: int) -> Tuple[Dict, dbc.Alert, float]:
    """Fetch data from Firebase and update storage."""
    ctx = dash.callback_context
    
    # Only proceed if this is the initial call or a refresh button click
    if not ctx.triggered or ctx.triggered[0]['prop_id'] == 'interval-component.n_intervals' or ctx.triggered[0]['prop_id'] == 'refresh-button.n_clicks':
        try:
            df = fetch_firebase_data()
            if df.empty:
                logger.info("No data available in Firebase")
                return {}, dbc.Alert("Connected to Firebase but no data found", color="warning"), time.time()
            
            logger.info(f"Successfully fetched {len(df)} records")
            return df.to_dict('records'), dbc.Alert([
                html.I(className="bi bi-check-circle me-2"),
                "Connected to Firebase"
            ], color="success", className="d-flex align-items-center"), time.time()
            
        except Exception as e:
            logger.error(f"Error updating data store: {e}")
            return {}, dbc.Alert([
                html.I(className="bi bi-exclamation-triangle me-2"),
                f"Firebase error: {str(e)}"
            ], color="danger", className="d-flex align-items-center"), time.time()
    
    return no_update, no_update, no_update

@app.callback(
    Output('last-update-text', 'children'),
    [Input('last-update', 'data')]
)
def update_last_update_text(last_update: float) -> str:
    """Update the last updated timestamp text."""
    if last_update:
        return f"Last updated: {datetime.fromtimestamp(last_update).strftime('%Y-%m-%d %H:%M:%S')}"
    return "Last updated: Never"

@app.callback(
    [Output('cpu-graph', 'figure'),
     Output('mem-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('detection-freq', 'figure'),
     Output('confidence-hist', 'figure'),
     Output('distance-graph', 'figure'),
     Output('fps-graph', 'figure'),
     Output('data-table', 'data')],
    [Input('data-store', 'data')]
)
def update_dashboard(data: List[Dict]) -> Tuple[go.Figure, ...]:
    """Update all dashboard components with new data."""
    if not data:
        logger.info("No data available for dashboard update")
        empty_fig = create_empty_figure()
        return [empty_fig] * 7, []
    
    try:
        df = pd.DataFrame(data)
        
        # Convert timestamp if needed
        if len(df) > 0 and isinstance(df['timestamp'].iloc[0], str):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter data
        system_stats = df[df['event_type'] == 'system_stats'].copy()
        detections = df[df['event_type'] == 'detection'].copy()
        
        logger.info(f"Updating dashboard with {len(system_stats)} system stats and {len(detections)} detections")
        
        # Create figures with error handling
        def safe_create_figure(creator, *args, **kwargs):
            try:
                return creator(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error creating figure: {e}")
                return create_empty_figure("Error displaying data")
        
        # System metrics figures
        cpu_fig = safe_create_figure(
            px.line, system_stats, x='timestamp', y='CPU',
            title='', labels={'CPU': 'Usage %'},
            color_discrete_sequence=['#1f77b4']
        )
        
        mem_fig = safe_create_figure(
            px.line, system_stats, x='timestamp', y='MEM',
            title='', labels={'MEM': 'Usage %'},
            color_discrete_sequence=['#ff7f0e']
        )
        
        temp_fig = safe_create_figure(
            px.line, system_stats, x='timestamp', y='TEMP',
            title='', labels={'TEMP': '°C'},
            color_discrete_sequence=['#d62728']
        )
        if isinstance(temp_fig, go.Figure):
            temp_fig.add_hline(y=80, line_dash="dash", line_color="red")
        
        # Detection figures
        detection_freq = safe_create_figure(
            px.histogram, detections, x='timestamp', 
            title='', labels={'timestamp': 'Time'},
            color_discrete_sequence=['#2ca02c']
        )
        
        confidence_hist = safe_create_figure(
            px.histogram, detections, x='confidence',
            title='', labels={'confidence': 'Score'},
            color_discrete_sequence=['#9467bd'],
            nbins=20,
            range_x=[0, 1] if not detections.empty else None
        )
        
        distance_fig = safe_create_figure(
            px.scatter, detections, x='timestamp', y='estimated_distance_cm',
            color='confidence',
            title='', labels={'estimated_distance_cm': 'Distance (cm)'},
            color_continuous_scale='Viridis'
        )
        
        fps_fig = safe_create_figure(
            px.scatter, detections, x='timestamp', y='FPS',
            title='', labels={'FPS': 'Frames Per Second'},
            color_discrete_sequence=['#17becf']
        )
        
        # Apply consistent styling to all figures
        for fig in [cpu_fig, mem_fig, temp_fig, detection_freq, 
                   confidence_hist, distance_fig, fps_fig]:
            if isinstance(fig, go.Figure):
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    margin={'l': 40, 'r': 40, 't': 30, 'b': 30},
                    xaxis={'gridcolor': '#444'},
                    yaxis={'gridcolor': '#444'},
                    hovermode='x unified'
                )
        
        return (
            cpu_fig, mem_fig, temp_fig,
            detection_freq, confidence_hist,
            distance_fig, fps_fig,
            df.to_dict('records')
        )
    
    except Exception as e:
        logger.error(f"Error in dashboard update: {e}")
        empty_fig = create_empty_figure("Error displaying data")
        return [empty_fig] * 7, []

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
