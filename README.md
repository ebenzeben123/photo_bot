# Gorilla Photo Bot

This is a production-ready Telegram bot that receives photo uploads from field reps and posts them to JobNimbus jobs. It supports both topic-based and group-based workflows, with exact and fuzzy job name matching, and a fallback caption prompt when no job is initially detected.

## Features

- Uploads Telegram photo messages to matching JobNimbus jobs
- Automatically detects job name from:
  - Telegram topic title (used for exact match)
  - Photo caption (used for exact or fuzzy match)
  - User reply after photo upload
  - Edited photo caption
- Fuzzy matching with inline confirmation buttons for multiple results
- Silent operation in topics (no confirmation replies)
- Confirmation replies in groups for successful or failed uploads
- Logs upload results to the console
- Optional integration with reserved ngrok domain for webhook delivery

## Project Structure

summary_bot/
├── bot.py              # Main logic for handling uploads and routing
├── config.py           # Loads secrets from .env
├── utils.py            # Handles API search and upload requests
├── jobnimbus.py        # Button generation and reusable JobNimbus helpers
├── .env                # Secrets (Telegram token, JobNimbus API key)
├── .gitignore
├── requirements.txt
└── run_bot.bat         # Starts bot from venv (used with Task Scheduler)

## Setup

1. Clone the repo and install Python 3.11
2. Create and activate a virtual environment:

   python -m venv venv
   venv\Scripts\activate

3. Install dependencies:

   pip install -r requirements.txt

4. Add a .env file with the following values:

   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   JOBNIMBUS_API_KEY=your_jobnimbus_api_key

5. Launch the bot:

   python bot.py

   Or use run_bot.bat to include the venv activation automatically.

## Webhook Support (optional)

To expose your bot to the internet for webhooks, use ngrok with a reserved domain.

Example ngrok.yml:

version: 3
agent:
  authtoken: your_ngrok_token

tunnels:
  telegram_bot:
    proto: http
    addr: 500
    domain: your-reserved-subdomain.ngrok.app

Start ngrok:

   ngrok start telegram_bot

Then set your Telegram webhook URL to:

   https://your-reserved-subdomain.ngrok.app/webhook

## Notes

- Job names must match exactly when coming from topic titles
- Bracketed text (e.g. [Roofing]) in topic names is automatically stripped before searching
- Photos sent in group chats with no caption will trigger a prompt for the job name
- Matching logic is case-insensitive and supports partial matches when needed

---

PRs and cleanups welcome. This bot is tuned for field speed and reliability in production.
