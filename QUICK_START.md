# 🚀 Quick Start Guide

## AI-Powered Excel Mock Interviewer

### 📋 Prerequisites
- Docker and Docker Compose installed
- API key for Anthropic Claude or OpenAI GPT

### ⚡ 3-Step Deployment

#### 1. Setup Environment
```bash
# Copy environment template
cp configuration/env.example .env

# Edit .env file and add your API keys
# ANTHROPIC_API_KEY=your_anthropic_key_here
# OPENAI_API_KEY=your_openai_key_here
```

#### 2. Deploy Application
```bash
# Navigate to deployment folder
cd deployment

# Start the application
docker-compose up -d
```

#### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs

### 🎯 That's It!

Your AI-Powered Excel Mock Interviewer is now running and ready to conduct intelligent Excel proficiency interviews!

### 📚 Need Help?

- **Detailed Setup**: See [documentation/README.md](documentation/README.md)
- **Architecture**: See [documentation/DESIGN_DOCUMENT.md](documentation/DESIGN_DOCUMENT.md)
- **Deployment**: See [documentation/DEPLOYMENT_GUIDE.md](documentation/DEPLOYMENT_GUIDE.md)
- **Sample Interview**: See [documentation/SAMPLE_TRANSCRIPT.md](documentation/SAMPLE_TRANSCRIPT.md)

### 🔧 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services  
docker-compose down

# Restart services
docker-compose restart

# Check status
docker-compose ps
```

---

**Ready to revolutionize Excel skill assessment!** 🎉
