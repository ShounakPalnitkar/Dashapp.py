import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from io import StringIO
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Firebase credentials
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "smartaid-6c5c0",
    "private_key_id": "4ca2f01452ce8893c8723ed1b746c9d0d2c86445",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDC9pRncbYZNLbj\n2+6W7UOxNvCsOD2g2lFZcrhyuPkYAsQTrMZP5heBGQB7Y3jqU10McPxJ1l/7Y1cm\nCVmjz1ea8yTjXk7dJr3IThlZt2uc5BzY82NyktwvpSqwbn9MpXRy3jE/AYfAj0gk\nIfW7bxb6T+14Ybi+LbcjjSlTOv93Pof6Znwo+z//XIVBIfdMVui0+4qg/DKm0o3S\nI260Q6s1jIy7bYRahSxfQRRqF0ru/NznJwRMmcKpkt9/8LzgK4E79VqUh1XJ2ruA\n4oUVYbO+4EYm66MBjDEL+e15pGGmn+XOxep7MsTDtz393HvEKAVsq+gOlHpD8zoQ\nXspzUlt7AgMBAAECggEAMOICc61fKxK8iIUsXUtAHb7YuVWgniQfIX5SIPGgAxUu\ndIBteLsISaYrKMTYHGiqe+QYXasShcVypGbTwu7J2F/+b8PFok2EaCSs1oHWyY+o\na/0agi+wZYHUIkiSQnV5rRNo5ZNMpktGm0iohEZmTHyd3gEigQyVTqSmJ+gzBYKH\n3f26nAhw2tIodtZ4dzeqgEeT1/k9fbBGg1kr5jbzpAbQWoPKcuJYK++XmRpy5Bwo\nzT7SPrVXKms1kikOSE8Z/vsOR2WggVg8KU/VrEWWdY8HMPVT9XnyNdp0XxTWiEZr\nvNXTqc67TAWy1SMqRaiJgM+OT3xcq0kzZGAsUp4rgQKBgQDwsq+qPgswHZT9OhNJ\nshVXejDm5t6bPj+4uKJAqJl8FrTskzM8wuWJghd5AWDJBuETQGYnKmblIjEkmN31\n+Y7+QV7DMIUBrOUxmtNNKI3+iFyKHMq3SK5eZc/anSw9yReCWUrDttJJe3tNID73\nZpOgIRTh1H1WksMsUn87LUqsdwKBgQDPW5GLeLmFPLdHE8lkWnDm2spTeBrDq6lz\nVFZRM8C2zSsQDvyh+SNT30j1wis6Y4MIkfH6Vi2KBviJ1mTHoJt6iJfhYrOvfIrj\n3GZ6inB0ukrzoH4SMMxBFCTt0hsTNZ..."
})

# Initialize Firebase Admin
firebase_admin.initialize_app(cred)
db = firestore.client()

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
    # Your dashboard layout code here...
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
    
    # Firebase integration - for example, write data to Firebase
    db.collection('analytics_data').add({
        'timestamp': df['timestamp'][0],
        'cpu': df['CPU'][0],
        'mem': df['MEM'][0],
        'temp': df['TEMP'][0]
    })

    # Your existing code to update figures
    # ...

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