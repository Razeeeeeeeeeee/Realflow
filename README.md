# Vapi Webhook Server

A webhook server that handles Vapi AI phone calls for commercial real estate lead collection. The assistant answers calls, has natural conversations with prospects, collects their information, and saves everything to a database.

## What it does

- Answers inbound calls instantly with a natural-sounding AI voice
- Has conversational interactions to understand what callers are looking for
- Gently qualifies leads (property type, location, budget, timeline, etc.)
- Collects contact information (name, phone, email)
- Saves all data to SQLite database in real-time
- Stores complete call transcripts and AI-generated summaries
- **Automatically logs call data to Google Sheets** (optional)

## Setup

- Vapi account with API key
- A publicly accessible URL for webhooks (use ngrok for testing)

### Installation

```bash
uv sync
```

### Configuration

Create a `.env` file:

```bash
VAPI_API_KEY=your_vapi_api_key
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_SECRET=your_webhook_secret
BROKERAGE_NAME=Realflow
PORT=8000
```

### Create the assistant

```bash
python create_assistant.py
```

This creates a Vapi assistant configured with:
- GPT-4o for conversation handling
- Cartesia Sonic voice (natural sounding)
- Custom prompts for real estate lead qualification
- Webhook integration for data collection

Save the Assistant ID that gets printed.

### Google Sheets Integration (Optional)

To automatically log all call data to a Google Sheet:

1. Follow the setup guide in **[GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)**
2. Add your webhook URL to `.env`:
   ```bash
   GOOGLE_SHEETS_WEBHOOK_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
   ```
3. Restart your server

Call data will be logged with these columns:
- **Timestamp** - When the call occurred
- **Name** - Caller's name
- **Role** - owner/buyer/broker/lender
- **Inquiry** - What they're looking for
- **Market** - Location/region
- **Notes** - Combined notes (reason, deal size, urgency)

## Running the server

```bash
python app.py
```

The server starts on port 8000 (or whatever you set in .env).

For local testing with ngrok:

```bash
ngrok http 8000
```

## How it works

### Call flow

1. Someone calls your Vapi phone number
2. Assistant answers immediately and introduces itself
3. Natural conversation to understand their needs
4. Collects contact details when appropriate
5. Saves information to database during the call
6. Ends call professionally with confirmation

### Data storage

Everything gets saved to `conversation_data/calls.db`:

**During the call:**
- Caller information stored immediately when submitted

**After the call:**
- Complete transcript
- AI-generated summary
- Call duration, cost, recording URL
- Full conversation metadata

### API endpoints

```bash
GET /health
GET /db/calls?limit=50

GET /db/calls/{call_id}


GET /db/stats
```

## Database structure

The SQLite database has two main tables:

**caller_information:**
- Stores lead data in the exact format received from Vapi
- Includes timestamp, tool call ID, and raw payload
- Saved immediately when caller submits information

**calls:**
- Complete call records
- Transcripts stored as JSON
- AI summaries and success evaluations
- Call metrics and metadata

### Querying the database

```bash
# Open database
sqlite3 conversation_data/calls.db

# Recent leads
SELECT * FROM caller_information ORDER BY submitted_at DESC LIMIT 10;

# Calls with summaries
SELECT call_id, summary, call_duration FROM calls ORDER BY created_at DESC;

# Export to CSV
sqlite3 -header -csv conversation_data/calls.db \
  "SELECT * FROM caller_information;" > leads.csv
```


# Deliverables
```
Assistant ID: e9be887d-0a5b-485d-aba7-d6aabb556a48

I configured the webhook to my local machine and exposed it using ngrok.
The agent outputs to a database and to a webhook.
```