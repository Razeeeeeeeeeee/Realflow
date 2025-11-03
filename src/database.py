import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .models import CallerInfo, ConversationData

# Database file location
DB_PATH = Path("conversation_data/calls.db")


def init_database():
    """Set up database tables if they don't exist"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for caller information (structured format)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caller_information (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT,
            timestamp BIGINT,
            type TEXT,
            tool_call_id TEXT,
            function_name TEXT,
            arguments TEXT,
            raw_payload TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table for complete call data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_id TEXT UNIQUE,
            assistant_id TEXT,
            call_duration REAL,
            call_status TEXT,
            recording_url TEXT,
            summary TEXT,
            success_evaluation TEXT,
            phone_number TEXT,
            started_at TEXT,
            ended_at TEXT,
            end_reason TEXT,
            cost REAL,
            transcript TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH.absolute()}")


def save_caller_info(caller_info: CallerInfo, call_id: str = "unknown", raw_message: Dict[str, Any] = None) -> int:
    """Save caller info in the tool-calls format, returns database ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract tool call details from raw message if provided
    timestamp = None
    message_type = None
    tool_call_id = None
    
    if raw_message:
        timestamp = raw_message.get("timestamp")
        message_type = raw_message.get("type")
        
        # Extract tool call ID
        tool_calls = raw_message.get("toolCalls", [])
        if tool_calls and len(tool_calls) > 0:
            tool_call_id = tool_calls[0].get("id")
    
    # Convert caller info to arguments JSON
    arguments_json = json.dumps(caller_info.dict(exclude_none=True))
    raw_payload_json = json.dumps(raw_message) if raw_message else None
    
    cursor.execute("""
        INSERT INTO caller_information (
            call_id, timestamp, type, tool_call_id,
            function_name, arguments, raw_payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        call_id,
        timestamp,
        message_type or "tool-calls",
        tool_call_id,
        "submit_caller_information",
        arguments_json,
        raw_payload_json
    ))
    
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Saved caller info to database (ID: {row_id})")
    return row_id


def save_call_data(conversation: ConversationData) -> int:
    """Save full call details including transcript and metadata"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert transcript to JSON string
    transcript_json = json.dumps([msg.dict() for msg in conversation.transcript])
    metadata_json = json.dumps(conversation.metadata)
    
    # Insert or update call data
    cursor.execute("""
        INSERT OR REPLACE INTO calls (
            call_id, assistant_id, call_duration, call_status,
            recording_url, summary, success_evaluation,
            phone_number, started_at, ended_at, end_reason, cost,
            transcript, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        conversation.call_id,
        conversation.assistant_id,
        conversation.call_duration,
        conversation.call_status,
        conversation.recording_url,
        conversation.summary,
        conversation.success_evaluation,
        conversation.metadata.get("phone_number"),
        conversation.metadata.get("started_at"),
        conversation.metadata.get("ended_at"),
        conversation.metadata.get("end_reason"),
        conversation.metadata.get("cost"),
        transcript_json,
        metadata_json
    ))
    
    row_id = cursor.lastrowid
    
    # Also save caller info if available
    if conversation.caller_info:
        save_caller_info(conversation.caller_info, conversation.call_id)
    
    conn.commit()
    conn.close()
    
    print(f"Saved call data to database (ID: {row_id})")
    return row_id


def get_caller_info_by_call_id(call_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve caller information by call ID in tool-calls format"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM caller_information 
        WHERE call_id = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (call_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        # Parse JSON fields
        if data.get('arguments'):
            data['arguments'] = json.loads(data['arguments'])
        if data.get('raw_payload'):
            data['raw_payload'] = json.loads(data['raw_payload'])
        return data
    return None


def get_call_by_id(call_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve complete call data by call ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM calls WHERE call_id = ?", (call_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        # Parse JSON fields
        if data.get('transcript'):
            data['transcript'] = json.loads(data['transcript'])
        if data.get('metadata'):
            data['metadata'] = json.loads(data['metadata'])
        return data
    return None


def get_recent_calls(limit: int = 50) -> list[Dict[str, Any]]:
    """Get recent calls"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM calls 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    calls = []
    for row in rows:
        data = dict(row)
        if data.get('transcript'):
            data['transcript'] = json.loads(data['transcript'])
        if data.get('metadata'):
            data['metadata'] = json.loads(data['metadata'])
        calls.append(data)
    
    return calls


def get_stats() -> Dict[str, Any]:
    """Get database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total calls
    cursor.execute("SELECT COUNT(*) FROM calls")
    total_calls = cursor.fetchone()[0]
    
    # Total caller info submissions
    cursor.execute("SELECT COUNT(*) FROM caller_information")
    total_submissions = cursor.fetchone()[0]
    
    # Average call duration
    cursor.execute("SELECT AVG(call_duration) FROM calls WHERE call_duration IS NOT NULL")
    avg_duration = cursor.fetchone()[0] or 0
    
    # Calls by role (parse from JSON arguments)
    cursor.execute("SELECT arguments FROM caller_information WHERE arguments IS NOT NULL")
    roles = {}
    asset_types = {}
    
    for row in cursor.fetchall():
        try:
            args = json.loads(row[0])
            role = args.get("caller_role")
            if role:
                roles[role] = roles.get(role, 0) + 1
            
            asset = args.get("asset_type")
            if asset:
                asset_types[asset] = asset_types.get(asset, 0) + 1
        except (json.JSONDecodeError, KeyError):
            pass
    
    conn.close()
    
    return {
        "total_calls": total_calls,
        "total_submissions": total_submissions,
        "average_duration": round(avg_duration, 2),
        "caller_roles": roles,
        "asset_types": asset_types
    }


def get_caller_info_in_tool_format(call_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve caller information formatted exactly like the tool-calls message
    """
    data = get_caller_info_by_call_id(call_id)
    if not data:
        return None
    
    # Reconstruct in tool-calls format
    return {
        "timestamp": data.get("timestamp"),
        "type": data.get("type"),
        "toolCalls": [
            {
                "id": data.get("tool_call_id"),
                "type": "function",
                "function": {
                    "name": data.get("function_name"),
                    "arguments": data.get("arguments")  # Already parsed as dict
                }
            }
        ]
    }


init_database()
