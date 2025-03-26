import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import dash_bootstrap_components as dbc
from datetime import datetime
import json
import os

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# =============================================
# Configuration (Update these for your API)
# =============================================

# API Settings (replace with your actual endpoint)
API_URL = os.getenv('API_URL', 'http://your-visual-hat-api.com/data')  # From environment variables or default
API_KEY = os.getenv('API_KEY', '')  # For authenticated APIs

# Expected data categories (keep these to validate API response)
DEVICE_NAMES = ["Camera", "Processor", "Sensors", "WiFi Module"]
SYSTEM_CATEGORIES = ["CPU", "Memory", "Storage", "Network"]
PI_CATEGORIES = ["CPU Temp", "GPU Temp", "Memory Usage", "Disk Usage"]

# =============================================
# API Service Layer
# =============================================

class DataService:
    @staticmethod
    def fetch_live_data():
        """Fetches real-time data from API with error handling"""
        headers = {'Authorization': f'Bearer {API_KEY}'} if API_KEY else {}
        
        try:
            response = requests.get(API_URL, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Connection Failed: {str(e)}")

# =============================================
# Dashboard Layout (Keep your existing UI)
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    # ... [Your existing layout code remains exactly the same] ...
])

# =============================================
# Callbacks with Pure API Integration
# =============================================

@app.callback(
    [Output('device-distribution', 'figure'),
     Output('power-management', 'figure'),
     Output('power-management-table', 'data'),
     Output('system-performance', 'figure'),
     Output('raspberry-pi', 'figure'),
     Output('temperature-level', 'figure'),
     Output('object-detection-time', 'figure'),
     Output('kpi-cards', 'children'),
     Output('data-status', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    try:
        # Get FRESH data from API every callback
        api_data = DataService.fetch_live_data()
        
        # Validate and transform API response
        device_df = pd.DataFrame(api_data['device_data']).rename(
            columns={'name': 'Device', 'power': 'Power Usage'})
        
        system_df = pd.DataFrame({
            'Category': SYSTEM_CATEGORIES,
            'Value': [
                api_data['system_data']['cpu_usage'],
                api_data['system_data']['memory_usage'],
                api_data['system_data']['storage_usage'],
                api_data['system_data']['network_usage']
            ]
        })
        
        pi_df = pd.DataFrame({
            'Category': PI_CATEGORIES,
            'Value': [
                api_data['pi_data']['cpu_temp'],
                api_data['pi_data']['gpu_temp'],
                api_data['pi_data']['memory_usage'],
                api_data['pi_data']['disk_usage']
            ]
        })
        
        time_df = pd.DataFrame(api_data['time_data']).assign(
            Time=lambda x: pd.to_datetime(x['timestamp']),
            Detection_Time=lambda x: x['detection_time'].astype(float),
            Temperature=lambda x: x['temperature'].astype(float)
        )
        
        status = "Live data"
        
    except Exception as e:
        # Minimal fallback - empty but valid structures
        device_df = pd.DataFrame(columns=['Device', 'Power Usage'])
        system_df = pd.DataFrame(columns=['Category', 'Value'])
        pi_df = pd.DataFrame(columns=['Category', 'Value'])
        time_df = pd.DataFrame(columns=['Time', 'Detection Time', 'Temperature'])
        status = f"Error: {str(e)}"

    # Generate visualizations (unchanged from your original)
    device_fig = px.bar(device_df, x="Device", y="Power Usage", ...)  # Your existing code
    power_fig = px.bar(...)  # Keep your original visualization code
    # ... [All other figures remain exactly as you had them] ...

    return (
        device_fig, power_fig, device_df.to_dict('records'),
        system_performance_fig, raspberry_pi_fig,
        temp_fig, detection_fig, kpi_cards,
        status
    )

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)