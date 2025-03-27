import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import plotly.express as px
import random

# Initialize Firebase
cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Replace with actual path
firebase_admin.initialize_app(cred)
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
        fig = px.histogram(df, x='label', title='Event Frequency', color='label', template='plotly_dark')
    else:
        fig = px.histogram(title='No Data Available', template='plotly_dark')

    # Return updated data and statistics
    return df.to_dict("records"), cpu_text, mem_text, temp_text, fig

if __name__ == '__main__':
    app.run_server(debug=True)