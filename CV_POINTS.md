# CV Points - Realflow AI Voice Agent Project

## Project Overview
Developed an enterprise-grade AI voice agent system for commercial real estate lead qualification using Vapi AI, handling inbound calls with natural language processing and automated data collection.

## Technical Skills Demonstrated

### Backend Development & API Design
- Built RESTful API server using **FastAPI** with async/await patterns for high-performance webhook processing
- Implemented webhook authentication and security with HMAC signature verification
- Designed scalable microservices architecture with separation of concerns (routes, handlers, models, database layers)
- Created multiple API endpoints for health checks, data retrieval, and statistics (`/health`, `/db/calls`, `/db/stats`)

### AI & Natural Language Processing Integration
- Integrated **Vapi AI SDK** for voice conversation handling with GPT-4o language model
- Configured advanced AI voice synthesis using **Cartesia Sonic** for natural-sounding speech
- Implemented **Deepgram Nova-2** speech-to-text transcription with smart formatting
- Designed comprehensive system prompts for conversational AI with personality and context awareness
- Built function calling mechanism for AI agent to invoke data collection tools during conversations

### Database Design & Management
- Designed and implemented **SQLite** database schema with normalized tables for call records and lead information
- Created efficient database queries with proper indexing for fast data retrieval
- Implemented transaction management for data integrity during concurrent call processing
- Built database migration and initialization system with automatic table creation
- Developed JSON-based storage for complex nested data structures (transcripts, metadata)

### Data Processing & Webhook Integration
- Developed real-time webhook handler for processing various event types (function calls, call status, end-of-call reports)
- Implemented structured data extraction from AI-generated conversation analysis
- Built parser for complex nested JSON payloads from external APIs
- Created automated data pipeline sending lead information to Google Sheets via webhook
- Implemented error handling and fallback mechanisms for external service failures

### Real-time Communication & Event Processing
- Handled asynchronous event streams from telephony system (Twilio integration)
- Processed real-time transcript updates during active phone calls
- Implemented status tracking for call lifecycle management (queued, in-progress, completed)
- Built logging system for conversation monitoring and debugging

### Software Engineering Best Practices
- Applied clean code principles with modular architecture (config, routes, handlers, models, database, utils)
- Used **Pydantic** for data validation and type safety with BaseModel schemas
- Implemented comprehensive error handling with try-catch blocks and logging
- Created environment-based configuration management with `.env` files
- Followed RESTful API design patterns and HTTP status code conventions

### DevOps & Deployment
- Configured **Uvicorn** ASGI server with hot-reload for development
- Set up dependency management using modern Python tooling (uv package installer, requirements.txt, pyproject.toml)
- Implemented ngrok integration for local webhook testing and development
- Created deployment-ready configuration with customizable host, port, and log levels
- Built initialization scripts for automated assistant creation and configuration

### Third-Party API Integration
- Integrated **Vapi AI API** with proper authentication and error handling
- Connected to **Google Sheets API** via webhooks for automated data export
- Implemented **Twilio** telephony integration for call recording and dual-channel audio
- Built OAuth and API key management for secure external service access

### Data Analytics & Reporting
- Created aggregation queries for business intelligence (call statistics, lead metrics)
- Built role and asset type distribution analytics from structured data
- Implemented average call duration calculations and success rate tracking
- Designed CSV export functionality for external data analysis
- Developed real-time dashboard endpoints for monitoring system health

## Key Achievements

### Performance & Scalability
- Achieved instant call answering with zero delay through optimized webhook processing
- Handled concurrent calls with async architecture and proper resource management
- Implemented efficient database queries with pagination support (configurable page limits)
- Built system capable of processing calls up to 10 minutes with full transcript storage

### User Experience & Business Impact
- Created natural conversational flow that collects 11+ data points without feeling like interrogation
- Implemented intelligent lead qualification logic for commercial real estate (property type, location, budget, timeline)
- Built automatic follow-up system by capturing contact information (name, phone, email)
- Designed professional call flow with proper greetings and closing statements

### Code Quality & Maintainability
- Wrote clean, documented code with type hints and docstrings
- Created separation of concerns with dedicated modules for each functionality area
- Implemented consistent error handling patterns across the codebase
- Built configurable system with centralized configuration management

## Technologies Used

**Languages & Frameworks:**
- Python 3.x
- FastAPI (async web framework)
- Pydantic (data validation)
- SQLite (database)

**AI & Voice:**
- Vapi AI (conversation orchestration)
- OpenAI GPT-4o (language model)
- Cartesia Sonic (voice synthesis)
- Deepgram Nova-2 (speech recognition)

**Infrastructure & Tools:**
- Uvicorn (ASGI server)
- ngrok (webhook tunneling)
- Twilio (telephony)
- Google Sheets API (data export)
- python-dotenv (configuration)
- httpx (HTTP client)

**Development Practices:**
- RESTful API design
- Async/await programming
- Webhook architecture
- Event-driven design
- Database normalization
- Type safety with Pydantic

## Project Metrics
- **Lines of Code:** 800+ lines of production Python code
- **API Endpoints:** 5+ RESTful endpoints
- **Database Tables:** 2 normalized tables with complex relationships
- **External Integrations:** 4 major third-party services (Vapi, OpenAI, Cartesia, Deepgram)
- **Data Points Collected:** 11+ structured fields per lead
- **Max Call Duration:** 600 seconds with full recording and transcription
