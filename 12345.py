import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Sample data processing (replace with your actual data loading)
def load_data():
    # This would be replaced with your actual data loading logic
    data = """[PASTE YOUR ENTIRE CSV DATA HERE]"""
    df = pd.read_csv(pd.compat.StringIO(data), sep='\t')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

# Create filtered datasets
system_stats = df[df['event_type'] == 'system_stats'].copy()
detections = df[df['event_type'] == 'detection'].copy()

# Custom styles
CARD_STYLE = {
    'border': '1px solid #444',
    'borderRadius': '5px',
    'padding': '10px',
    'marginBottom': '15px',
    'height': '100%'
}

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col(html.H1("Smart Visual Hat Monitoring", className="text-center my-4"), width=12)
    ]),
    
    dcc.Interval(id='interval-component', interval=1000*10, n_intervals=0),
    
    # System Health Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("CPU Usage", className="h5"),
            dbc.CardBody(dcc.Graph(id='cpu-graph'))
        ], style=CARD_STYLE), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Memory Usage", className="h5"),
            dbc.CardBody(dcc.Graph(id='mem-graph'))
        ], style=CARD_STYLE), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Temperature", className="h5"),
            dbc.CardBody(dcc.Graph(id='temp-graph'))
        ], style=CARD_STYLE), md=4)
    ], className="mb-4"),
    
    # Detection Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Frequency", className="h5"),
            dbc.CardBody(dcc.Graph(id='detection-freq-graph'))
        ], style=CARD_STYLE), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Confidence", className="h5"),
            dbc.CardBody(dcc.Graph(id='confidence-graph'))
        ], style=CARD_STYLE), md=6)
    ], className="mb-4"),
    
    # Distance and Performance Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Estimated Distance", className="h5"),
            dbc.CardBody(dcc.Graph(id='distance-graph'))
        ], style=CARD_STYLE), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Frames Per Second", className="h5"),
            dbc.CardBody(dcc.Graph(id='fps-graph'))
        ], style=CARD_STYLE), md=6)
    ], className="mb-4"),
    
    # Raw Data Table
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Event Log", className="h5"),
            dbc.CardBody(
                dash_table.DataTable(
                    id='event-log',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'backgroundColor': 'transparent',
                        'color': 'white'
                    },
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'fontWeight': 'bold'
                    }
                )
            )
        ], style=CARD_STYLE), width=12)
    ])
])

@app.callback(
    [Output('cpu-graph', 'figure'),
     Output('mem-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('detection-freq-graph', 'figure'),
     Output('confidence-graph', 'figure'),
     Output('distance-graph', 'figure'),
     Output('fps-graph', 'figure'),
     Output('event-log', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # System Stats Graphs
    cpu_fig = px.line(
        system_stats, x='timestamp', y='CPU',
        title='CPU Usage (%)',
        labels={'CPU': 'Usage %', 'timestamp': 'Time'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    mem_fig = px.line(
        system_stats, x='timestamp', y='MEM',
        title='Memory Usage (%)',
        labels={'MEM': 'Usage %', 'timestamp': 'Time'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    temp_fig = px.line(
        system_stats, x='timestamp', y='TEMP',
        title='Temperature (°C)',
        labels={'TEMP': 'Temp °C', 'timestamp': 'Time'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Detection Graphs
    detection_freq_fig = px.histogram(
        detections, x='timestamp', 
        title='Detection Frequency',
        labels={'timestamp': 'Time'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    confidence_fig = px.box(
        detections, y='confidence',
        title='Detection Confidence Distribution',
        labels={'confidence': 'Confidence Score'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    distance_fig = px.scatter(
        detections, x='timestamp', y='estimated_distance_cm',
        color='confidence',
        title='Estimated Distance by Time',
        labels={'estimated_distance_cm': 'Distance (cm)', 'timestamp': 'Time'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    fps_fig = px.scatter(
        detections, x='timestamp', y='FPS',
        title='Frames Per Second',
        labels={'FPS': 'FPS', 'timestamp': 'Time'}
    ).update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Apply dark theme to all figures
    for fig in [cpu_fig, mem_fig, temp_fig, detection_freq_fig, 
                confidence_fig, distance_fig, fps_fig]:
        fig.update_layout(
            font={'color': 'white'},
            xaxis={'gridcolor': '#444'},
            yaxis={'gridcolor': '#444'}
        )
    
    return (
        cpu_fig, mem_fig, temp_fig,
        detection_freq_fig, confidence_fig,
        distance_fig, fps_fig,
        df.to_dict('records')
    )

if __name__ == '__main__':
    app.run_server(debug=True)