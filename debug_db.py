#!/usr/bin/env python3
"""
Database diagnostic script to check tables and identify issues
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("conversation_data/calls.db")

def check_database():
    """Check database contents and structure"""
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH.absolute()}")
        return
    
    print(f"✅ Database found at: {DB_PATH.absolute()}\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check caller_information table
    print("=" * 60)
    print("CALLER_INFORMATION TABLE")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM caller_information")
    count = cursor.fetchone()[0]
    print(f"Total rows: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM caller_information ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("\nMost recent entries:")
        for row in rows:
            print(f"  ID: {row[0]}, Call ID: {row[1]}, Function: {row[5]}")
    else:
        print("⚠️  No rows found in caller_information table")
    
    # Check calls table
    print("\n" + "=" * 60)
    print("CALLS TABLE")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM calls")
    count = cursor.fetchone()[0]
    print(f"Total rows: {count}")
    
    if count > 0:
        cursor.execute("SELECT call_id, phone_number, call_status, call_duration FROM calls ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("\nMost recent calls:")
        for row in rows:
            print(f"  Call ID: {row[0]}")
            print(f"    Phone: {row[1]}")
            print(f"    Status: {row[2]}")
            print(f"    Duration: {row[3]}s")
            print()
    else:
        print("⚠️  No rows found in calls table")
    
    # Check for calls with caller info in analysis
    if count > 0:
        print("=" * 60)
        print("CHECKING FOR CALLER INFO IN CALL METADATA")
        print("=" * 60)
        
        cursor.execute("SELECT call_id, metadata FROM calls WHERE metadata IS NOT NULL")
        rows = cursor.fetchall()
        
        import json
        found_caller_info = False
        for row in rows:
            call_id, metadata_json = row
            try:
                metadata = json.loads(metadata_json)
                analysis = metadata.get('analysis', {})
                if 'structuredData' in analysis and analysis['structuredData']:
                    print(f"\n✅ Found structured data in call {call_id}:")
                    print(f"   {json.dumps(analysis['structuredData'], indent=4)}")
                    found_caller_info = True
            except json.JSONDecodeError:
                pass
        
        if not found_caller_info:
            print("⚠️  No calls have structured data in analysis")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    
    if count == 0:
        print("❌ No calls have been recorded yet")
        print("   - Check if the webhook server is running")
        print("   - Check if calls are being made to the assistant")
        print("   - Check webhook URL configuration")
    else:
        print("✅ Calls are being recorded")
        
        cursor = sqlite3.connect(DB_PATH).cursor()
        cursor.execute("SELECT COUNT(*) FROM caller_information")
        caller_count = cursor.fetchone()[0]
        
        if caller_count == 0:
            print("❌ But caller_information is empty")
            print("\nPossible reasons:")
            print("   1. Assistant not calling submit_caller_information function")
            print("   2. Webhook not receiving function-call messages")
            print("   3. Function call handler failing silently")
            print("\nTo debug:")
            print("   - Check webhook server logs during a test call")
            print("   - Look for 'Function called: submit_caller_information' in logs")
            print("   - Verify WEBHOOK_URL in .env matches your ngrok/public URL")


if __name__ == "__main__":
    check_database()
