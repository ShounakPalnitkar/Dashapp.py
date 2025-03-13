import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import random

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

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Smart Visual Hat Monitoring Dashboard", style={'textAlign': 'center', 'color': 'white'}),

    # Interval component to refresh data every 3 minutes (180,000 milliseconds)
    dcc.Interval(id='interval-component', interval=180000, n_intervals=0),

    # First row: Device Distribution and Overall Dashboard Performance
    html.Div([
        # Device Distribution (Smaller Visualization)
        html.Div([
            html.Div(
                dcc.Graph(id='device-distribution'),
                style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Overall Dashboard Performance (KPI Cards)
        html.Div([
            html.H3("Overall Dashboard Performance", style={'textAlign': 'center', 'color': 'white'}),
            html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Second row: Power Management (Horizontal Bar Chart on the left, Table on the right)
    html.Div([
        # Horizontal Bar Chart for Power Management
        html.Div([
            html.Div(
                dcc.Graph(id='power-management'),
                style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'}
            )
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Table for Power Management
        html.Div([
            dash_table.DataTable(
                id='power-management-table',
                columns=[{'name': 'Device', 'id': 'Device'}, {'name': 'Power Usage', 'id': 'Power Usage'}],
                data=[],
                style_table={'height': '300px', 'overflowY': 'auto', 'width': '400px', 'backgroundColor': 'black', 'color': 'white'},
                style_cell={'textAlign': 'left', 'padding': '10px', 'backgroundColor': 'black', 'color': 'white'},
                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Third row: System Performance and Raspberry Pi (Side by Side)
    html.Div([
        html.Div([
            html.Div(
                dcc.Graph(id='system-performance'),
                style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'}
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Div(
                dcc.Graph(id='raspberry-pi'),
                style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'}
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Fourth row: Temperature Level and Object Detection Time (Side by Side)
    html.Div([
        html.Div([
            html.Div(
                dcc.Graph(id='temperature-level'),
                style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'}
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Div(
                dcc.Graph(id='object-detection-time'),
                style={'border': '2px solid #cccccc', 'padding': '10px', 'borderRadius': '5px'}
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Buttons and Download Option
    html.Div([
        html.Button('Temperature Stats', id='temp-stats-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}),
        html.Button('Network Stability', id='network-stability-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}),
        html.Button('Device Config', id='device-config-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'}),
        html.Button('Overall Performance', id='overall-performance-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'})
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    html.Div([
        html.Button('Download Report', id='download-report-btn', style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#2c3e50', 'color': 'white'})
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Div to display button-specific data
    html.Div(id='button-response', style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '20px', 'color': 'white'}),

    # Download component for file downloads
    dcc.Download(id='download-report')
], style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'})

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
            px.bar(title="No Data Available"),  # Placeholder for device-distribution
            px.bar(title="No Data Available"),  # Placeholder for power-management
            [],  # Placeholder for power-management-table
            px.pie(title="No Data Available"),  # Placeholder for system-performance
            px.pie(title="No Data Available"),  # Placeholder for raspberry-pi
            go.Figure(),  # Placeholder for temperature-level
            px.line(title="No Data Available"),  # Placeholder for object-detection-time
            []  # Placeholder for kpi-cards
        )

    # Device Distribution (Smaller Visualization)
    device_fig = px.bar(device_df, x='Device', y='Power Usage', title='Device Distribution', 
                        color='Device', color_discrete_sequence=px.colors.qualitative.Plotly)
    device_fig.update_layout(
        height=300, 
        margin=dict(l=20, r=20, t=40, b=20), 
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font={'color': 'white'}
    )
    
    # Power Management (Horizontal Bar Chart)
    power_fig = px.bar(device_df, y='Device', x='Power Usage', title='Power Management', 
                       color='Device', color_discrete_sequence=px.colors.qualitative.Plotly, 
                       orientation='h')
    power_fig.update_layout(
        yaxis_title="Device", 
        xaxis_title="Power Usage", 
        height=400, 
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font={'color': 'white'}
    )

    # System Performance
    system_fig = px.pie(system_df, values='Value', names='Category', title='System Performance', 
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    system_fig.update_layout(
        height=400, 
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font={'color': 'white'}
    )

    # Raspberry Pi Performance
    pi_fig = px.pie(pi_df, values='Value', names='Category', title='Raspberry Pi Performance', 
                    hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
    pi_fig.update_layout(
        height=400, 
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font={'color': 'white'}
    )

    # Temperature Level (Gauge Chart with Colored Indicator)
    temp_value = pi_df.loc[pi_df['Category'] == 'Temperature', 'Value'].values[0] if not pi_df.empty else 0

    # Determine the color of the indicator based on the temperature value
    if temp_value <= 30:
        indicator_color = "blue"
    elif temp_value <= 70:
        indicator_color = "yellow"
    else:
        indicator_color = "red"

    temp_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temp_value,
        title={'text': "Temperature Level", 'font': {'size': 20, 'color': 'white'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#cccccc', 'tickvals': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]},
            'bar': {'color': indicator_color},  # Set the indicator color dynamically
            'steps': [
                {'range': [0, 30], 'color': "blue", 'name': 'Good (0-30)'},
                {'range': [30, 70], 'color': "yellow", 'name': 'Moderate (30-70)'},
                {'range': [70, 100], 'color': "red", 'name': 'High (70-100)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},  # Set the indicator needle color to white
                'thickness': 0.75,
                'value': temp_value
            }
        }
    ))

    # Add custom labels for the gauge
    temp_fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=80, b=20),
        plot_bgcolor='black',
        paper_bgcolor='black',
        font={'color': 'white'},
        annotations=[
            # Good
            dict(
                x=0.15, y=0.2,
                xref="paper", yref="paper",
                text="Good (0-30)",
                showarrow=False,
                font=dict(size=14, color="blue")
            ),
            # Moderate
            dict(
                x=0.5, y=0.4,
                xref="paper", yref="paper",
                text="Moderate (30-70)",
                showarrow=False,
                font=dict(size=14, color="yellow")
            ),
            # High
            dict(
                x=0.85, y=0.2,
                xref="paper", yref="paper",
                text="High (70-100)",
                showarrow=False,
                font=dict(size=14, color="red")
            )
        ]
    )

    # Object Detection Time
    time_fig = px.line(time_df, x='Time', y='Detection Time', title='Object Detection Time', 
                       line_shape='linear', markers=True)
    time_fig.update_layout(
        height=400, 
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font={'color': 'white'}
    )

    # Overall Dashboard Performance (KPI Cards)
    kpi_cards = [
        html.Div([
            html.H4("Response Time", style={'color': 'white'}),
            html.H3(f"{random.randint(10, 100)} ms", style={'color': 'white'})
        ], style={'textAlign': 'center', 'border': '1px solid #cccccc', 'padding': '10px', 'borderRadius': '5px', 'width': '45%', 'marginBottom': '10px'}),
        html.Div([
            html.H4("Cache Utilization", style={'color': 'white'}),
            html.H3(f"{random.randint(0, 100)}%", style={'color': 'white'})
        ], style={'textAlign': 'center', 'border': '1px solid #cccccc', 'padding': '10px', 'borderRadius': '5px', 'width': '45%', 'marginBottom': '10px'}),
        html.Div([
            html.H4("Dashboard Load Time", style={'color': 'white'}),
            html.H3(f"{random.randint(100, 500)} ms", style={'color': 'white'})
        ], style={'textAlign': 'center', 'border': '1px solid #cccccc', 'padding': '10px', 'borderRadius': '5px', 'width': '45%', 'marginBottom': '10px'}),
        html.Div([
            html.H4("Data Accuracy", style={'color': 'white'}),
            html.H3(f"{random.randint(90, 100)}%", style={'color': 'white'})
        ], style={'textAlign': 'center', 'border': '1px solid #cccccc', 'padding': '10px', 'borderRadius': '5px', 'width': '45%', 'marginBottom': '10px'})
    ]
    
    return device_fig, power_fig, device_df.to_dict('records'), system_fig, pi_fig, temp_fig, time_fig, kpi_cards

# Callback to handle button clicks and update visualizations
@app.callback(
    Output('button-response', 'children'),
    [Input('temp-stats-btn', 'n_clicks'),
     Input('network-stability-btn', 'n_clicks'),
     Input('device-config-btn', 'n_clicks'),
     Input('overall-performance-btn', 'n_clicks')]
)
def handle_button_clicks(temp_clicks, network_clicks, device_clicks, overall_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "No button clicked yet"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'temp-stats-btn':
            return f"Temperature Stats: {random.randint(0, 100)}%"
        elif button_id == 'network-stability-btn':
            return f"Network Stability: {random.randint(0, 100)}%"
        elif button_id == 'device-config-btn':
            return f"Device Config: {random.randint(0, 100)}%"
        elif button_id == 'overall-performance-btn':
            return f"Overall Performance: {random.randint(0, 100)}%"

# Callback to generate and download the full report
@app.callback(
    Output('download-report', 'data'),
    [Input('download-report-btn', 'n_clicks')],
    prevent_initial_call=True
)
def generate_report(n_clicks):
    if n_clicks is None:
        return dash.no_update
    else:
        # Fetch the latest data
        device_df, system_df, pi_df, time_df = fetch_data()

        # Combine all data into a single dictionary
        report_data = {
            'Device Distribution': device_df.to_dict('records'),
            'Power Management': device_df.to_dict('records'),
            'System Performance': system_df.to_dict('records'),
            'Raspberry Pi Performance': pi_df.to_dict('records'),
            'Object Detection Time': time_df.to_dict('records')
        }

        # Convert the dictionary to a CSV string
        report_csv = ""
        for section, data in report_data.items():
            report_csv += f"{section}\n"
            df = pd.DataFrame(data)
            report_csv += df.to_csv(index=False)
            report_csv += "\n\n"

        # Return the CSV file for download
        return dict(content=report_csv, filename="full_report.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)