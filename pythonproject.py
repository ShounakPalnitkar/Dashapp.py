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
# Firebase Configuration
# =============================================

# Load Firebase credentials from environment variables
firebase_config = {
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL")
}

# Initialize Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Firebase initialization error: {e}")
    db = None

# =============================================
# Data Loading from Firebase
# =============================================

def load_data_from_firebase():
    """Fetch data from Firebase Firestore"""
    try:
        if not db:
            return pd.DataFrame()
            
        # Get all documents from the collection
        docs = db.collection('detection_data').stream()
        
        # Convert to list of dictionaries
        data = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id  # Include document ID if needed
            data.append(doc_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert timestamp if it exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        return df
    
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                   'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])

# =============================================
# Dashboard Layout (same as before)
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    # ... (same layout code as in previous example)
])

# =============================================
# Callbacks (modified for Firebase)
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
    # Load data from Firebase instead of CSV
    df = load_data_from_firebase()
    
    if df.empty:
        return [px.scatter(title="No Data Available")] * 7 + [[]]
    
    # Filter data for different visualizations
    system_stats = df[df['event_type'] == 'system_stats']
    detections = df[df['event_type'] == 'detection']
    
    # Create figures (same as before)
    cpu_fig = px.line(
        system_stats, x='timestamp', y='CPU',
        title='CPU Usage Over Time',
        labels={'CPU': 'CPU Usage (%)', 'timestamp': 'Time'},
        template='plotly_dark'
    )
    
    # ... (other figures same as before)
    
    return (
        cpu_fig, mem_fig, temp_fig,
        detection_freq, confidence_hist,
        distance_fig, fps_fig,
        df.to_dict('records')
    )

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)