@echo off
REM AI Excel Interviewer - Windows Deployment Script

echo 🚀 AI-Powered Excel Mock Interviewer - Windows Deployment
echo ========================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy ..\configuration\env.example .env
    echo ⚠️  Please edit .env file and add your API keys:
    echo    - ANTHROPIC_API_KEY=your_anthropic_key_here
    echo    - OPENAI_API_KEY=your_openai_key_here
    echo.
    echo Press Enter when you've added your API keys...
    pause
)

echo ✅ Environment configuration ready

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose ps

REM Test backend health
echo 🏥 Testing backend health...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is healthy
) else (
    echo ❌ Backend health check failed
    echo 📋 Check logs: docker-compose logs backend
)

REM Display access information
echo.
echo 🎉 Deployment Complete!
echo ======================
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo 📋 Useful Commands:
echo    View logs:     docker-compose logs -f
echo    Stop services: docker-compose down
echo    Restart:       docker-compose restart
echo.
echo 🚀 Ready to conduct AI-powered Excel interviews!
pause
