from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CallerInfo(BaseModel):
    """Structured caller information"""
    caller_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    caller_role: Optional[str] = None  # owner, buyer, broker, lender, tenant, landlord, investor, other
    asset_type: Optional[str] = None
    location: Optional[str] = None
    reason_for_calling: Optional[str] = None
    deal_size: Optional[str] = None
    urgency: Optional[str] = None
    additional_notes: Optional[str] = None
    inquiry_summary: Optional[str] = None


class Message(BaseModel):
    """Individual message in conversation"""
    role: str
    content: str
    timestamp: Optional[str] = None


class ConversationData(BaseModel):
    """Complete conversation data"""
    call_id: str
    assistant_id: str
    caller_info: Optional[CallerInfo] = None
    transcript: list[Message] = []
    call_duration: Optional[float] = None
    call_status: Optional[str] = None
    recording_url: Optional[str] = None
    summary: Optional[str] = None  # AI-generated call summary
    success_evaluation: Optional[str] = None  # Whether call objectives were met
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
