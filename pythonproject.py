import dash
from dash import dcc, html, Input, Output, dash_table, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
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
        logger.info(f"DataFrame created with {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error fetching data from Firebase: {e}")
        return pd.DataFrame()

# Define the layout of the app
app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("Firebase Data Visualization"), width={"size": 6, "offset": 3}),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='cpu-usage-graph', figure=create_empty_figure()), width=6),
        dbc.Col(dcc.Graph(id='memory-usage-graph', figure=create_empty_figure()), width=6),
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(id='data-table', style_table={'height': '450px', 'overflowY': 'auto'},), width=12)
    ]),
])

# Define the callback to update graphs and table
@app.callback(
    [Output('cpu-usage-graph', 'figure'),
     Output('memory-usage-graph', 'figure'),
     Output('data-table', 'data')],
    Input('interval-component', 'n_intervals')
)
def update_graphs_and_table(n_intervals: int) -> Tuple[go.Figure, go.Figure, List[Dict[str, Union[str, float]]]]:
    """Fetch data from Firebase and update graphs and table."""
    df = fetch_firebase_data()
    
    if df.empty:
        return create_empty_figure("No data available"), create_empty_figure("No data available"), []
    
    # Create the CPU Usage and Memory Usage plots
    cpu_fig = px.line(df, x='timestamp', y='cpu_usage', title='CPU Usage Over Time')
    memory_fig = px.line(df, x='timestamp', y='memory_usage', title='Memory Usage Over Time')
    
    # Update plot formatting
    cpu_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
    memory_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})

    # Convert data to format for the table
    data_table = df.to_dict('records')
    
    return cpu_fig, memory_fig, data_table

if __name__ == '__main__':
    app.run_server(debug=True)
