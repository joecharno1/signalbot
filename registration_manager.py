#!/usr/bin/env python3
"""
Signal Bot Manager

A management utility for your Signal Idle User Bot that helps with registration
and provides fallback options when direct Signal registration fails.
"""

import json
import requests
import time
from datetime import datetime

class SignalRegistrationManager:
    """Manages Signal registration and provides fallback options"""
    
    def __init__(self, signal_service="127.0.0.1:8080"):
        self.signal_service = signal_service
        self.base_url = f"http://{signal_service}/v1"
    
    def check_service_status(self):
        """Check if signal-cli-rest-api is running"""
        try:
            response = requests.get(f"{self.base_url}/about", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Signal CLI REST API is running")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Mode: {data.get('mode', 'Unknown')}")
                return True
            else:
                print(f"❌ Signal service returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Signal service: {e}")
            return False
    
    def check_registered_accounts(self):
        """Check what accounts are already registered"""
        try:
            response = requests.get(f"{self.base_url}/accounts", timeout=5)
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    print(f"✅ Found {len(accounts)} registered account(s):")
                    for account in accounts:
                        print(f"   📱 {account}")
                    return accounts
                else:
                    print("ℹ️  No accounts currently registered")
                    return []
            else:
                print(f"❌ Failed to get accounts: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking accounts: {e}")
            return None
    
    def try_register_with_captcha(self, phone_number, captcha_token):
        """Attempt to register with a captcha token"""
        print(f"🔄 Attempting to register {phone_number} with captcha...")
        
        try:
            # Try REST API registration
            data = {"captcha": captcha_token}
            response = requests.post(
                f"{self.base_url}/register/{phone_number}",
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                print("✅ Registration request sent! Check for SMS verification code.")
                return True
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ Registration failed: {error_data.get('error', 'Unknown error')}")
                return False
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during registration: {e}")
            return False
    
    def verify_registration(self, phone_number, verification_code):
        """Verify registration with SMS code"""
        print(f"🔄 Verifying {phone_number} with code {verification_code}...")
        
        try:
            data = {"verificationCode": verification_code}
            response = requests.post(
                f"{self.base_url}/register/{phone_number}/verify",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Phone number successfully registered!")
                return True
            else:
                error_data = response.json()
                print(f"❌ Verification failed: {error_data.get('error', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during verification: {e}")
            return False
    
    def generate_qr_link(self):
        """Generate a QR code link for device linking"""
        try:
            response = requests.get(f"{self.base_url}/qrcodelink?device_name=idle-bot", timeout=10)
            if response.status_code == 200:
                print("✅ QR code link generated!")
                print(f"🔗 Open this link in your browser: {self.base_url}/qrcodelink?device_name=idle-bot")
                print("📱 Then scan the QR code with your Signal app:")
                print("   Settings → Linked devices → '+' → Scan QR code")
                return True
            else:
                print(f"❌ Failed to generate QR link: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error generating QR link: {e}")
            return False


def main():
    """Main registration management interface"""
    print("🤖 Signal Idle User Bot - Registration Manager")
    print("=" * 50)
    
    manager = SignalRegistrationManager()
    
    # Check service status
    if not manager.check_service_status():
        print("\n❌ Cannot proceed without signal-cli-rest-api running")
        print("💡 Make sure Docker container is running: docker-compose up -d")
        return
    
    # Check existing accounts
    print("\n🔍 Checking for existing registered accounts...")
    accounts = manager.check_registered_accounts()
    
    if accounts:
        print(f"\n✅ Great! You already have registered accounts.")
        print("🚀 Your bot should be ready to use!")
        print("\n📋 Next steps:")
        print("1. Add the bot to your Signal group")
        print("2. Make the bot an admin in the group")
        print("3. Test with: python src/idle_bot.py")
        return
    
    # No accounts registered, offer options
    print("\n🔧 No accounts registered. Choose an option:")
    print("1. Register new phone number (requires SMS access)")
    print("2. Link as secondary device (requires QR code scanning)")
    print("3. Run in demo mode (for testing)")
    
    choice = input("\nEnter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        phone = input("Enter phone number (e.g., +12035442924): ").strip()
        captcha = input("Enter captcha token from https://signalcaptchas.org/registration/generate.html: ").strip()
        
        if manager.try_register_with_captcha(phone, captcha):
            verification_code = input("Enter the SMS verification code you received: ").strip()
            if manager.verify_registration(phone, verification_code):
                print("\n🎉 Registration successful!")
                print("🚀 Your bot is now ready to use!")
            else:
                print("\n❌ Verification failed. You may need to try again.")
        else:
            print("\n❌ Registration failed. Check your captcha token and try again.")
    
    elif choice == "2":
        print("\n🔗 Generating QR code for device linking...")
        if manager.generate_qr_link():
            input("\nPress Enter after you've scanned the QR code with your Signal app...")
            
            # Check if linking worked
            time.sleep(2)
            accounts = manager.check_registered_accounts()
            if accounts:
                print("\n🎉 Device linking successful!")
                print("🚀 Your bot is now ready to use!")
            else:
                print("\n❌ Device linking may not have completed. Check your Signal app.")
        else:
            print("\n❌ Failed to generate QR link.")
    
    elif choice == "3":
        print("\n🎭 Running in demo mode...")
        print("💡 This will show you how the bot works without Signal registration.")
        print("🚀 Run: python demo_bot.py")
    
    else:
        print("\n❌ Invalid choice.")


if __name__ == "__main__":
    main()
