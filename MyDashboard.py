import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import requests
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Fetch data from the provided URL
def fetch_data_from_url():
    url = "https://smartaid.ngrok.io/analytics/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # Assuming the response is JSON data
            return data
        else:
            print("Failed to fetch data")
            return {}
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return {}

# Create a sample data frame for the graph (replace this with actual fetched data)
data = fetch_data_from_url()
# If data is fetched, use it, else use dummy data
if data:
    df = pd.DataFrame(data)
else:
    # Dummy data for the example
    df = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D'],
        'Value': [10, 15, 7, 12]
    })

# Create a simple bar chart using Plotly
fig = px.bar(df, x='Category', y='Value', title='Sample Bar Chart')

# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([ 
        dbc.Col(html.H1("Welcome to the Analytics Dashboard", className="text-center"))
    ], className="mb-4"),
    
    dbc.Row([ 
        dbc.Col(html.A("Visit Analytics Dashboard", href="https://smartaid.ngrok.io/analytics/", target="_blank"))
    ], className="mb-4"),
    
    dbc.Row([ 
        dbc.Col(dcc.Graph(figure=fig))
    ], className="mb-4"),
    
    dbc.Row([ 
        dbc.Col(html.Div("This is a simple example of integrating a plotly graph with data fetched from a URL."))
    ], className="mb-4")
], fluid=True)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
