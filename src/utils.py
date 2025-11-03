import json
import httpx
from datetime import datetime
from typing import Optional

from .config import DATA_DIR, GOOGLE_SHEETS_WEBHOOK_URL
from .models import CallerInfo, ConversationData


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify webhook signature for security
    """
    # TODO: Implement webhook signature verification

    return True
    

def save_conversation_data(data: ConversationData, call_id: str):
    """
    Save conversation data to JSON file
    """
    filename = DATA_DIR / f"call_{call_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w") as f:
        json.dump(data.model_dump(), f, indent=2)
    
    print(f"Saved conversation data to: {filename}")
    
    # Also append to a master log file
    log_file = DATA_DIR / "all_calls.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(data.model_dump()) + "\n")


def format_caller_summary(caller_info: CallerInfo) -> str:
    """
    Format caller information into a readable summary
    """
    summary_parts = []
    
    if caller_info.caller_name:
        summary_parts.append(f"Name: {caller_info.caller_name}")
    if caller_info.phone_number:
        summary_parts.append(f"Phone: {caller_info.phone_number}")
    if caller_info.email:
        summary_parts.append(f"Email: {caller_info.email}")
    if caller_info.caller_role:
        summary_parts.append(f"Role: {caller_info.caller_role}")
    if caller_info.asset_type:
        summary_parts.append(f"Asset Type: {caller_info.asset_type}")
    if caller_info.location:
        summary_parts.append(f"Location: {caller_info.location}")
    if caller_info.deal_size:
        summary_parts.append(f"Deal Size: {caller_info.deal_size}")
    if caller_info.urgency:
        summary_parts.append(f"Urgency: {caller_info.urgency}")
    if caller_info.inquiry_summary:
        summary_parts.append(f"Summary: {caller_info.inquiry_summary}")
    if caller_info.additional_notes:
        summary_parts.append(f"Notes: {caller_info.additional_notes}")
    
    return "\n".join(summary_parts) if summary_parts else "No caller information collected"


async def send_to_google_sheets(caller_info: CallerInfo, call_id: Optional[str] = None) -> bool:
    """
    Send caller information to Google Sheets via webhook
    
    Formats data with columns: timestamp, name, role, inquiry, market, notes
    
    Returns True if successful, False otherwise
    """
    print("\n" + "=" * 60)
    print("GOOGLE SHEETS WEBHOOK ATTEMPT")
    print("=" * 60)
    print(f"Webhook URL configured: {bool(GOOGLE_SHEETS_WEBHOOK_URL)}")
    print(f"Webhook URL: {GOOGLE_SHEETS_WEBHOOK_URL[:50] + '...' if GOOGLE_SHEETS_WEBHOOK_URL and len(GOOGLE_SHEETS_WEBHOOK_URL) > 50 else GOOGLE_SHEETS_WEBHOOK_URL or 'NOT SET'}")
    print(f"Caller info: {caller_info.caller_name}")
    
    if not GOOGLE_SHEETS_WEBHOOK_URL:
        print("Google Sheets webhook URL not configured - skipping")
        print("To enable: Set GOOGLE_SHEETS_WEBHOOK_URL in your .env file")
        print("=" * 60 + "\n")
        return False
    
    try:
        # Combine additional_notes and reason_for_calling into notes field
        notes_parts = []
        if caller_info.reason_for_calling:
            notes_parts.append(f"Reason: {caller_info.reason_for_calling}")
        if caller_info.additional_notes:
            notes_parts.append(caller_info.additional_notes)
        if caller_info.deal_size:
            notes_parts.append(f"Deal Size: {caller_info.deal_size}")
        if caller_info.urgency:
            notes_parts.append(f"Urgency: {caller_info.urgency}")
        
        # Format data for Google Sheets
        sheet_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "name": caller_info.caller_name or "Unknown",
            "role": caller_info.caller_role or "Unknown",
            "inquiry": caller_info.inquiry_summary or "No summary",
            "market": caller_info.location or "Not specified",
            "notes": " | ".join(notes_parts) if notes_parts else "None",
            # Include additional fields for reference
            "phone": caller_info.phone_number or "",
            "email": caller_info.email or "",
            "asset_type": caller_info.asset_type or "",
            "call_id": call_id or ""
        }
        
        # Send to webhook
        print("\nSending data to webhook...")
        print(f"Data payload: {json.dumps(sheet_data, indent=2)}")
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.post(
                GOOGLE_SHEETS_WEBHOOK_URL,
                json=sheet_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\nWebhook response status: {response.status_code}")
            print(f"Response body: {response.text[:200]}")
            
            if response.status_code in [200, 201, 202]:
                print(f"Successfully sent to Google Sheets: {caller_info.caller_name}")
                print("=" * 60 + "\n")
                return True
            else:
                print(f"Google Sheets webhook returned status {response.status_code}: {response.text}")
                print("=" * 60 + "\n")
                return False
                
    except httpx.TimeoutException:
        print("Google Sheets webhook timeout - data not sent")
        print("=" * 60 + "\n")
        return False
    except Exception as e:
        print(f"Error sending to Google Sheets: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("=" * 60 + "\n")
        return False
