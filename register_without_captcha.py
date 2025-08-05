#!/usr/bin/env python3
"""
Signal Bot Registration WITHOUT Captcha

This script tries multiple methods to register without using the problematic captcha system.
"""

import subprocess
import sys
import time
import requests
import json
import os

class CaptchaFreeRegistration:
    """Register Signal bot without captcha"""
    
    def __init__(self, phone_number="+13045641145"):
        self.phone_number = phone_number
        self.api_base = "http://localhost:8080/v1"
    
    def run_docker_command(self, cmd):
        """Run a command in the Docker container"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return None, str(e), 1
    
    def check_existing_registration(self):
        """Check if already registered"""
        print("🔍 Checking for existing registrations...")
        
        try:
            response = requests.get(f"{self.api_base}/accounts", timeout=5)
            if response.status_code == 200:
                accounts = response.json()
                if accounts and self.phone_number in accounts:
                    print(f"✅ {self.phone_number} is already registered!")
                    return True
        except Exception as e:
            print(f"⚠️  API check failed: {e}")
        
        # Also check via signal-cli directly
        stdout, stderr, code = self.run_docker_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} listAccounts"
        )
        if code == 0 and self.phone_number in (stdout or ""):
            print(f"✅ {self.phone_number} found in signal-cli accounts!")
            return True
        
        return False
    
    def try_direct_registration(self):
        """Try registration without captcha first"""
        print(f"\n📝 Method 1: Direct registration (no captcha)")
        print("=" * 50)
        
        stdout, stderr, code = self.run_docker_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} register"
        )
        
        print(f"Command output: {stdout}")
        print(f"Error output: {stderr}")
        
        if "SMS" in (stdout or "") or "voice" in (stdout or ""):
            print("✅ Registration initiated without captcha!")
            return self.handle_verification()
        
        return False
    
    def try_voice_registration(self):
        """Try voice call registration"""
        print(f"\n📝 Method 2: Voice call registration")
        print("=" * 50)
        
        stdout, stderr, code = self.run_docker_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} register --voice"
        )
        
        print(f"Command output: {stdout}")
        print(f"Error output: {stderr}")
        
        if "voice" in (stdout or "").lower() or code == 0:
            print("✅ Voice call requested!")
            return self.handle_verification()
        
        return False
    
    def try_rest_api_direct(self):
        """Try REST API without captcha"""
        print(f"\n📝 Method 3: REST API direct registration")
        print("=" * 50)
        
        try:
            # Try without captcha first
            response = requests.post(
                f"{self.api_base}/register/{self.phone_number}",
                json={},
                timeout=30
            )
            
            print(f"API Response: {response.status_code}")
            print(f"API Body: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ REST API registration successful!")
                return self.handle_verification()
            elif response.status_code == 400:
                # Try with voice
                response = requests.post(
                    f"{self.api_base}/register/{self.phone_number}",
                    json={"use_voice": True},
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    print("✅ Voice registration via API successful!")
                    return self.handle_verification()
        
        except Exception as e:
            print(f"❌ REST API error: {e}")
        
        return False
    
    def try_signal_cli_with_config(self):
        """Try using signal-cli with pre-configured settings"""
        print(f"\n📝 Method 4: signal-cli with manual config")
        print("=" * 50)
        
        # Try to initialize the account first
        stdout, stderr, code = self.run_docker_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} --verbose register"
        )
        
        print(f"Verbose output: {stdout}")
        print(f"Verbose error: {stderr}")
        
        # Look for any indication of what's needed
        if stdout or stderr:
            combined_output = (stdout or "") + (stderr or "")
            if "UUID" in combined_output or "token" in combined_output.lower():
                print("⚠️  Still requires captcha/token")
                return False
            elif "SMS" in combined_output or "verification" in combined_output.lower():
                print("✅ May have initiated registration!")
                return self.handle_verification()
        
        return False
    
    def try_existing_session(self):
        """Check if there's an existing session we can use"""
        print(f"\n📝 Method 5: Check for existing session")
        print("=" * 50)
        
        # Check signal-cli data directory
        stdout, stderr, code = self.run_docker_command(
            "docker exec signal-api ls -la /home/.local/share/signal-cli/data/"
        )
        
        if code == 0 and stdout:
            print("📁 Signal-cli data directory contents:")
            print(stdout)
            
            # Look for our phone number
            if self.phone_number.replace("+", "") in stdout:
                print(f"✅ Found data for {self.phone_number}!")
                
                # Try to use existing registration
                stdout, stderr, code = self.run_docker_command(
                    f"docker exec signal-api signal-cli -a {self.phone_number} receive"
                )
                
                if code == 0:
                    print("✅ Account appears to be functional!")
                    return True
        
        return False
    
    def handle_verification(self):
        """Handle SMS/voice verification"""
        print("\n📱 Verification Step")
        print("=" * 30)
        
        verification_code = input("📋 Enter the verification code (SMS or voice): ").strip()
        
        if not verification_code:
            print("❌ No verification code entered")
            return False
        
        print(f"🔄 Verifying with code: {verification_code}")
        
        stdout, stderr, code = self.run_docker_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} verify {verification_code}"
        )
        
        if code == 0:
            print("✅ Verification successful!")
            
            # Confirm registration
            time.sleep(2)
            if self.check_existing_registration():
                return True
        else:
            print(f"❌ Verification failed: {stderr}")
        
        return False
    
    def manual_alternative(self):
        """Provide manual alternative steps"""
        print(f"\n🛠️  Manual Alternative Method")
        print("=" * 50)
        
        print("\n💡 If all automated methods fail, try this:")
        print("\n1. **Use Signal Desktop:**")
        print("   - Download Signal Desktop from signal.org/desktop")
        print("   - Link it to your main Signal account")
        print("   - This creates a linked device")
        
        print("\n2. **Use signal-cli linking:**")
        print("   - Run: docker exec signal-api signal-cli link -n 'idle-bot'")
        print("   - This generates a QR code URL")
        print("   - Open the URL in browser and scan with Signal app")
        
        print("\n3. **Try different phone number:**")
        print("   - Google Voice: voice.google.com (free US number)")
        print("   - TextNow: textnow.com (free US/Canada)")
        print("   - Use a different virtual number service")
        
        print("\n4. **Docker reset:**")
        print("   - docker-compose down")
        print("   - docker volume rm docker_signal-cli-config")
        print("   - docker-compose up -d")
        print("   - Try registration again")


