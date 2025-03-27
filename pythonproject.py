import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import plotly.graph_objects as go

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# ==============================================
# Firebase Initialization
# ==============================================

# Initialize Firebase with your credentials
cred = credentials.Certificate({
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
})

# Initialize Firebase app (use None as name to avoid reinitialization errors)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def load_data():
    """Load data from Firebase Firestore"""
    try:
        # Query data from Firestore
        docs = db.collection('sensor_data').stream()
        
        # Convert to DataFrame
        data = []
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id
            data.append(doc_data)
        
        df = pd.DataFrame(data)
        
        # Convert timestamp if it exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ensure numeric columns are properly typed
        numeric_cols = ['CPU', 'MEM', 'TEMP', 'confidence', 'estimated_distance_cm', 'FPS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        print(f"Error loading data from Firebase: {e}")
        return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                   'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])

# ==============================================
# Dashboard Layout (same as before)
# ==============================================

app.layout = dbc.Container(fluid=True, children=[ 
    # Title
    dbc.Row([
        dbc.Col(html.H1("Smart Hat Analytics Dashboard", className="text-center my-4"))
    ]), 

    # Refresh interval
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),
    
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
    ]),

    # Event Type Distribution
    dbc.Row([ 
        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Event Type Distribution", className="h5"), 
            dbc.CardBody(dcc.Graph(id='event-type-graph')) 
        ], className="shadow"), md=6),

        # Latest Events Table
        dbc.Col(dbc.Card([ 
            dbc.CardHeader("Latest Events", className="h5"), 
            dbc.CardBody(dash_table.DataTable(id='latest-events', style_table={'height': '300px', 'overflowY': 'auto'}))
        ], className="shadow"), md=6)
    ])
])

# ==============================================
# Callback to update graphs and table
# ==============================================

@app.callback(
    [Output('cpu-graph', 'figure'),
     Output('mem-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('event-type-graph', 'figure'),
     Output('latest-events', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_intervals):
    df = load_data()  # Load data from Firebase Firestore
    
    # Generate CPU, Memory, and Temperature graphs
    cpu_graph = px.line(df, x='timestamp', y='CPU', title="CPU Usage (%)")
    mem_graph = px.line(df, x='timestamp', y='MEM', title="Memory Usage (%)")
    temp_graph = px.line(df, x='timestamp', y='TEMP', title="Temperature (°C)")
    
    # Event Type Distribution (bar graph)
    event_type_counts = df['event_type'].value_counts()
    event_type_graph = px.bar(event_type_counts, x=event_type_counts.index, y=event_type_counts.values, title="Event Type Distribution")
    
    # Display latest events in table
    latest_events = df[['timestamp', 'event_type', 'label', 'confidence']].tail(10).to_dict('records')
    
    return cpu_graph, mem_graph, temp_graph, event_type_graph, latest_events

# ==============================================
# Run the server
# ==============================================
if __name__ == '__main__':
    app.run_server(debug=True)
