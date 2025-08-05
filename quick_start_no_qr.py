#!/usr/bin/env python3
"""
Quick Start Script - Signal Bot with No QR Code

This script combines setup and registration into one easy process.
No QR code scanning required!
"""

import subprocess
import time
import os
import sys
import requests

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*60)
    print("🤖 Signal Bot Quick Start - No QR Code Required!")
    print("="*60 + "\n")

def check_docker():
    """Check if Docker is installed and running"""
    print("🔍 Checking Docker installation...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker is installed: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker daemon is running")
                return True
            else:
                print("❌ Docker daemon is not running")
                print("💡 Please start Docker Desktop")
                return False
        else:
            print("❌ Docker is not installed")
            print("💡 Please install Docker Desktop from https://docker.com")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def start_signal_service():
    """Start Signal CLI REST API"""
    print("\n📦 Starting Signal CLI REST API...")
    
    # Change to docker directory
    docker_dir = os.path.join(os.path.dirname(__file__), "docker")
    os.chdir(docker_dir)
    
    # Run docker-compose
    result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Signal service starting...")
        
        # Wait for service to be ready
        print("⏳ Waiting for service to initialize (10 seconds)...")
        time.sleep(10)
        
        # Check if service is responding
        try:
            response = requests.get("http://localhost:8080/v1/about", timeout=5)
            if response.status_code == 200:
                print("✅ Signal CLI REST API is ready!")
                return True
        except:
            pass
        
        print("⚠️  Service may still be starting. Continuing anyway...")
        return True
    else:
        print(f"❌ Failed to start service: {result.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    # Change back to root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("⚠️  Some dependencies may have failed to install")
        print("💡 You can install them manually with: pip install -r requirements.txt")
        return True  # Continue anyway

def run_registration():
    """Run the no-QR registration process"""
    print("\n🚀 Starting registration process...")
    print("="*60)
    
    # Import and run the registration
    try:
        import register_no_qr
        register_no_qr.main()
    except ImportError:
        # If import fails, run as subprocess
        subprocess.run([sys.executable, "register_no_qr.py"])

def main():
    """Main quick start process"""
    print_banner()
    
    # Step 1: Check Docker
    if not check_docker():
        print("\n❌ Cannot proceed without Docker. Please install Docker Desktop first.")
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Start Signal service
    if not start_signal_service():
        print("\n❌ Failed to start Signal service.")
        print("💡 Try running manually: cd docker && docker-compose up -d")
        input("\nPress Enter to exit...")
        return
    
    # Step 3: Install dependencies
    install_dependencies()
    
    # Step 4: Run registration
    print("\n" + "="*60)
    print("🎯 Ready to register your Signal bot!")
    print("="*60)
    print("\n📋 You will need:")
    print("1. A phone number that can receive SMS or calls")
    print("2. Access to https://signalcaptchas.org/registration/generate.html")
    print("3. About 5 minutes")
    print("\n✨ No QR code scanning required!")
    
    input("\nPress Enter to start registration...")
    
    run_registration()
    
    print("\n" + "="*60)
    print("🏁 Quick start complete!")
    print("="*60)
    print("\nIf registration was successful, you can now:")
    print("1. Configure your bot: edit config/bot_config.yaml")
    print("2. Run your bot: python src/idle_bot.py")
    print("\n💡 Need help? Check docs/NO_QR_REGISTRATION_GUIDE.md")

if __name__ == "__main__":
    main()
