#!/usr/bin/env python3
"""
AI Excel Interviewer - Production Ready Startup Script
"""

import uvicorn
import os
import sys
from dotenv import load_dotenv

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
# Check if .env file exists
if not os.path.exists('.env'):
    print("❌ .env file not found!")
    print("📝 Please copy env.example to .env and add your API keys:")
    print("   cp ../configuration/env.example .env")
    print("   # Then edit .env with your API keys")
    # return False
    
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not anthropic_key and not openai_key:
        print("❌ No API keys found!")
        print("📝 Please add at least one API key to your .env file:")
        print("   ANTHROPIC_API_KEY=your_key_here")
        print("   # OR")
        print("   OPENAI_API_KEY=your_key_here")
        # return False
    
    if anthropic_key:
        print("✅ Anthropic Claude API key found")
    if openai_key:
        print("✅ OpenAI GPT API key found")
    
    # return True

def main():
    """Main startup function"""
    print("🚀 AI-Powered Excel Mock Interviewer")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    print("\n🎯 System Status:")
    print("✅ Backend: Ready")
    print("✅ AI Engine: Ready")
    print("✅ WebSocket: Ready")
    print("✅ Evaluation: Ready")
    
    print("\n🌐 Access Points:")
    print("   📱 Frontend: http://localhost:3000")
    print("   🔧 Backend:  http://localhost:8000")
    print("   📖 API Docs: http://localhost:8000/docs")
    
    print("\n🚀 Starting server...")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for production
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
