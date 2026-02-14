from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import os
import pandas as pd
import hashlib
import uuid
import json
import tempfile

import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = FastAPI()

# Allow OAuth over HTTP for local testing ONLY
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# -------------------------------
# Build client_secrets.json from env (Vercel-safe)
# -------------------------------

CLIENT_SECRETS_FILE = "client_secret_web.json"

if not os.path.exists(CLIENT_SECRETS_FILE):
    secrets = {
        "web": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URI")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(tmp.name, "w") as f:
        json.dump(secrets, f)

    CLIENT_SECRETS_FILE = tmp.name

# -------------------------------
# Google Sheets setup
# -------------------------------

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

if "GOOGLE_SERVICE_ACCOUNT_JSON" in os.environ:
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
else:
    # Local dev fallback (file in project root, gitignored)
    with open("service_account.json", "r") as f:
        service_account_info = json.load(f)

sheets_creds = Credentials.from_service_account_info(
    service_account_info, scopes=SHEETS_SCOPES
)

sheets_client = gspread.authorize(sheets_creds)

SHEET_NAME = "All_subscriptions"  # <-- change if needed
sheet = sheets_client.open(SHEET_NAME).sheet1

def append_df_to_sheet(df):
    if len(sheet.get_all_values()) == 0:
        sheet.append_row(list(df.columns))

    rows = df.values.tolist()
    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")

# -------------------------------
# YouTube OAuth setup
# -------------------------------

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

# -------------------------------
# Routes
# -------------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
    <head>
        <title>YouTube Research Tool</title>
        <style>
            body {
                font-family: Arial;
                text-align: center;
                padding: 40px;
                background-color: #f5f5f5;
            }
            .btn {
                padding: 12px 25px;
                background-color: #ff0000;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }
            iframe {
                margin-top: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>

        <h1>YouTube Subscription Research Tool</h1>

        <p>
            <a href="/login" class="btn">Connect your YouTube</a>
        </p>

        <h2>🎥 Demo Video</h2>

        <iframe width="800" height="450"
            src="https://youtu.be/1stDRZrML5o"
            frameborder="0"
            allowfullscreen>
        </iframe>

    </body>
    </html>
    """

@app.get("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return RedirectResponse(authorization_url)

@app.get("/oauth2callback", response_class=HTMLResponse)
def oauth2callback(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    youtube = build("youtube", "v3", credentials=credentials)

    me = youtube.channels().list(part="id", mine=True).execute()

    if "items" in me and len(me["items"]) > 0:
        user_channel_id = me["items"][0]["id"]
        user_hash = hashlib.sha256(user_channel_id.encode()).hexdigest()
    else:
        user_hash = "anon_" + uuid.uuid4().hex

    rows = []
    req = youtube.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=50
    )

    while req is not None:
        res = req.execute()
        for item in res.get("items", []):
            rows.append({
                "user_id": user_hash,
                "channel_id": item["snippet"]["resourceId"]["channelId"],
                "channel_title": item["snippet"]["title"]
            })
        req = youtube.subscriptions().list_next(req, res)

    df = pd.DataFrame(rows)

    append_df_to_sheet(df)

    return f"""
    <h3>Thank you!</h3>
    <p>Saved {len(rows)} subscriptions.</p>
    <p>You can close this window.</p>
    """
