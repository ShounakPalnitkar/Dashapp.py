import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import os  # Import os to access the environment variables

# Initialize the Dash app
app = dash.Dash(__name__)

# Backend API URL (replace with your actual API endpoint)
API_URL = "http://your-backend-api.com/data"

# Function to fetch data from the backend
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        print("Fetched data:", data)  # Debugging statement

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
    html.H1("Smart Visual Hat Monitoring Dashboard", style={'textAlign': 'center', 'color': 'white'}),

    # Interval component to refresh data every 3 minutes
    dcc.Interval(id='interval-component', interval=180000, n_intervals=0),

    # First row: Device Distribution and Overall Dashboard Performance
    html.Div([
        # Device Distribution (Smaller Visualization)
        html.Div([html.Div(dcc.Graph(id='device-distribution'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Overall Dashboard Performance (KPI Cards)
        html.Div([html.H3("Overall Dashboard Performance", style={'textAlign': 'center', 'color': 'white'}), html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'})], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Second row: Power Management (Horizontal Bar Chart on the left, Table on the right)
    html.Div([html.Div([html.Div(dcc.Graph(id='power-management'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'}), html.Div([dash_table.DataTable(id='power-management-table', columns=[{'name': 'Device', 'id': 'Device'}, {'name': 'Power Usage', 'id': 'Power Usage'}], data=[], style_table={'height': '300px', 'overflowY': 'auto', 'width': '400px', 'backgroundColor': 'black', 'color': 'white'}, style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': 'black', 'color': 'white'}, style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'})], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Third row: System Performance and Raspberry Pi (Side by Side)
    html.Div([html.Div([html.Div(dcc.Graph(id='system-performance'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'}), html.Div([html.Div(dcc.Graph(id='raspberry-pi'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'})], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Fourth row: Temperature Level and Object Detection Time (Side by Side)
    html.Div([html.Div([html.Div(dcc.Graph(id='temperature-level'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'}), html.Div([html.Div(dcc.Graph(id='object-detection-time'), style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'})], style={'width': '48%', 'display': 'inline-block'})], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Buttons and Download Option
    html.Div([html.Button('Temperature Stats', id='temp-stats-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}), html.Button('Network Stability', id='network-stability-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}), html.Button('Device Config', id='device-config-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}), html.Button('Overall Performance', id='overall-performance-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'})], style={'textAlign': 'center', 'marginTop': '20px'}),

    html.Div([html.Button('Download Report', id='download-report-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'})], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Div to display button-specific data
    html.Div(id='button-response', style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '20px', 'color': 'white'}),

    # Download component for file downloads
    dcc.Download(id='download-report')
])

# Callback to update data every 3 minutes
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
            [],  # Placeholder for power-management-table
            px.pie(title="System Performance"),  # Placeholder for system-performance
            px.pie(title="Raspberrypi"),  # Placeholder for raspberry-pi
            go.Figure(),  # Placeholder for temperature-level
            px.line(title="Object Detection Time"),  # Placeholder for object-detection-time
            []  # Placeholder for kpi-cards
        )

    # Device Distribution
    device_fig = px.bar(device_df, x='Device', y='Power Usage', title='Device Distribution', color='Device', color_discrete_sequence=px.colors.qualitative.Plotly)
    device_fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='black', paper_bgcolor='black', font={'color': 'white'})
    
    # Power Management (Horizontal Bar Chart)
    power_fig = px.bar(device_df, y='Device', x='Power Usage', title='Power Management', color='Device', orientation='h', color_discrete_sequence=px.colors.qualitative.Plotly)
    power_fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='black', paper_bgcolor='black', font={'color': 'white'})

    # Power Management Table
    power_table = device_df[['Device', 'Power Usage']].to_dict('records')

    # System Performance (Pie Chart)
    system_fig = px.pie(system_df, names='Category', values='Value', title='System Performance', color_discrete_sequence=px.colors.qualitative.Plotly)
    system_fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='black', paper_bgcolor='black', font={'color': 'white'})

    # Raspberry Pi Performance (Pie Chart)
    pi_fig = px.pie(pi_df, names='Category', values='Value', title='Raspberry Pi Performance', color_discrete_sequence=px.colors.qualitative.Plotly)
    pi_fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='black', paper_bgcolor='black', font={'color': 'white'})

    # Temperature Level (Line Graph)
    temp_fig = go.Figure(data=go.Scatter(x=time_df['Time'], y=time_df['Temperature Level'], mode='lines', name='Temperature'))
    temp_fig.update_layout(title='Temperature Level', plot_bgcolor='black', paper_bgcolor='black', font={'color': 'white'})

    # Object Detection Time (Line Graph)
    detection_fig = px.line(time_df, x='Time', y='Detection Time', title='Object Detection Time', line_shape='linear')
    detection_fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor='black', paper_bgcolor='black', font={'color': 'white'})

    # KPI Cards (Placeholder)
    kpi_cards = [
        html.Div([html.H4("Total Devices"), html.P(f"{len(device_df)}")], style={'textAlign': 'center', 'flex': 1, 'backgroundColor': '#2c3e50', 'borderRadius': '5px', 'padding': '20px', 'color': 'white'}),
        html.Div([html.H4("Total Power Usage"), html.P(f"{device_df['Power Usage'].sum():.2f}")], style={'textAlign': 'center', 'flex': 1, 'backgroundColor': '#2c3e50', 'borderRadius': '5px', 'padding': '20px', 'color': 'white'})
    ]

    return device_fig, power_fig, power_table, system_fig, pi_fig, temp_fig, detection_fig, kpi_cards

# Run the server with dynamic port binding
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8050))) 