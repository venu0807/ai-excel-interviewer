import React, { useState, useEffect } from 'react';
import { MessageCircle, Send, User, Bot, FileText, CheckCircle } from 'lucide-react';
import './App.css';
import ReactDOM from "react-dom/client";

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'question' | 'feedback' | 'conclusion';
}

interface InterviewReport {
  interview_summary: {
    total_questions: number;
    correct_answers: number;
    success_rate: number;
    overall_performance: string;
    skill_level_assessed: string;
  };
  strengths: string[];
  areas_for_improvement: string[];
  recommendations: string[];
  detailed_feedback: Array<{
    question: string;
    candidate_response: string;
    score: number;
    feedback: string;
    skill_category: string;
  }>;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewCompleted, setInterviewCompleted] = useState(false);
  const [finalReport, setFinalReport] = useState<InterviewReport | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [candidateInfo, setCandidateInfo] = useState({
    name: '',
    experience: '',
    level: 'beginner'
  });

  const addMessage = (text: string, sender: 'user' | 'bot', type?: 'question' | 'feedback' | 'conclusion') => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date(),
      type
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const connectWebSocket = () => {
    // Get the current host and protocol
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = process.env.NODE_ENV === 'production' ? window.location.host : 'localhost:8000';
      const wsUrl = `${protocol}//${host}/ws/interview/${Date.now()}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
      setIsConnected(true);
      setWs(websocket);
      console.log('Connected to interview session');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'connection_established') {
          console.log('Connection established');
        } else if (data.type === 'interview_started') {
          setInterviewStarted(true);
          addMessage(data.message, 'bot', 'question');
        } else if (data.type === 'agent_response') {
          const messageType = data.evaluation ? 'feedback' : 'question';
          addMessage(data.message, 'bot', messageType);
          
          if (data.next_action === 'conclusion') {
            setInterviewCompleted(true);
          }
        } else if (data.type === 'interview_completed') {
          setInterviewCompleted(true);
          setFinalReport(data.report);
          addMessage(data.message, 'bot', 'conclusion');
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from interview session');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const startInterview = () => {
    if (ws && isConnected) {
      const message = {
        type: 'start_interview',
        candidate_info: candidateInfo,
        message: `Hello! My name is ${candidateInfo.name}. I have ${candidateInfo.experience} of Excel experience and consider myself at a ${candidateInfo.level} level.`
      };
      ws.send(JSON.stringify(message));
    }
  };

  const sendMessage = () => {
    if (inputMessage.trim() && ws && isConnected) {
      const message = {
        type: 'response',
        message: inputMessage
      };
      ws.send(JSON.stringify(message));
      addMessage(inputMessage, 'user');
      setInputMessage('');
    }
  };

  const endInterview = () => {
    if (ws && isConnected) {
      const message = {
        type: 'end_interview'
      };
      ws.send(JSON.stringify(message));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  if (!interviewStarted && !interviewCompleted) {
    return (
      <div className="app">
        <div className="welcome-screen">
          <div className="welcome-card">
            <div className="welcome-header">
              <FileText className="welcome-icon" />
              <h1>AI-Powered Excel Mock Interviewer</h1>
              <p>Test your Excel skills with our intelligent interview system</p>
            </div>
            
            <div className="candidate-form">
              <h3>Let's get started!</h3>
              
              <div className="form-group">
                <label>Your Name:</label>
                <input
                  type="text"
                  value={candidateInfo.name}
                  onChange={(e) => setCandidateInfo(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter your name"
                />
              </div>
              
              <div className="form-group">
                <label>Excel Experience:</label>
                <select
                  value={candidateInfo.experience}
                  onChange={(e) => setCandidateInfo(prev => ({ ...prev, experience: e.target.value }))}
                >
                  <option value="">Select experience level</option>
                  <option value="Less than 1 year">Less than 1 year</option>
                  <option value="1-3 years">1-3 years</option>
                  <option value="3-5 years">3-5 years</option>
                  <option value="5+ years">5+ years</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Skill Level:</label>
                <select
                  value={candidateInfo.level}
                  onChange={(e) => setCandidateInfo(prev => ({ ...prev, level: e.target.value }))}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
              
              <button 
                className="start-button"
                onClick={startInterview}
                disabled={!candidateInfo.name || !candidateInfo.experience || !isConnected}
              >
                {isConnected ? 'Start Interview' : 'Connecting...'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (interviewCompleted && finalReport) {
    return (
      <div className="app">
        <div className="report-screen">
          <div className="report-header">
            <CheckCircle className="report-icon" />
            <h1>Interview Complete!</h1>
            <p>Here's your detailed performance report</p>
          </div>
          
          <div className="report-content">
            <div className="summary-card">
              <h3>Overall Performance</h3>
              <div className="metrics">
                <div className="metric">
                  <span className="metric-label">Questions Answered:</span>
                  <span className="metric-value">{finalReport.interview_summary.total_questions}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Success Rate:</span>
                  <span className="metric-value">{finalReport.interview_summary.success_rate}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Performance Level:</span>
                  <span className="metric-value">{finalReport.interview_summary.overall_performance}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Skill Level Assessed:</span>
                  <span className="metric-value">{finalReport.interview_summary.skill_level_assessed}</span>
                </div>
              </div>
            </div>
            
            <div className="strengths-card">
              <h3>Strengths</h3>
              <ul>
                {finalReport.strengths.map((strength, index) => (
                  <li key={index}>{strength}</li>
                ))}
              </ul>
            </div>
            
            <div className="improvement-card">
              <h3>Areas for Improvement</h3>
              <ul>
                {finalReport.areas_for_improvement.map((area, index) => (
                  <li key={index}>{area}</li>
                ))}
              </ul>
            </div>
            
            <div className="recommendations-card">
              <h3>Recommendations</h3>
              <ul>
                {finalReport.recommendations.map((recommendation, index) => (
                  <li key={index}>{recommendation}</li>
                ))}
              </ul>
            </div>
          </div>
          
          <button className="restart-button" onClick={() => window.location.reload()}>
            Take Another Interview
          </button>
        </div>
        </div>
    );
}

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <MessageCircle className="chat-icon" />
          <div className="header-info">
            <h2>Excel Mock Interview</h2>
            <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          {interviewStarted && !interviewCompleted && (
            <button className="end-button" onClick={endInterview}>
              End Interview
            </button>
          )}
        </div>
        
        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-avatar">
                {message.sender === 'user' ? <User /> : <Bot />}
              </div>
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {!interviewCompleted && (
          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your answer here..."
              rows={3}
              disabled={!isConnected}
            />
            <button 
              className="send-button"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || !isConnected}
            >
              <Send />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;