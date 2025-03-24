import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

API_URL = "http://127.0.0.1:5000/data"

def fetch_data():
    """Fetches data from the API and returns DataFrame."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        
        if not data or "device_data" not in data:
            return pd.DataFrame({"Device": [], "Power Usage": []})
        
        device_df = pd.DataFrame(data["device_data"])
        if "device" not in device_df or "power_usage" not in device_df:
            return pd.DataFrame({"Device": [], "Power Usage": []})
        
        return device_df.rename(columns={"device": "Device", "power_usage": "Power Usage"})
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame({"Device": [], "Power Usage": []})

app.layout = dbc.Container([
    html.H1("Device Power Usage Dashboard", className="text-center"),
    dcc.Interval(id="interval", interval=5000, n_intervals=0),
    dbc.Row([
        dbc.Col(dcc.Graph(id="device_graph"), width=12)
    ])
], fluid=True)

@app.callback(
    Output("device_graph", "figure"),
    Input("interval", "n_intervals")
)
def update_data(n):
    device_df = fetch_data()
    
    if device_df.empty:
        fig = px.bar(title="No Data Available", labels={"x": "Device", "y": "Power Usage"})
        return fig
    
    fig = px.bar(device_df, x="Device", y="Power Usage", title="Device Power Usage")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
