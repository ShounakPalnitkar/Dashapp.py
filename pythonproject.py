import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import time

# Initialize Firebase
def initialize_firebase():
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
        print("Firebase initialized successfully")
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
    if not firebase_initialized:
        return pd.DataFrame()
    
    try:
        ref = db.reference('smart_hat_data')  # Adjust this path to your Firebase structure
        data = ref.get()
        
        if not data:
            return pd.DataFrame()
            
        # Convert the data to a DataFrame
        records = []
        for timestamp, values in data.items():
            record = {'timestamp': datetime.fromtimestamp(float(timestamp))}
            record.update(values)
            records.append(record)
            
        df = pd.DataFrame(records)
        
        # Ensure all expected columns are present
        expected_cols = ['timestamp', 'event_type', 'label', 'confidence',
                        'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
                
        # Convert numeric columns
        numeric_cols = ['confidence', 'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Filter to only keep data from the last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        df = df[df['timestamp'] >= cutoff_time]
        
        return df.sort_values('timestamp', ascending=False)
        
    except Exception as e:
        print(f"Error fetching Firebase data: {e}")
        return pd.DataFrame()

# =============================================
# Dashboard Layout
# =============================================

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Smart Hat Data", className="text-center"))
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(id='data-table'), width=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='cpu-graph'), width=6),
        dbc.Col(dcc.Graph(id='mem-graph'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='temp-graph'), width=6),
        dbc.Col(dcc.Graph(id='detection-freq'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='confidence-hist'), width=6),
        dbc.Col(dcc.Graph(id='distance-graph'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='fps-graph'), width=12)
    ]),
    dcc.Store(id='data-store', data={})
], fluid=True)

# =============================================
# Callback Functions
# =============================================

@app.callback(
    [Output('data-store', 'data'),
     Output('firebase-status', 'children'),
     Output('cpu-graph', 'figure'),
     Output('mem-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('detection-freq', 'figure'),
     Output('confidence-hist', 'figure'),
     Output('distance-graph', 'figure'),
     Output('fps-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_data_store(n):
    """Fetch the latest data from Firebase and update graphs."""
    try:
        df = fetch_firebase_data()
        if df.empty:
            return {}, dbc.Alert("Connected to Firebase but no data found", color="warning"), {}, {}, {}, {}, {}, {}, {}

        cpu_fig = create_figure(df, 'CPU')
        mem_fig = create_figure(df, 'MEM')
        temp_fig = create_figure(df, 'TEMP')
        detection_freq_fig = create_detection_freq_figure(df)
        confidence_hist_fig = create_confidence_hist_figure(df)
        distance_fig = create_figure(df, 'estimated_distance_cm')
        fps_fig = create_figure(df, 'FPS')

        return df.to_dict('records'), dbc.Alert("Connected to Firebase", color="success"), cpu_fig, mem_fig, temp_fig, detection_freq_fig, confidence_hist_fig, distance_fig, fps_fig

    except Exception as e:
        print(f"Error updating data: {e}")
        return {}, dbc.Alert("Error fetching data", color="danger"), {}, {}, {}, {}, {}, {}, {}

def create_figure(df, column_name):
    """Create a line graph for the specified column."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[column_name], mode='lines', name=column_name))
    fig.update_layout(title=f'{column_name} Over Time',
                      xaxis_title='Time',
                      yaxis_title=column_name)
    return fig

def create_detection_freq_figure(df):
    """Create a bar chart for event types."""
    fig = px.bar(df, x='event_type', title="Detection Frequency")
    fig.update_layout(xaxis_title="Event Type", yaxis_title="Frequency")
    return fig

def create_confidence_hist_figure(df):
    """Create a histogram for confidence."""
    fig = px.histogram(df, x="confidence", title="Confidence Distribution")
    fig.update_layout(xaxis_title="Confidence", yaxis_title="Frequency")
    return fig

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
