"""
AI-Powered Excel Mock Interviewer
Main FastAPI application with intelligent interview agent
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os
from dotenv import load_dotenv

from interview_agent import InterviewAgent
from connection_manager import ConnectionManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Excel Mock Interviewer",
    description="Automated technical interview system for Excel proficiency assessment",
    version="1.0.0"
)

# CORS middleware configuration
origins = [
    "http://localhost:3000",  # React development server
    "http://localhost:8000",  # FastAPI development server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Static files
# Templates (for HTML responses) - removed static files mounting
templates = None

# Initialize services
connection_manager = ConnectionManager()

class InterviewOrchestrator:
    """Main orchestrator that coordinates all interview components"""
    
    def __init__(self):
        self.active_interviews: Dict[str, InterviewAgent] = {}
        self.session_states: Dict[str, dict] = {}
    
    async def start_interview(self, session_id: str, candidate_info: dict) -> InterviewAgent:
        """Initialize a new interview session"""
        try:
            # Create interview agent
            agent = InterviewAgent(
                session_id=session_id,
                candidate_info=candidate_info
            )
            
            # Initialize session state
            session_state = {
                "session_id": session_id,
                "candidate_info": candidate_info,
                "start_time": datetime.utcnow(),
                "current_phase": "introduction",
                "questions_asked": 0,
                "skill_level": "beginner",
                "responses": [],
                "performance_metrics": {
                    "correct_answers": 0,
                    "total_questions": 0,
                    "response_times": [],
                    "skill_demonstrations": []
                }
            }
            
            # Store session
            self.active_interviews[session_id] = agent
            self.session_states[session_id] = session_state
            
            logger.info(f"Started interview session: {session_id}")
            return agent
            
        except Exception as e:
            logger.error(f"Error starting interview {session_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to start interview")
    
    async def process_message(self, session_id: str, message: str) -> dict:
        """Process candidate response and generate next question"""
        try:
            agent = self.active_interviews.get(session_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Interview session not found")
            
            # Process the message through the agent
            response = await agent.process_response(message)
            
            # Update session state
            session_state = self.session_states[session_id]
            session_state["responses"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "candidate_message": message,
                "agent_response": response["message"],
                "evaluation": response.get("evaluation", {}),
                "next_action": response.get("next_action", "continue")
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for {session_id}: {str(e)}")
            return {
                "message": "I apologize, but I encountered an error. Could you please repeat your response?",
                "type": "error"
            }
    
    async def end_interview(self, session_id: str) -> dict:
        """Conclude interview and generate final report"""
        try:
            agent = self.active_interviews.get(session_id)
            session_state = self.session_states.get(session_id)
            
            if not agent or not session_state:
                raise HTTPException(status_code=404, detail="Interview session not found")
            
            # Generate comprehensive feedback report
            feedback_report = await agent.generate_final_report(session_state)
            
            # Update session with final report
            session_state["end_time"] = datetime.utcnow()
            session_state["final_report"] = feedback_report
            session_state["status"] = "completed"
            
            # Clean up active session
            del self.active_interviews[session_id]
            del self.session_states[session_id]
            
            logger.info(f"Completed interview session: {session_id}")
            return feedback_report
            
        except Exception as e:
            logger.error(f"Error ending interview {session_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to complete interview")

# Initialize orchestrator
interview_orchestrator = InterviewOrchestrator()

# REST API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main interview interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Excel Interviewer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }
            .header { margin-bottom: 30px; }
            h1 { 
                color: #333; 
                font-size: 2.5rem; 
                margin-bottom: 10px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            p { color: #666; font-size: 1.1rem; margin-bottom: 30px; }
            .start-btn { 
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white; 
                padding: 16px 32px; 
                border: none; 
                border-radius: 12px; 
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer; 
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            .start-btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            .features {
                margin-top: 40px;
                text-align: left;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            .feature {
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .feature h3 { color: #333; margin-bottom: 10px; }
            .feature p { color: #666; font-size: 0.9rem; margin: 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>AI-Powered Excel Mock Interviewer</h1>
                <p>Test your Excel skills with our intelligent interview system</p>
                <a href="http://localhost:3000" class="start-btn">Start Interview</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🤖 Intelligent AI</h3>
                    <p>Advanced conversational AI powered by Claude and GPT-4 for natural interview experience</p>
                </div>
                <div class="feature">
                    <h3>📊 Comprehensive Assessment</h3>
                    <p>Multi-dimensional evaluation across 5 Excel skill categories with detailed feedback</p>
                </div>
                <div class="feature">
                    <h3>⚡ Real-time Communication</h3>
                    <p>WebSocket-based instant feedback and natural conversation flow</p>
                </div>
                <div class="feature">
                    <h3>📈 Detailed Analytics</h3>
                    <p>Comprehensive performance reports with strengths, improvements, and recommendations</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/api/interview/start")
async def start_interview_session(candidate_info: dict):
    """Initialize a new interview session"""
    session_id = str(uuid.uuid4())
    
    try:
        agent = await interview_orchestrator.start_interview(session_id, candidate_info)
        initial_message = await agent.get_initial_greeting()
        
        return {
            "session_id": session_id,
            "message": initial_message,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Failed to start interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start interview session")

@app.post("/api/interview/{session_id}/message")
async def send_message(session_id: str, message_data: dict):
    """Send a message to the interview agent"""
    try:
        response = await interview_orchestrator.process_message(session_id, message_data["message"])
        return response
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.post("/api/interview/{session_id}/end")
async def end_interview_session(session_id: str):
    """End interview and get final report"""
    try:
        final_report = await interview_orchestrator.end_interview(session_id)
        return {
            "session_id": session_id,
            "status": "completed",
            "report": final_report
        }
    except Exception as e:
        logger.error(f"Failed to end interview {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete interview")

# WebSocket endpoint for real-time interview
@app.websocket("/ws/interview/{session_id}")
async def websocket_interview_endpoint(websocket: WebSocket, session_id: str):
    """Handle real-time interview conversation via WebSocket"""
    await connection_manager.connect(websocket, session_id)
    
    try:
        await connection_manager.send_personal_message(
            session_id,
            json.dumps({
                "type": "connection_established",
                "message": "Connected to interview session",
                "session_id": session_id
            })
        )
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                candidate_message = message_data.get("message", "")
                message_type = message_data.get("type", "response")
                
                if message_type == "start_interview":
                    candidate_info = message_data.get("candidate_info", {})
                    agent = await interview_orchestrator.start_interview(session_id, candidate_info)
                    initial_greeting = await agent.get_initial_greeting()
                    
                    response = {
                        "type": "interview_started",
                        "message": initial_greeting,
                        "session_id": session_id
                    }
                    
                elif message_type == "response":
                    agent_response = await interview_orchestrator.process_message(
                        session_id, candidate_message
                    )
                    
                    response = {
                        "type": "agent_response",
                        "message": agent_response["message"],
                        "evaluation": agent_response.get("evaluation", {}),
                        "next_action": agent_response.get("next_action", "continue"),
                        "session_id": session_id
                    }
                    
                elif message_type == "end_interview":
                    final_report = await interview_orchestrator.end_interview(session_id)
                    
                    response = {
                        "type": "interview_completed",
                        "message": "Thank you for completing the interview!",
                        "report": final_report,
                        "session_id": session_id
                    }
                
                else:
                    response = {
                        "type": "error",
                        "message": "Unknown message type",
                        "session_id": session_id
                    }
                
                await connection_manager.send_personal_message(
                    session_id,
                    json.dumps(response)
                )
                
            except json.JSONDecodeError:
                agent_response = await interview_orchestrator.process_message(session_id, data)
                
                response = {
                    "type": "agent_response",
                    "message": agent_response["message"],
                    "session_id": session_id
                }
                
                await connection_manager.send_personal_message(
                    session_id,
                    json.dumps(response)
                )
            
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                error_response = {
                    "type": "error",
                    "message": "I encountered an error processing your response. Please try again.",
                    "session_id": session_id
                }
                
                await connection_manager.send_personal_message(
                    session_id,
                    json.dumps(error_response)
                )
    
    except WebSocketDisconnect:
        logger.info(f"Client {session_id} disconnected")
        connection_manager.disconnect(session_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_interviews": len(interview_orchestrator.active_interviews)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
