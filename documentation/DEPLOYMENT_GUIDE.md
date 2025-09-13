# Deployment Guide - AI Excel Interviewer

## 🚀 Quick Deployment

### Option 1: Docker Compose (Recommended)

1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd ai-excel-interviewer
cp env.example .env
```

2. **Configure Environment**
Edit `.env` file with your API keys:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Access Application**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Backend Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here

# Start server
python start_server.py
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes* | Anthropic Claude API key |
| `OPENAI_API_KEY` | Yes* | OpenAI GPT API key |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Debug mode (default: false) |

*At least one LLM API key is required

### API Keys Setup

#### Anthropic Claude (Recommended)
1. Visit: https://console.anthropic.com/
2. Create account and get API key
3. Add to `.env` file: `ANTHROPIC_API_KEY=your_key_here`

#### OpenAI GPT (Alternative/Backup)
1. Visit: https://platform.openai.com/api-keys
2. Create account and get API key
3. Add to `.env` file: `OPENAI_API_KEY=your_key_here`

## 📊 Monitoring

### Health Checks
```bash
# Check server health
curl http://localhost:8000/health

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### Performance Monitoring
- Response time: <2 seconds per interaction
- Concurrent users: 100+ supported
- Memory usage: ~200MB per instance
- CPU usage: Low for typical load

## 🔒 Security Considerations

### Production Deployment
1. **Use HTTPS**: Enable SSL/TLS certificates
2. **Environment Variables**: Never commit API keys to version control
3. **Rate Limiting**: Configure appropriate rate limits
4. **Firewall**: Restrict access to necessary ports only
5. **Updates**: Keep dependencies updated regularly

### Security Checklist
- [ ] API keys stored securely
- [ ] HTTPS enabled
- [ ] CORS configured properly
- [ ] Input validation enabled
- [ ] Error messages don't leak sensitive info
- [ ] Regular security updates

## 🐛 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if port is in use
netstat -tulpn | grep :8000

# Kill process if needed
sudo kill -9 $(lsof -t -i:8000)
```

#### API Key Issues
```bash
# Test API key
python -c "import os; print('Key set:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

#### Frontend Connection Issues
- Check backend is running on port 8000
- Verify CORS settings
- Check browser console for errors

#### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Logs and Debugging
```bash
# View application logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend

# Debug mode
DEBUG=true python start_server.py
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Use load balancer (nginx example)
# Configure nginx.conf for load balancing
```

### Performance Optimization
- Enable response caching
- Use Redis for session storage
- Implement database connection pooling
- Configure CDN for static assets

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Strategy
- Regular database backups (if using persistent storage)
- Configuration file backups
- API key backups (secure storage)

## 📞 Support

### Getting Help
1. Check the [README.md](README.md) for basic setup
2. Review the [Design Document](DESIGN_DOCUMENT.md) for architecture
3. Check [troubleshooting section](#-troubleshooting)
4. Create an issue in the repository

### Performance Issues
- Monitor resource usage: `docker stats`
- Check response times: `curl -w "@curl-format.txt" http://localhost:8000/health`
- Review application logs for errors

---

**Need help?** Check the troubleshooting section or create an issue in the repository.
