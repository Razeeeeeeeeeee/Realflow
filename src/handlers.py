import json
from typing import Dict, Any

from .models import CallerInfo, ConversationData, Message
from .utils import save_conversation_data, format_caller_summary, send_to_google_sheets
from .database import save_caller_info


async def handle_end_of_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the end-of-call report with full conversation data
    """
    try:
        message = payload.get("message", {})
        if not isinstance(message, dict):
            print(f"Warning: message is not a dict, it's {type(message)}")
            message = {}
        
        call_data = message
        
        call_obj = call_data.get("call", {})
        if not isinstance(call_obj, dict):
            call_obj = {}
        
        call_id = call_obj.get("id", "unknown")
        assistant_id = call_obj.get("assistantId", "unknown")
        
        transcript_messages = []
        transcript_list = call_data.get("transcript", [])
        if isinstance(transcript_list, list):
            for msg in transcript_list:
                if isinstance(msg, dict):
                    transcript_messages.append(Message(
                        role=msg.get("role", "unknown"),
                        content=msg.get("content", ""),
                        timestamp=msg.get("timestamp")
                    ))
        
        caller_info = None
        call_summary = None
        success_evaluation = None
        
        analysis = call_data.get("analysis", {})
        if isinstance(analysis, dict):
            if "structuredData" in analysis:
                structured = analysis["structuredData"]
                if isinstance(structured, dict):
                    caller_info = CallerInfo(**structured)
            
            call_summary = analysis.get("summary")
            success_evaluation = analysis.get("successEvaluation")
        
        conversation = ConversationData(
            call_id=call_id,
            assistant_id=assistant_id,
            caller_info=caller_info,
            transcript=transcript_messages,
            call_duration=call_obj.get("duration"),
            call_status=call_obj.get("status"),
            recording_url=call_data.get("recordingUrl"),
            summary=call_summary,
            success_evaluation=success_evaluation,
            metadata={
                "phone_number": call_obj.get("phoneNumber"),
                "started_at": call_obj.get("startedAt"),
                "ended_at": call_obj.get("endedAt"),
                "end_reason": call_data.get("endedReason"),
                "cost": call_data.get("cost"),
                "analysis": analysis
            }
        )
        
        save_conversation_data(conversation, call_id)
        
        if caller_info:
            save_caller_info(caller_info, call_id, raw_message=None)
            await send_to_google_sheets(caller_info, call_id)
        
        print("\n" + "CALL SUMMARY ".center(60, "="))
        print(f"\nCall ID: {call_id}")
        print(f"Duration: {conversation.call_duration or 'N/A'} seconds")
        print(f"Status: {conversation.call_status or 'N/A'}")
        
        if call_summary:
            print("\nAI SUMMARY:")
            print("-" * 60)
            print(call_summary)
            print("-" * 60)
        
        if success_evaluation:
            print(f"\nSuccess Evaluation: {success_evaluation}")
        
        if caller_info:
            print("\nCALLER INFORMATION:")
            print("-" * 60)
            print(format_caller_summary(caller_info))
        
        if transcript_messages:
            print(f"\nTRANSCRIPT ({len(transcript_messages)} messages):")
            print("-" * 60)
            for msg in transcript_messages[:10]:
                role_label = "ASSISTANT" if msg.role == "assistant" else "USER"
                print(f"{role_label}: {msg.content[:100]}...")
            if len(transcript_messages) > 10:
                print(f"... and {len(transcript_messages) - 10} more messages")
        
        print("\n" + "=" * 60 + "\n")
        
        return {"status": "success", "call_id": call_id, "data_saved": True}
    
    except Exception as e:
        print(f"Error in handle_end_of_call: {str(e)}")
        print(f"Payload received: {json.dumps(payload, indent=2)}")
        return {"status": "error", "message": str(e)}


async def handle_function_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process function calls when assistant collects caller info
    """
    print("\n" + "FUNCTION CALL HANDLER ".center(60, "="))
    
    message = payload.get("message", {})
    
    print(f"\nRaw payload keys: {list(payload.keys())}")
    print(f"Message keys: {list(message.keys())}")
    
    function_call = message.get("functionCall") or message.get("toolCall")
    tool_call_list = message.get("toolCallList", [])
    if not function_call and tool_call_list:
        function_call = tool_call_list[0] if len(tool_call_list) > 0 else {}
    
    if not function_call:
        function_call = {}
        print("WARNING: No function call found in message!")
        print(f"Full message: {json.dumps(message, indent=2)}")
    
    tool_call_id = function_call.get("id")
    function_name = function_call.get("name") or function_call.get("function", {}).get("name")
    
    parameters = function_call.get("parameters") or function_call.get("function", {}).get("arguments", {})
    if isinstance(parameters, str):
        try:
            parameters = json.loads(parameters)
        except (json.JSONDecodeError, ValueError):
            parameters = {}
    
    print(f"\nFunction called: {function_name}")
    print(f"Tool Call ID: {tool_call_id}")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    if function_name == "submit_caller_information":
        try:
            caller_info = CallerInfo(**parameters)
            
            msg_call_id = message.get("call", {}).get("id", "unknown") if isinstance(message.get("call"), dict) else "unknown"
            db_id = save_caller_info(caller_info, msg_call_id, raw_message=message)
            
            print("\nCALLER INFORMATION SUBMITTED:")
            print("-" * 60)
            print(format_caller_summary(caller_info))
            print(f"Database ID: {db_id}")
            print("-" * 60)
            
            await send_to_google_sheets(caller_info, msg_call_id)
            
            result_message = "Thank you! I've recorded your information. Our team will reach out to you within 24 hours."
            
            response = {
                "result": result_message
            }
            
            if tool_call_id:
                response["toolCallId"] = tool_call_id
            
            print(f"Returning response: {json.dumps(response, indent=2)}")
            return response
            
        except Exception as e:
            print(f"Error processing caller info: {str(e)}")
            error_response = {
                "result": f"Error: {str(e)}"
            }
            if tool_call_id:
                error_response["toolCallId"] = tool_call_id
            return error_response
    
    return {"result": "Function call received"}


async def handle_status_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Track call status changes"""
    message = payload.get("message", {})
    status = message.get("status")
    
    print(f"Status update: {status}")
    
    return {"status": "received"}


async def handle_transcript(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Log transcript as conversation happens"""
    message = payload.get("message", {})
    transcript_type = message.get("transcriptType")
    transcript = message.get("transcript")
    
    if transcript_type == "final":
        print(f"Transcript: {transcript}")
    
    return {"status": "received"}
