#!/bin/bash
# Signal Bot Setup Without QR Code

echo "🤖 Signal Bot Setup (No QR Code Required)"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker is installed"

# Start Signal CLI REST API
echo ""
echo "📦 Starting Signal CLI REST API..."
cd docker
docker-compose up -d

# Wait for service to be ready
echo "⏳ Waiting for Signal service to start..."
sleep 10

# Check if service is running
if docker ps | grep -q signal-api; then
    echo "✅ Signal CLI REST API is running"
else
    echo "❌ Failed to start Signal CLI REST API"
    exit 1
fi

cd ..

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run: python register_no_qr.py"
echo "2. Choose SMS or voice verification (no QR code needed!)"
echo "3. Follow the registration prompts"
echo "4. Once registered, run: python src/idle_bot.py"
echo ""
echo "💡 Registration options available:"
echo "   - SMS verification (most common)"
echo "   - Voice call verification"
echo "   - REST API method"
echo ""
echo "No QR code scanning required! 🎉"
