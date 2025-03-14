import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json

# Initialize the Dash app
app = dash.Dash(__name__)

# Backend API URL (replace with your actual API endpoint)
API_URL = "http://your-backend-api.com/data"  # Make sure this is a valid API

# Function to fetch data from the backend
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()  # Assume this returns a JSON response

        # Parse the data into DataFrames
        device_data = data.get("device_data", [])
        system_data = data.get("system_data", [])
        pi_data = data.get("pi_data", [])
        time_data = data.get("time_data", [])

        return (
            pd.DataFrame(device_data),
            pd.DataFrame(system_data),
            pd.DataFrame(pi_data),
            pd.DataFrame(time_data),
        )
    except Exception as e:
        print(f"Error fetching data: {e}")
        # Return empty DataFrames if there's an error
        return (
            pd.DataFrame({"Device": [], "Power Usage": []}),
            pd.DataFrame({"Category": [], "Value": []}),
            pd.DataFrame({"Category": [], "Value": []}),
            pd.DataFrame({"Time": [], "Detection Time": []}),
        )

# Layout for the dashboard
app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    # Header Section
    html.H1("Live Stream Smart Visual Hat Monitoring Dashboard", style={'textAlign': 'center', 'color': 'white'}),

    # Interval component to refresh data every 5 seconds for live updates
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),  # 5 seconds interval

    # First row: Device Distribution and Overall Dashboard Performance
    html.Div([
        html.Div([html.Div(dcc.Graph(id='device-distribution'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([html.H3("Overall Dashboard Performance", style={'textAlign': 'center', 'color': 'white'}), html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'})], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Second row: Power Management (Horizontal Bar Chart on the left, Table on the right)
    html.Div([
        html.Div([html.Div(dcc.Graph(id='power-management'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([dash_table.DataTable(id='power-management-table', columns=[{'name': 'Device', 'id': 'Device'}, {'name': 'Power Usage', 'id': 'Power Usage'}], data=[], style_table={'height': '300px', 'overflowY': 'auto', 'width': '400px', 'backgroundColor': 'black', 'color': 'white'}, style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': 'black', 'color': 'white'}, style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'})], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Third row: System Performance and Raspberry Pi (Side by Side)
    html.Div([
        html.Div([html.Div(dcc.Graph(id='system-performance'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'}), 
        html.Div([html.Div(dcc.Graph(id='raspberry-pi'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Fourth row: Temperature Level and Object Detection Time (Side by Side)
    html.Div([
        html.Div([html.Div(dcc.Graph(id='temperature-level'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'}), 
        html.Div([html.Div(dcc.Graph(id='object-detection-time'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Buttons and Download Option
    html.Div([html.Button('Temperature Stats', id='temp-stats-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}), 
              html.Button('Network Stability', id='network-stability-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}), 
              html.Button('Device Config', id='device-config-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}), 
              html.Button('Overall Performance', id='overall-performance-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'})], style={'textAlign': 'center', 'marginTop': '20px'}),

    html.Div([html.Button('Download Report', id='download-report-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'})], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Div to display button-specific data
    html.Div(id='button-response', style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '20px', 'color': 'white'}),

    # Download component for file downloads
    dcc.Download(id='download-report')
])

# Callback to update data every 5 seconds for live stream
@app.callback(
    [Output('device-distribution', 'figure'),
     Output('power-management', 'figure'),
     Output('power-management-table', 'data'),
     Output('system-performance', 'figure'),
     Output('raspberry-pi', 'figure'),
     Output('temperature-level', 'figure'),
     Output('object-detection-time', 'figure'),
     Output('kpi-cards', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n_intervals):
    device_df, system_df, pi_df, time_df = fetch_data()

    # Handle empty DataFrames
    if device_df.empty or system_df.empty or pi_df.empty or time_df.empty:
        print("Warning: One or more DataFrames are empty. Using placeholder data.")
        return (
            px.bar(title="Device Distribution"),  # Placeholder for device-distribution
            px.bar(title="Power Management"),  # Placeholder for power-management
            [],
            px.bar(title="System Performance"),  # Placeholder for system-performance
            px.bar(title="Raspberry Pi"),  # Placeholder for raspberry-pi
            px.line(title="Temperature Levels"),  # Placeholder for temperature-level
            px.line(title="Object Detection Time"),  # Placeholder for object-detection-time
            []  # Placeholder for KPI cards
        )

    # Proceed to update figures with real data
    # Example: Device Distribution chart
    device_dist_figure = px.bar(device_df, x="Device", y="Power Usage", title="Device Distribution")

    # Power Management chart (Horizontal Bar)
    power_management_figure = px.bar(system_df, x="Value", y="Category", orientation='h', title="Power Management")

    # Power Management table
    power_table_data = device_df.to_dict('records')

    # System Performance chart
    system_performance_figure = px.line(system_df, x="Category", y="Value", title="System Performance")

    # Raspberry Pi performance chart
    pi_performance_figure = px.line(pi_df, x="Category", y="Value", title="Raspberry Pi")

    # Temperature Levels chart
    temp_levels_figure = px.line(time_df, x="Time", y="Detection Time", title="Temperature Levels")

    # Object Detection Time chart
    object_detection_time_figure = px.line(time_df, x="Time", y="Detection Time", title="Object Detection Time")

    # KPI Cards (just an example)
    kpi_cards = [
        html.Div([html.H3("CPU Load", style={'textAlign': 'center'}), html.P(system_df['Value'].mean(), style={'fontSize': '30px', 'textAlign': 'center'})]),
        html.Div([html.H3("RAM Usage", style={'textAlign': 'center'}), html.P(system_df['Value'].mean(), style={'fontSize': '30px', 'textAlign': 'center'})])
    ]

    return (
        device_dist_figure,
        power_management_figure,
        power_table_data,
        system_performance_figure,
        pi_performance_figure,
        temp_levels_figure,
        object_detection_time_figure,
        kpi_cards
    )

# Running the server with explicit port configuration
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050) 
    
        
    
       
