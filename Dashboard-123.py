import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import random

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Simulate real-time data for devices
def get_real_time_data():
    """Simulates real-time power usage data."""
    devices = ["Device A", "Device B", "Device C", "Device D"]
    power_usage = [random.randint(100, 250) for _ in devices]  # Random power usage between 100 and 250
    return pd.DataFrame({"Device": devices, "Power Usage": power_usage})

# Layout of the dashboard
app.layout = dbc.Container([
    html.H1("Real-Time Device Power Usage Dashboard", className="text-center"),
    
    # Interval to refresh data every 5 seconds
    dcc.Interval(id="interval", interval=5000, n_intervals=0),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="device_graph"), width=12),
    ], justify="center"),

    # Footer Section
    dbc.Row([
        dbc.Col(html.Div("Powered by Dash and Bootstrap", className="text-center"), width=12)
    ], style={"padding-top": "20px"})
], fluid=True)

@app.callback(
    Output("device_graph", "figure"),
    Input("interval", "n_intervals")
)
def update_data(n):
    """Callback function to update data every interval."""
    device_df = get_real_time_data()  # Fetch real-time data
    
    # Create a bar chart to display the real-time power usage
    fig = px.bar(device_df, x="Device", y="Power Usage", title="Device Power Usage",
                 labels={"Device": "Device", "Power Usage": "Power Usage (Watts)"})
    fig.update_layout(
        template="plotly_dark",  # For a dark-themed graph
        xaxis_title="Device",
        yaxis_title="Power Usage (Watts)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)