def main():
    """Main registration without captcha"""
    print("🚫 Signal Registration WITHOUT Captcha")
    print("=" * 60)
    print("\nThis script tries multiple methods to avoid the problematic captcha system.\n")
    
    registrar = CaptchaFreeRegistration()
    
    # Check if already registered
    if registrar.check_existing_registration():
        print("\n🎉 Great! You're already registered!")
        print("🚀 Run: python src/idle_bot.py")
        return
    
    print(f"\n📱 Attempting to register: {registrar.phone_number}")
    print("🔄 Trying multiple methods...")
    
    methods = [
        ("Direct Registration", registrar.try_direct_registration),
        ("Voice Registration", registrar.try_voice_registration),
        ("REST API Direct", registrar.try_rest_api_direct),
        ("signal-cli Verbose", registrar.try_signal_cli_with_config),
        ("Existing Session", registrar.try_existing_session),
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Trying: {method_name}")
        
        try:
            if method_func():
                print(f"\n🎉 SUCCESS with {method_name}!")
                print("✅ Your Signal bot is registered and ready!")
                print("\n📋 Next steps:")
                print("1. Add the bot to your Signal group")
                print("2. Make the bot an admin")
                print("3. Run: python src/idle_bot.py")
                return
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
        
        print(f"❌ {method_name} didn't work, trying next method...")
    
    # If all methods fail
    print("\n😞 All automated methods failed.")
    print("📚 Showing manual alternatives...")
    registrar.manual_alternative()


if __name__ == "__main__":
    main()
