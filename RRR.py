import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import random

# Your Firebase service account credentials as a dictionary
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

# Initialize Firebase with the credentials from the dictionary
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)

# Now your Firebase is initialized and you can proceed with the rest of your code...
db = firestore.client()

def load_data():
    """Load event data from Firestore and handle connection errors."""
    try:
        docs = db.collection("events").stream()
        data = []
        for doc in docs:
            doc_dict = doc.to_dict()
            data.append(doc_dict)

        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Check if timestamp exists and convert to datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        
        # Handle any potential conversion issues
        df = df.dropna(subset=["timestamp"])

        return df
    
    except Exception as e:
        print(f"Error loading data from Firestore: {e}")
        return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence', 'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])

def save_data_to_firebase(data):
    """Save new detection data to Firebase."""
    try:
        db.collection("events").add(data)
    except Exception as e:
        print(f"Error saving to Firestore: {e}")

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])
app.title = "Real-Time Detection Dashboard"

# Define layout
app.layout = html.Div(style={"backgroundColor": "#1e1e1e", "color": "white", "padding": "20px"}, children=[
    html.H1("Real-Time Detection Dashboard", style={"textAlign": "center", "color": "white"}),

    # Interval to update every 5 seconds
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),

    html.Div([
        html.Div([
            html.H3("System Stats", style={"color": "#ffcc00"}),
            html.P(id='cpu-stat', children="CPU: N/A"),
            html.P(id='mem-stat', children="Memory: N/A"),
            html.P(id='temp-stat', children="Temperature: N/A")
        ], style={"backgroundColor": "#333", "padding": "15px", "borderRadius": "10px", "margin": "10px"}),

        html.Div([
            html.H3("Latest Detections", style={"color": "#00ccff"}),
            dash_table.DataTable(id='data-table', style_table={'overflowX': 'auto'},
                                 style_header={'backgroundColor': 'black', 'color': 'white'})
        ], style={"backgroundColor": "#444", "padding": "15px", "borderRadius": "10px", "margin": "10px"})
    ], style={"display": "flex", "justifyContent": "space-around"}),

    # Event histogram graph
    dcc.Graph(id='event-histogram', style={"backgroundColor": "#1e1e1e"}),
])

@app.callback(
    [Output('data-table', 'data'),
     Output('cpu-stat', 'children'),
     Output('mem-stat', 'children'),
     Output('temp-stat', 'children'),
     Output('event-histogram', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    # Load the data
    df = load_data()

    # Generate sample system stats (for demonstration)
    cpu_usage = random.uniform(10, 90)
    mem_usage = random.uniform(30, 80)
    temp = random.uniform(40, 80)
    
    # Format the system stats
    cpu_text = f"CPU: {cpu_usage:.2f}%"
    mem_text = f"Memory: {mem_usage:.2f}%"
    temp_text = f"Temperature: {temp:.2f}°C"
    
    # Create histogram figure based on data
    if not df.empty:
        fig = px.histogram(df, x='label', title="Event Type Distribution")
    else:
        fig = px.histogram(title="Event Type Distribution")
    
    # Return updated data and stats
    return df.to_dict('records'), cpu_text, mem_text, temp_text, fig

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)