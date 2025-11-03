import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Header

from .config import DATA_DIR, WEBHOOK_SECRET, BROKERAGE_NAME
from .utils import verify_webhook_signature
from .database import get_recent_calls as db_get_recent_calls, get_call_by_id as db_get_call_by_id, get_stats as db_get_stats
from .handlers import (
    handle_end_of_call,
    handle_function_call,
    handle_status_update,
    handle_transcript
)

webhook_router = APIRouter()
api_router = APIRouter()


@webhook_router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": f"{BROKERAGE_NAME} Webhook Server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@webhook_router.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "data_directory": str(DATA_DIR),
        "data_directory_exists": DATA_DIR.exists(),
        "webhook_secret_configured": bool(WEBHOOK_SECRET and WEBHOOK_SECRET != "your-webhook-secret-key")
    }


@webhook_router.post("/webhook")
async def handle_vapi_webhook(
    request: Request,
    x_vapi_signature: Optional[str] = Header(None)
):
    """
    Main webhook endpoint for Vapi callbacks
    """
    try:
        body = await request.body()
        
        if x_vapi_signature and not verify_webhook_signature(body, x_vapi_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        payload = json.loads(body)
        message_type = payload.get("message", {}).get("type")
        
        print(f"\n{'=' * 60}")
        print(f"Received webhook: {message_type}")
        print(f"{'=' * 60}")
        print(f"Payload keys: {list(payload.keys())}")
        print(f"Message keys: {list(payload.get('message', {}).keys())}")
        
        if message_type == "end-of-call-report":
            return await handle_end_of_call(payload)
        
        elif message_type == "function-call" or message_type == "tool-calls":
            return await handle_function_call(payload)
        
        elif message_type == "status-update":
            return await handle_status_update(payload)
        
        elif message_type == "transcript":
            return await handle_transcript(payload)
        
        else:
            print(f"Unhandled message type: {message_type}")
            return {"status": "received", "message_type": message_type}
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/calls")
async def list_calls(limit: int = 50):
    """List recent calls"""
    log_file = DATA_DIR / "all_calls.jsonl"
    
    if not log_file.exists():
        return {"calls": [], "total": 0}
    
    calls = []
    with open(log_file, "r") as f:
        for line in f:
            calls.append(json.loads(line))
    
    calls = calls[-limit:][::-1]
    
    return {"calls": calls, "total": len(calls)}


@api_router.get("/calls/{call_id}")
async def get_call(call_id: str):
    """Get specific call data"""
    log_file = DATA_DIR / "all_calls.jsonl"
    
    if not log_file.exists():
        raise HTTPException(status_code=404, detail="No calls found")
    
    with open(log_file, "r") as f:
        for line in f:
            call_data = json.loads(line)
            if call_data.get("call_id") == call_id:
                return call_data
    
    raise HTTPException(status_code=404, detail=f"Call {call_id} not found")


@api_router.get("/stats")
async def get_statistics():
    """Get call statistics"""
    log_file = DATA_DIR / "all_calls.jsonl"
    
    if not log_file.exists():
        return {"total_calls": 0, "stats": {}}
    
    total_calls = 0
    total_duration = 0
    roles = {}
    asset_types = {}
    
    with open(log_file, "r") as f:
        for line in f:
            call_data = json.loads(line)
            total_calls += 1
            
            if call_data.get("call_duration"):
                total_duration += call_data["call_duration"]
            
            if call_data.get("caller_info"):
                info = call_data["caller_info"]
                if info.get("caller_role"):
                    roles[info["caller_role"]] = roles.get(info["caller_role"], 0) + 1
                if info.get("asset_type"):
                    asset_types[info["asset_type"]] = asset_types.get(info["asset_type"], 0) + 1
    
    return {
        "total_calls": total_calls,
        "average_duration": total_duration / total_calls if total_calls > 0 else 0,
        "caller_roles": roles,
        "asset_types": asset_types
    }


@api_router.get("/db/calls")
async def list_calls_from_db(limit: int = 50):
    """List recent calls from SQLite database"""
    calls = db_get_recent_calls(limit)
    return {"calls": calls, "total": len(calls), "source": "database"}


@api_router.get("/db/calls/{call_id}")
async def get_call_from_db(call_id: str):
    """Get specific call data from SQLite database"""
    call_data = db_get_call_by_id(call_id)
    
    if not call_data:
        raise HTTPException(status_code=404, detail=f"Call {call_id} not found in database")
    
    return call_data


@api_router.get("/db/stats")
async def get_database_statistics():
    """Get call statistics from SQLite database"""
    return db_get_stats()
