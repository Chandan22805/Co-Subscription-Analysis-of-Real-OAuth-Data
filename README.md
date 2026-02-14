📺 YouTube Subscription Research Tool

A FastAPI-based backend application that allows users to connect their YouTube account via Google OAuth and securely stores their subscription data into Google Sheets for research and analysis purposes.

⸻

🚀 Overview

This application:
	•	Authenticates users using Google OAuth
	•	Fetches the user’s YouTube channel ID
	•	Retrieves all their YouTube subscriptions
	•	Anonymizes the user using SHA256 hashing
	•	Stores subscription data into Google Sheets

It is designed to be secure, scalable, and deployable on platforms like Vercel, Render, or Railway.

⸻

🛠 Tech Stack
	•	FastAPI – Backend framework
	•	Google OAuth 2.0 – Authentication
	•	YouTube Data API v3 – Subscription retrieval
	•	Google Sheets API – Data storage
	•	gspread – Sheets integration
	•	Pandas – Data handling

⸻

📂 Project Structure

.
├── main.py
├── service_account.json (local only, gitignored)
├── requirements.txt
└── README.md


⸻

🔐 Environment Variables Required

Set the following environment variables:

GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
GOOGLE_SERVICE_ACCOUNT_JSON

Notes:
	•	GOOGLE_SERVICE_ACCOUNT_JSON should contain the entire JSON string of your service account credentials.
	•	GOOGLE_REDIRECT_URI must match what you configured in Google Cloud Console.

⸻

⚙️ Google Cloud Setup

1️⃣ Enable APIs

Enable:
	•	YouTube Data API v3
	•	Google Sheets API
	•	Google Drive API

2️⃣ Create OAuth Credentials

Create OAuth credentials (Web Application) and configure:
	•	Authorized redirect URI:




3️⃣ Create Service Account
	•	Create a Service Account
	•	Download JSON credentials
	•	Share your Google Sheet with the service account email

⸻

📊 Google Sheet Setup

Create a Google Sheet named:

All_subscriptions

Share it with your service account email.

The app automatically:
	•	Adds headers if empty
	•	Appends subscription rows

⸻

▶️ Running Locally

1️⃣ Install dependencies

pip install -r requirements.txt

2️⃣ Run server

uvicorn main:app --reload

3️⃣ Open in browser




⸻

🔄 Application Flow
	1.	User clicks Connect your YouTube
	2.	Redirected to Google OAuth
	3.	User grants permission
	4.	App fetches:
	•	User channel ID
	•	All subscriptions
	5.	User ID is hashed
	6.	Data is appended to Google Sheets

⸻

🧾 Stored Data Format

user_id (hashed)	channel_id	channel_title



⸻

🔒 Security Features
	•	User identity is anonymized using SHA256 hashing
	•	OAuth credentials are stored in environment variables
	•	No sensitive user data is stored permanently
	•	Service account access is restricted to specific sheet

⸻

⚠️ Important Notes
	•	OAUTHLIB_INSECURE_TRANSPORT=1 is enabled for local testing only.
	•	Remove it in production environments using HTTPS.
	•	Ensure your deployment platform supports environment variables.

⸻

📦 Deployment

Compatible with:
	•	Vercel
	•	Railway
	•	Render
	•	Any platform supporting FastAPI + environment variables

Ensure:
	•	Environment variables are properly configured
	•	Redirect URI matches deployment URL

⸻

🚀 Possible Enhancements
	•	Add timestamp column
	•	Store subscriber counts
	•	Store channel categories
	•	Add database instead of Sheets
	•	Add dashboard UI
	•	Add analytics processing layer

⸻

📜 License

This project is intended for research and educational purposes.

⸻
