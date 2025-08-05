#!/usr/bin/env python3
"""
Signal Bot Registration Without QR Code

This script helps you register your bot's phone number with Signal
using SMS or voice verification instead of QR code scanning.
"""

import subprocess
import sys
import time
import re
import requests
import json

class NoQRRegistration:
    """Handles Signal registration without QR codes"""
    
    def __init__(self, phone_number="+13045641145"):
        self.phone_number = phone_number
        self.api_base = "http://localhost:8080/v1"
        self.captcha_url = "https://signalcaptchas.org/challenge/generate.html"
        
    def run_docker_command(self, cmd):
        """Run a command in the Docker container"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return None, str(e), 1
    
    def check_docker_status(self):
        """Check if Signal API container is running"""
        print("🔍 Checking Docker container status...")
        stdout, stderr, code = self.run_docker_command("docker ps --filter name=signal-api --format \"{{.Names}} {{.Status}}\"")
        
        if code == 0 and "signal-api" in (stdout or ""):
            print("✅ Signal API container is running")
            return True
        else:
            print("❌ Signal API container is not running")
            print("💡 Start it with: docker-compose up -d")
            return False
    
    def check_existing_registration(self):
        """Check if phone number is already registered"""
        print(f"\n🔍 Checking if {self.phone_number} is already registered...")
        
        try:
            response = requests.get(f"{self.api_base}/accounts", timeout=5)
            if response.status_code == 200:
                accounts = response.json()
                if self.phone_number in accounts:
                    print(f"✅ {self.phone_number} is already registered!")
                    return True
                else:
                    print(f"ℹ️  {self.phone_number} is not registered yet")
                    return False
        except Exception as e:
            print(f"⚠️  Could not check registration status: {e}")
            return False
    
    def extract_captcha_token(self, input_string):
        """Extract captcha token from various input formats"""
        # Try to extract UUID pattern
        patterns = [
            r'signal-captcha[s]?://.*?([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            r'signal-hcaptcha\.([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, input_string)
            if match:
                return match.group(1)
        
        return None
    
    def register_with_sms(self):
        """Register using SMS verification"""
        print("\n📱 SMS Registration Method")
        print("=" * 40)
        
        # Step 1: Get captcha
        print(f"\n📝 Step 1: Get a captcha token")
        print(f"🔗 Visit: {self.captcha_url}")
        print("1. Solve the captcha completely")
        print("2. Right-click on 'Open Signal' button")
        print("3. Select 'Copy link address'")
        print("4. Paste the FULL URL here")
        
        captcha_input = input("\n📋 Paste captcha URL or token: ").strip()
        captcha_token = self.extract_captcha_token(captcha_input)
        
        if not captcha_token:
            print("⚠️  Could not extract captcha token automatically")
            print("💡 The token looks like: 5fad97ac-7d06-4e44-b18a-b950b20148ff")
            captcha_token = input("📋 Enter just the captcha token: ").strip()
        
        print(f"\n✅ Using captcha token: {captcha_token}")
        
        # Step 2: Request SMS verification
        print(f"\n📝 Step 2: Requesting SMS verification for {self.phone_number}...")
        cmd = f'docker exec signal-api signal-cli -a {self.phone_number} register --captcha "{captcha_token}"'
        stdout, stderr, code = self.run_docker_command(cmd)
        
        if code == 0 or "SMS" in (stdout or "") or "voice" in (stdout or ""):
            print("✅ SMS verification requested!")
            print("📱 You should receive an SMS with a 6-digit code")
            
            # Step 3: Enter verification code
            print("\n📝 Step 3: Enter verification code")
            sms_code = input("📋 Enter the 6-digit SMS code: ").strip()
            
            print(f"\n🔄 Verifying with code {sms_code}...")
            cmd = f"docker exec signal-api signal-cli -a {self.phone_number} verify {sms_code}"
            stdout, stderr, code = self.run_docker_command(cmd)
            
            if code == 0:
                print("✅ Phone number successfully verified!")
                return True
            else:
                print(f"❌ Verification failed: {stderr}")
                return False
        else:
            print(f"❌ SMS request failed: {stderr}")
            print("\n💡 Common issues:")
            print("- Captcha token expired (get a fresh one)")
            print("- Phone number format issue")
            print("- Rate limiting (wait a few minutes)")
            return False
    
    def register_with_voice(self):
        """Register using voice call verification"""
        print("\n☎️  Voice Call Registration Method")
        print("=" * 40)
        
        # Step 1: Get captcha
        print(f"\n📝 Step 1: Get a captcha token")
        print(f"🔗 Visit: {self.captcha_url}")
        print("Follow the same steps as SMS registration to get a captcha token")
        
        captcha_input = input("\n📋 Paste captcha URL or token: ").strip()
        captcha_token = self.extract_captcha_token(captcha_input)
        
        if not captcha_token:
            captcha_token = input("📋 Enter just the captcha token: ").strip()
        
        print(f"\n✅ Using captcha token: {captcha_token}")
        
        # Step 2: Request voice verification
        print(f"\n📝 Step 2: Requesting voice call verification for {self.phone_number}...")
        cmd = f'docker exec signal-api signal-cli -a {self.phone_number} register --voice --captcha "{captcha_token}"'
        stdout, stderr, code = self.run_docker_command(cmd)
        
        if code == 0 or "voice" in (stdout or "").lower():
            print("✅ Voice call requested!")
            print("☎️  You should receive a phone call with a 6-digit code")
            print("💡 Listen carefully and write down the code")
            
            # Step 3: Enter verification code
            print("\n📝 Step 3: Enter verification code from voice call")
            voice_code = input("📋 Enter the 6-digit code from the call: ").strip()
            
            print(f"\n🔄 Verifying with code {voice_code}...")
            cmd = f"docker exec signal-api signal-cli -a {self.phone_number} verify {voice_code}"
            stdout, stderr, code = self.run_docker_command(cmd)
            
            if code == 0:
                print("✅ Phone number successfully verified!")
                return True
            else:
                print(f"❌ Verification failed: {stderr}")
                return False
        else:
            print(f"❌ Voice call request failed: {stderr}")
            return False
    
    def register_with_rest_api(self):
        """Register using REST API directly"""
        print("\n🌐 REST API Registration Method")
        print("=" * 40)
        
        # Get captcha
        print(f"\n📝 Get a captcha token from: {self.captcha_url}")
        captcha_input = input("\n📋 Paste captcha URL or token: ").strip()
        captcha_token = self.extract_captcha_token(captcha_input)
        
        if not captcha_token:
            captcha_token = input("📋 Enter just the captcha token: ").strip()
        
        print(f"\n🔄 Registering {self.phone_number} via REST API...")
        
        try:
            # Request registration
            data = {"captcha": captcha_token, "use_voice": False}
            response = requests.post(
                f"{self.api_base}/register/{self.phone_number}",
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print("✅ Registration requested! Check for SMS/voice verification")
                
                # Get verification code
                verify_code = input("\n📋 Enter the verification code: ").strip()
                
                # Verify
                verify_data = {"verificationCode": verify_code}
                verify_response = requests.post(
                    f"{self.api_base}/register/{self.phone_number}/verify",
                    json=verify_data,
                    timeout=30
                )
                
                if verify_response.status_code == 200:
                    print("✅ Successfully registered!")
                    return True
                else:
                    print(f"❌ Verification failed: {verify_response.text}")
                    return False
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ REST API error: {e}")
            return False
    
    def show_success_message(self):
        """Show success message and next steps"""
        print("\n" + "🎉" * 10)
        print("🎉 SUCCESS! Your Signal bot is registered!")
        print("🎉" * 10)
        
        print(f"\n✅ Registered number: {self.phone_number}")
        print("\n📋 Next steps:")
        print("1. Add the bot to your Signal group")
        print("2. Make the bot an admin (required for removing users)")
        print("3. Run the bot: python src/idle_bot.py")
        print("\n💡 Bot commands:")
        print("  !help  - Show all commands")
        print("  !stats - View activity statistics")
        print("  !idle  - Check for idle users")


def main():
    """Main registration interface"""
    print("🤖 Signal Bot Registration (No QR Code)")
    print("=" * 50)
    
    # Get phone number
    default_phone = "+13045641145"
    print(f"\n📱 Default phone number: {default_phone}")
    custom_phone = input("Press Enter to use default, or enter a different number: ").strip()
    phone_number = custom_phone if custom_phone else default_phone
    
    registrar = NoQRRegistration(phone_number)
    
    # Check Docker
    if not registrar.check_docker_status():
        return
    
    # Check if already registered
    if registrar.check_existing_registration():
        registrar.show_success_message()
        return
    
    # Show registration options
    print("\n🔧 Registration Options (No QR Code Required):")
    print("1. SMS verification (most common)")
    print("2. Voice call verification")
    print("3. REST API method (advanced)")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            if registrar.register_with_sms():
                registrar.show_success_message()
                break
            else:
                print("\n💡 Try again or choose a different method")
        
        elif choice == "2":
            if registrar.register_with_voice():
                registrar.show_success_message()
                break
            else:
                print("\n💡 Try again or choose a different method")
        
        elif choice == "3":
            if registrar.register_with_rest_api():
                registrar.show_success_message()
                break
            else:
                print("\n💡 Try again or choose a different method")
        
        elif choice == "4":
            print("\n👋 Exiting...")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-4")


if __name__ == "__main__":
    main()
