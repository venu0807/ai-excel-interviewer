#!/bin/bash

# AI Excel Interviewer - Production Deployment Script
# This script sets up and deploys the complete solution

echo "🚀 AI-Powered Excel Mock Interviewer - Deployment Script"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp ../configuration/env.example .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - ANTHROPIC_API_KEY=your_anthropic_key_here"
    echo "   - OPENAI_API_KEY=your_openai_key_here"
    echo ""
    echo "Press Enter when you've added your API keys..."
    read
fi

echo "✅ Environment configuration ready"

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Test backend health
echo "🏥 Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "📋 Check logs: docker-compose logs backend"
fi

# Display access information
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "🚀 Ready to conduct AI-powered Excel interviews!"
