import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
import json

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
            # Using direct credentials with proper formatting
            firebase_config = {
                "type": "service_account",
                "project_id": "smartaid-6c5c0",
                "private_key_id": "4ca2f01452ce8893c8723ed1b746c9d0d2c86445",
                # Properly formatted multi-line private key
                "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDC9pRncbYZNLbj
2+6W7UOxNvCsOD2g2lFZcrhyuPkYAsQTrMZP5heBGQB7Y3jqU10McPxJ1l/7Y1cm
CVmjz1ea8yTjXk7dJr3IThlZt2uc5BzY82NyktwvpSqwbn9MpXRy3jE/AYfAj0gk
IfW7bxb6T+14Ybi+LbcjjSlTOv93Pof6Znwo+z//XIVBIfdMVui0+4qg/DKm0o3S
I260Q6s1jIy7bYRahSxfQRRqF0ru/NznJwRMmcKpkt9/8LzgK4E79VqUh1XJ2ruA
4oUVYbO+4EYm66MBjDEL+e15pGGmn+XOxep7MsTDtz393HvEKAVsq+gOlHpD8zoQ
XspzUlt7AgMBAAECggEAMOICc61fKxK8iIUsXUtAHb7YuVWgniQfIX5SIPGgAxUu
dIBteLsISaYrKMTYHGiqe+QYXasShcVypGbTwu7J2F/+b8PFok2EaCSs1oHWyY+o
a/0agi+wZYHUIkiSQnV5rRNo5ZNMpktGm0iohEZmTHyd3gEigQyVTqSmJ+gzBYKH
3f26nAhw2tIodtZ4dzeqgEeT1/k9fbBGg1kr5jbzpAbQWoPKcuJYK++XmRpy5Bwo
zT7SPrVXKms1kikOSE8Z/vsOR2WggVg8KU/VrEWWdY8HMPVT9XnyNdp0XxTWiEZr
vNXTqc67TAWy1SMqRaiJgM+OT3xcq0kzZGAsUp4rgQKBgQDwsq+qPgswHZT9OhNJ
shVXejDm5t6bPj+4uKJAqJl8FrTskzM8wuWJghd5AWDJBuETQGYnKmblIjEkmN31
+Y7+QV7DMIUBrOUxmtNNKI3+iFyKHMq3SK5eZc/anSw9yReCWUrDttJJe3tNID73
ZpOgIRTh1H1WksMsUn87LUqsdwKBgQDPW5GLeLmFPLdHE8lkWnDm2spTeBrDq6lz
VFZRM8C2zSsQDvyh+SNT30j1wis6Y4MIkfH6Vi2KBviJ1mTHoJt6iJfhYrOvfIrj
3GZ6inB0ukrzoH4SMMxBFCTt0hsTNZKLyjVZIBIhoHXKD2A0tgbS1AxxrVYD6m2k
1j8E4qg+HQKBgQCRVwRVoxM0YZh2c9vzsxHJ+aGPu7aNPUBS9UIcEvJjCH8FHzlg
JjteFezAh4F+waWk70z/t03cbBIKjDfy8FdU1fo3mJOn2FOo6VlQDP34xTRDvXD2
zW9k1st0sVVmlYeZkPthRIKkFmj0wFTlJM5dcbxfROTOIt6xY7sp64ZcrwKBgELt
neke7Gp4/n6RoZYtniaNpoP5Z+MGJSbM42HdzLdOS20BepfodsOJkYmc4Wb2J2wRM
Hv8/C4nOgC/1LCgm1agyKFuOARM2LponTEhnIK78Zi7GcYqrh3HF77l3JFgJ5ZgL
FzcCG/gQk5Q5bEL3MbKg0LdsTCQNaYBXypVoFwedAoGAcYjcBY+rCpvapxqmZ9JZ
Whj1zxY3mARNzRM1C4n4Z2E33PRcHe6YjyEaZNU2xbW5A05F6/Dhcs6jiu0P5z8R
1I0NyLm6Vh6F8mQh74wTjiKwvRCP9floCqhopkvxHBSfq77ZWG40xsEefu2jvuoX
Udk2n0xMbl1l/aNMLaZTi+8=
-----END PRIVATE KEY-----""",
                "client_email": "firebase-adminsdk-fbsvc@smartaid-6c5c0.iam.gserviceaccount.com",
                "client_id": "117085127067358398910",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40smartaid-6c5c0.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }

            # Debug output to verify key format
            print("Verifying private key format...")
            print(f"Key starts with: {firebase_config['private_key'][:50]}")
            print(f"Key ends with: {firebase_config['private_key'][-50:]}")
            print(f"Key contains BEGIN/END markers: {'BEGIN PRIVATE KEY' in firebase_config['private_key'] and 'END PRIVATE KEY' in firebase_config['private_key']}")

            # Create a temporary file to store the credentials
            with open('temp_firebase_creds.json', 'w') as f:
                json.dump(firebase_config, f)
            
            cred = credentials.Certificate('temp_firebase_creds.json')
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
        
        return firestore.client()
    
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
        # Test read one document
        test_doc = next(db.collection('detection_data').limit(1).stream(), None)
        if test_doc:
            print(f"🔥 Retrieved test document: {test_doc.id}")
        else:
            print("ℹ️ Collection exists but is empty")
    except Exception as e:
        print(f"⚠️ Test read failed: {str(e)}")
else:
    print("❌ Firebase connection failed")

# [Rest of your code remains exactly the same...]

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
