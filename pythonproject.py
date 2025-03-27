import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# ================================================
# Firebase Configuration with Enhanced Error Handling
# ================================================

def initialize_firebase():
    """Initialize Firebase with proper credential handling"""
    try:
        if not firebase_admin._apps:
            # Ensure Firebase credentials are set through environment variables or secure file
            firebase_creds = os.getenv("FIREBASE_CREDS_JSON_PATH", "path_to_your_firebase_creds.json")
            
            if not firebase_creds or not os.path.exists(firebase_creds):
                raise FileNotFoundError("Firebase credentials file not found. Ensure you have set the correct path.")

            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
        
        return firestore.client()
    
    except FileNotFoundError as e:
        print(f"🔥 Firebase credentials error: {str(e)}")
    except Exception as e:
        print(f"🔥 Firebase initialization failed: {str(e)}")
    
    return None

# Initialize Firebase connection with verification
print("Initializing Firebase...")
db = initialize_firebase()

# Verify connection
if db:
    print("✅ Firebase connection successful")
    try:
        # Test read one document to verify the connection works
        test_doc = next(db.collection('detection_data').limit(1).stream(), None)
        if test_doc:
            print(f"🔥 Retrieved test document: {test_doc.id}")
        else:
            print("ℹ️ Collection exists but is empty")
    except Exception as e:
        print(f"⚠️ Test read failed: {str(e)}")
else:
    print("❌ Firebase connection failed")

# ===================
# Dash App Layout
# ===================
app.layout = html.Div([
    html.H1("Firebase Integration with Dash", className="text-center"),
    
    # Add Dash components like graphs, tables, etc.
])

# ===================
# App Callbacks
# ===================
@app.callback(
    Output('output-container', 'children'),
    Input('input-component', 'value')
)
def update_output(value):
    # Callback function to process user input
    return f'Output: {value}'

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
