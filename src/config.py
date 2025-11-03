import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Brokerage Configuration
BROKERAGE_NAME = os.getenv("BROKERAGE_NAME", "Realflow")

# Server Configuration
PORT = int(os.getenv("PORT", 8000))
HOST = "0.0.0.0"
LOG_LEVEL = "info"

# Security
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret-key")

# Data Storage
DATA_DIR = Path("conversation_data")
DATA_DIR.mkdir(exist_ok=True)

# Application Metadata
APP_TITLE = "Webhook Server"
APP_DESCRIPTION = "Handles Vapi callbacks for real estate assistant"
APP_VERSION = "1.0.0"
