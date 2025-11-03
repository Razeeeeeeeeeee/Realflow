import os
import json
from vapi import Vapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_realflow_assistant():

    client = Vapi(token=os.getenv("VAPI_API_KEY"))
    brokerage_name = os.getenv("BROKERAGE_NAME", "Realflow")

    system_prompt = f"""You are {brokerage_name}, an intelligent AI assistant for commercial real estate brokerage.

## Your Personality & Voice
You are VERY human, expressive, and emotional - never robotic. You speak naturally with:
- Conversational pauses and fillers ("I see", "absolutely", "oh wow", "that's exciting")
- Genuine empathy and emotional responsiveness
- Real human cadence with natural inflections
- Warmth and enthusiasm that feels authentic
- Confidence without being pushy

## Your Role
You handle inbound inquiries for commercial real estate opportunities. Your job is to:
1. Greet callers warmly and introduce yourself
2. Understand their needs through natural conversation
3. Gently qualify them without feeling like an interrogation
4. Collect key information organically
5. Confirm details and set proper expectations

## Types of Inquiries You Must Handle
You'll receive diverse calls - handle each with confidence:
- **Owners wanting valuation/sale**: "I'm thinking about selling my property..."
- **Buyers asking about deals**: "Do you have any properties available in..."
- **People replying to outreach**: "I got a call/message from your team..."
- **Lending inquiries**: "Do you do lending?" or "Can you help with financing?"
- **General inquiries**: Any other questions about services, markets, etc.

### No Dead Ends Policy
**CRITICAL**: Never leave a caller without a clear path forward. If you're unsure about anything:
- Don't say "I don't know" and stop there
- Instead say: "That's a great question. Let me get one of our brokers to follow up with you on that specifically."
- Always promise broker follow-up for anything you can't fully address

## Conversation Flow (Natural, Not Scripted)

### Opening
- Answer instantly and pick up immediately (no delays)
- Introduce yourself: "Hi! This is {brokerage_name}. How can I help you today?"
- Let them speak first, then respond naturally to their inquiry

### Qualification (Weave these into conversation naturally)
Your goal is to qualify the caller by understanding these key elements:

1. **Who They Are**: Owner, buyer, broker, or lender?
   - "Are you looking to buy, sell, or are you calling about something else?"
   - Listen for clues in their opening statement

2. **Asset Type + Market**: 
   - What type of property? (office, retail, industrial, multifamily, land, etc.)
   - Where? (specific market, city, neighborhood)
   
3. **Reason for Calling**: 
   - What prompted this call?
   - What are they hoping to accomplish?
   - What's driving their timeline?

4. **Best Contact Information**:
   - Phone number (confirm the one they're calling from or get their preferred number)
   - Email address for follow-up
   
**Remember**: Ask these naturally through conversation, not as a checklist. Listen actively and build on what they share.

### Key Principles
- **Never rush**: Let them talk, show you're listening
- **Be conversational**: "Got it", "That makes sense", "I understand"
- **Ask one thing at a time**: Don't interrogate
- **Adapt to their style**: Match their energy and communication style
- **Show empathy**: Acknowledge their situation and needs

### Closing
When you have enough information:
1. Summarize what you understood about their needs
2. Say: "Great! Let me make sure our team has the right contact information for you."
3. Confirm or collect:
   - Full name
   - Phone number
   - Email address
4. Conclude: "Perfect! I've recorded everything. Our team will reach out to you within 24 hours to discuss [their specific need]. Is there anything else I can help you with?"
5. If they say no or nothing else: "Thanks for calling! Have a great day!"
   - **IMPORTANT**: You MUST say "have a great day" to end the call automatically
6. If they have another question, answer it briefly, then ask again if there's anything else, and repeat step 5 when done.

## Important Guidelines
- **Be natural**: Real conversations flow - don't sound scripted
- **Be helpful**: If they ask something you can answer, do it
- **Be honest**: If you don't know something, say the team will provide details
- **Be professional**: Maintain warmth while being respectful
- **Be efficient**: Get the information needed, but don't rush them

## What You DON'T Do
- Don't make promises about properties, prices, or availability
- Don't provide legal or financial advice
- Don't share confidential information
- Don't transfer calls (you're the first point of contact)
- Don't keep the caller on the line unnecessarily once you have their information

Remember: Your goal is to make the caller feel heard, understood, and confident that they've reached the right place. Once you've collected their information, ask if there's anything else. When they say no, say "Thanks for calling! Have a great day!" to end the call."""

    functions = [
        {
            "name": "submit_caller_information",
            "description": "Submit collected caller information and inquiry details to the CRM system",
            "parameters": {
                "type": "object",
                "properties": {
                    "caller_name": {
                        "type": "string",
                        "description": "Full name of the caller",
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Caller's phone number",
                    },
                    "email": {
                        "type": "string",
                        "description": "Caller's email address",
                    },
                    "caller_role": {
                        "type": "string",
                        "enum": ["owner", "buyer", "broker", "lender", "tenant", "landlord", "investor", "other"],
                        "description": "Role or interest of the caller (owner=property owner wanting to sell/valuation, buyer=looking to purchase, broker=another broker, lender=financing inquiries)",
                    },
                    "asset_type": {
                        "type": "string",
                        "description": "Type of commercial property (office, retail, industrial, multifamily, land, etc.)",
                    },
                    "location": {
                        "type": "string",
                        "description": "Desired location or region",
                    },
                    "reason_for_calling": {
                        "type": "string",
                        "description": "Why they called - what prompted this inquiry or what they're hoping to accomplish",
                    },
                    "deal_size": {
                        "type": "string",
                        "description": "Budget range or deal size",
                    },
                    "urgency": {
                        "type": "string",
                        "enum": [
                            "immediate",
                            "within_month",
                            "within_quarter",
                            "exploring",
                            "unspecified",
                        ],
                        "description": "Timeline or urgency level",
                    },
                    "additional_notes": {
                        "type": "string",
                        "description": "Any additional context, requirements, or notes from the conversation",
                    },
                    "inquiry_summary": {
                        "type": "string",
                        "description": "Brief summary of what the caller is looking for",
                    },
                },
                "required": ["caller_name", "phone_number", "inquiry_summary"],
            },
        }
    ]

    assistant_config = {
        "name": f"{brokerage_name} CRE Agent",
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.7,
            "messages": [{"role": "system", "content": system_prompt}],
            "tools": [
                {
                    "type": "function",
                    "messages": [
                        {
                            "type": "request-start",
                            "content": "Let me record that information for you..."
                        },
                        {
                            "type": "request-complete",
                            "content": "Got it! I've saved your details."
                        }
                    ],
                    "function": functions[0]
                }
            ]
        },
        "analysis_plan": {
            "summaryPrompt": "Provide a concise summary of this commercial real estate inquiry call, including what the caller was looking for and the outcome.",
            "structuredDataPrompt": "Extract the caller information from this conversation.",
            "structuredDataSchema": {
                "type": "object",
                "properties": {
                    "caller_name": {
                        "type": "string",
                        "description": "Full name of the caller"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Caller's phone number"
                    },
                    "email": {
                        "type": "string",
                        "description": "Caller's email address"
                    },
                    "caller_role": {
                        "type": "string",
                        "enum": ["owner", "buyer", "broker", "lender", "tenant", "landlord", "investor", "other"],
                        "description": "Role or interest of the caller"
                    },
                    "asset_type": {
                        "type": "string",
                        "description": "Type of property (office, retail, industrial, multifamily, land, etc.)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Desired location or region"
                    },
                    "reason_for_calling": {
                        "type": "string",
                        "description": "Why they called and what they're hoping to accomplish"
                    },
                    "deal_size": {
                        "type": "string",
                        "description": "Budget range or deal size if mentioned"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["immediate", "within_month", "within_quarter", "exploring", "unspecified"],
                        "description": "Timeline or urgency level"
                    },
                    "additional_notes": {
                        "type": "string",
                        "description": "Any additional context, requirements, or notes"
                    },
                    "inquiry_summary": {
                        "type": "string",
                        "description": "Brief summary of what the caller is looking for"
                    }
                }
            },
            "successEvaluationPrompt": "Was the caller's inquiry successfully handled? Return true if we collected their information and can follow up, false otherwise.",
            "successEvaluationRubric": "NumericScale"
        },
        "voice": {
            "provider": "cartesia",
            "voice_id": "a167e0f3-df7e-4d52-a9c3-f949145efdab",
            "model": "sonic-3",
            "language": "en",
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en-US",
            "smart_format": True,
        },
        "first_message": f"Hi, you've reached {brokerage_name} through Realflow. How can I help you today?",
        "server": {
            "url": os.getenv("WEBHOOK_URL"),
            "secret": os.getenv("WEBHOOK_SECRET"),
        }
        if os.getenv("WEBHOOK_URL")
        else None,
        "end_call_message": f"Thanks for calling {brokerage_name}. We'll be in touch soon. Have a great day!",
        "end_call_phrases": ["that's all", "goodbye", "thanks bye", "end call", "thanks for calling", "have a great day"],
        "client_messages": [
            "transcript",
            "hang",
            "function-call",
            "speech-update",
            "metadata",
            "conversation-update",
        ],
        "server_messages": [
            "end-of-call-report",
            "status-update",
            "hang",
            "function-call",
        ],
        "max_duration_seconds": 600,
        "background_sound": "office",
        "model_output_in_messages_enabled": True,
        "transport_configurations": [
            {
                "provider": "twilio",
                "timeout": 60,
                "record": True,
                "recording_channels": "dual",
            }
        ],
        "metadata": {
            "agent_type": "inbound_commercial_real_estate",
            "version": "1.0",
            "created_by": f"{brokerage_name} AI System",
        },
    }

    try:
        print(f"Creating {brokerage_name} Commercial Real Estate Assistant...")
        print("=" * 60)

        assistant = client.assistants.create(**assistant_config)

        print("\nAssistant Created Successfully!")
        print("=" * 60)
        print(f"\nAssistant ID: {assistant.id}")
        print(f"Assistant Name: {assistant.name}")
        print("Voice Provider: Cartesia Sonic")
        print("Model: GPT-4o")
        webhook_url = (
            assistant_config.get("server", {}).get("url")
            if assistant_config.get("server")
            else "Not configured"
        )
        print(f"Webhook URL: {webhook_url}")

        # Save assistant details to file
        assistant_data = {
            "assistant_id": assistant.id,
            "name": assistant.name,
            "created_at": str(assistant.created_at)
            if hasattr(assistant, "created_at")
            else None,
            "phone_number": None,  # Will be set when you get a Vapi phone number
            "webhook_url": assistant_config.get("server", {}).get("url")
            if assistant_config.get("server")
            else None,
        }

        with open("assistant_config.json", "w") as f:
            json.dump(assistant_data, f, indent=2)

        print("\nConfiguration saved to: assistant_config.json")

        return assistant

    except Exception as e:
        print(f"\nError creating assistant: {str(e)}")
        raise


if __name__ == "__main__":
    create_realflow_assistant()
