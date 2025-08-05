# Signal Bot Setup Without QR Code - PowerShell Version

Write-Host "🤖 Signal Bot Setup (No QR Code Required)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is installed
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose is installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Starting Signal CLI REST API..." -ForegroundColor Yellow

# Navigate to docker directory and start services
Push-Location docker
docker-compose up -d
Pop-Location

# Wait for service to be ready
Write-Host "⏳ Waiting for Signal service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if service is running
$runningContainers = docker ps --format "table {{.Names}}"
if ($runningContainers -match "signal-api") {
    Write-Host "✅ Signal CLI REST API is running" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start Signal CLI REST API" -ForegroundColor Red
    Write-Host "💡 Try running: docker-compose up -d in the docker folder" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow

# Install Python dependencies
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some dependencies may have failed to install" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: python register_no_qr.py" -ForegroundColor White
Write-Host "2. Choose SMS or voice verification (no QR code needed!)" -ForegroundColor White
Write-Host "3. Follow the registration prompts" -ForegroundColor White
Write-Host "4. Once registered, run: python src/idle_bot.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 Registration options available:" -ForegroundColor Yellow
Write-Host "   - SMS verification (most common)" -ForegroundColor White
Write-Host "   - Voice call verification" -ForegroundColor White
Write-Host "   - REST API method" -ForegroundColor White
Write-Host ""
Write-Host "No QR code scanning required! 🎉" -ForegroundColor Green
