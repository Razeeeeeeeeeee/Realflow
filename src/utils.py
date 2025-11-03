import json
from datetime import datetime

from .config import DATA_DIR
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
