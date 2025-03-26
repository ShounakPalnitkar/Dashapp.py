import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from io import StringIO

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# =============================================
# Embedded CSV Data
# =============================================

CSV_DATA = """
timestamp,event_type,label,confidence,estimated_distance_cm,FPS,CPU,MEM,TEMP
2025-03-26 12:52:09,system_stats,,,NaN,NaN,0,19.5,66.4
2025-03-26 13:04:13,detection,person,0.73,37.17,6.55,,,
2025-03-26 13:04:14,detection,person,0.58,42.28,11.55,,,
2025-03-26 13:04:52,system_stats,,,NaN,NaN,40.3,24.3,82.9
2025-03-26 13:04:17,detection,person,0.73,34.72,11.84,,,
2025-03-26 13:04:27,detection,person,0.93,48.66,10.02,,,
2025-03-26 13:04:47,detection,person,0.58,84.93,10.72,,,
2025-03-26 13:05:12,system_stats,,,NaN,NaN,40.2,25.2,82.9
2025-03-26 13:05:34,detection,person,0.79,65.47,10.48,,,
2025-03-26 13:06:12,system_stats,,,NaN,NaN,39.7,23.4,84.5
"""

def load_data():
    """Load data from embedded CSV string"""
    try:
        df = pd.read_csv(StringIO(CSV_DATA), parse_dates=['timestamp'])
        
        # Clean temperature data if needed
        if 'TEMP' in df.columns and df['TEMP'].dtype == object:
            df['TEMP'] = df['TEMP'].astype(str).str.replace('°C', '').astype(float)
            
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['timestamp', 'event_type', 'label', 'confidence',
                                   'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'])

# =============================================
# Dashboard Layout
# =============================================

app.layout = dbc.Container(fluid=True, children=[
    # Title
    dbc.Row([
        dbc.Col(html.H1("Smart Hat Analytics Dashboard", 
                       className="text-center my-4"))
    ]),
    
    # Refresh interval
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),
    
    # System Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("CPU Usage (%)", className="h5"),
            dbc.CardBody(dcc.Graph(id='cpu-graph'))
        ], className="shadow"), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Memory Usage (%)", className="h5"),
            dbc.CardBody(dcc.Graph(id='mem-graph'))
        ], className="shadow"), md=4),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Temperature (°C)", className="h5"),
            dbc.CardBody(dcc.Graph(id='temp-graph'))
        ], className="shadow"), md=4)
    ], className="mb-4"),
    
    # Detection Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Frequency", className="h5"),
            dbc.CardBody(dcc.Graph(id='detection-freq'))
        ], className="shadow"), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Detection Confidence", className="h5"),
            dbc.CardBody(dcc.Graph(id='confidence-hist'))
        ], className="shadow"), md=6)
    ], className="mb-4"),
    
    # Distance and Performance Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Object Distance (cm)", className="h5"),
            dbc.CardBody(dcc.Graph(id='distance-graph'))
        ], className="shadow"), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Frames Per Second", className="h5"),
            dbc.CardBody(dcc.Graph(id='fps-graph'))
        ], className="shadow"), md=6)
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Event Log", className="h5"),
            dbc.CardBody(
                dash_table.DataTable(
                    id='data-table',
                    columns=[{"name": i, "id": i} for i in [
                        'timestamp', 'event_type', 'label', 'confidence',
                        'estimated_distance_cm', 'FPS', 'CPU', 'MEM', 'TEMP'
                    ]],
                    page_size=10,
                    style_table={'overflowX': 'auto', 'height': '300px'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'backgroundColor': 'rgba(0,0,0,0)',
                        'color': 'white',
                        'border': '1px solid #444'
                    },
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'fontWeight': 'bold'
                    },
                    filter_action="native",
                    sort_action="native"
                )
            )
        ], className="shadow"), width=12)
    ])
])

# =============================================
# Callbacks
# =============================================

@app.callback(
    [Output('cpu-graph', 'figure'),
     Output('mem-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('detection-freq', 'figure'),
     Output('confidence-hist', 'figure'),
     Output('distance-graph', 'figure'),
     Output('fps-graph', 'figure'),
     Output('data-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = load_data()
    
    # Filter data
    system_stats = df[df['event_type'] == 'system_stats'].copy()
    detections = df[df['event_type'] == 'detection'].copy()
    
    # Create figures
    cpu_fig = px.line(
        system_stats, x='timestamp', y='CPU',
        title='', labels={'CPU': 'Usage %'},
        color_discrete_sequence=['#1f77b4']
    )
    
    mem_fig = px.line(
        system_stats, x='timestamp', y='MEM',
        title='', labels={'MEM': 'Usage %'},
        color_discrete_sequence=['#ff7f0e']
    )
    
    temp_fig = px.line(
        system_stats, x='timestamp', y='TEMP',
        title='', labels={'TEMP': '°C'},
        color_discrete_sequence=['#d62728']
    ).add_hline(y=80, line_dash="dash", line_color="red")
    
    detection_freq = px.histogram(
        detections, x='timestamp', 
        title='', labels={'timestamp': 'Time'},
        color_discrete_sequence=['#2ca02c']
    )
    
    confidence_hist = px.histogram(
        detections, x='confidence',
        title='', labels={'confidence': 'Score'},
        color_discrete_sequence=['#9467bd']
    )
    
    distance_fig = px.scatter(
        detections, x='timestamp', y='estimated_distance_cm',
        color='confidence',
        title='', labels={'estimated_distance_cm': 'Distance (cm)'},
        color_continuous_scale='Viridis'
    )
    
    fps_fig = px.scatter(
        detections, x='timestamp', y='FPS',
        title='', labels={'FPS': 'Frames Per Second'},
        color_discrete_sequence=['#17becf']
    )
    
    # Apply consistent styling
    for fig in [cpu_fig, mem_fig, temp_fig, detection_freq, 
               confidence_hist, distance_fig, fps_fig]:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            margin={'l': 40, 'r': 40, 't': 30, 'b': 30},
            xaxis={'gridcolor': '#444'},
            yaxis={'gridcolor': '#444'}
        )
    
    return (
        cpu_fig, mem_fig, temp_fig,
        detection_freq, confidence_hist,
        distance_fig, fps_fig,
        df.to_dict('records')
    )

# =============================================
# Run the App
# =============================================

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)