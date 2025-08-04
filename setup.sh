#!/bin/bash

# Signal Idle User Bot Setup Script

set -e

echo "🤖 Signal Idle User Bot Setup"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p docker/signal-cli-config

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding!"
fi

# Install Python dependencies (for local development)
if command -v python3 &> /dev/null; then
    echo "🐍 Installing Python dependencies..."
    python3 -m pip install -r requirements.txt
else
    echo "⚠️  Python3 not found. Skipping local Python setup."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your phone number and admin numbers"
echo "2. Edit config/bot_config.yaml with your settings"
echo "3. Start signal-cli-rest-api: cd docker && docker-compose up -d"
echo "4. Register your bot's phone number (see docs/SETUP.md)"
echo "5. Run the bot: python3 src/idle_bot.py"
echo ""
echo "For detailed instructions, see docs/SETUP.md"

