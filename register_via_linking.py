#!/usr/bin/env python3
"""
Signal Bot Registration via Device Linking

Since captcha registration isn't working, this script uses Signal's device linking
feature to register the bot as a linked device to your main Signal account.
"""

import subprocess
import time
import requests
import webbrowser
import json

class SignalLinkingRegistration:
    """Register bot via device linking instead of primary registration"""
    
    def __init__(self):
        self.api_base = "http://localhost:8080/v1"
    
    def run_docker_command(self, cmd):
        """Run a command in the Docker container"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return None, str(e), 1
    
    def check_service_status(self):
        """Check if signal-cli-rest-api is running"""
        try:
            response = requests.get(f"{self.api_base}/about", timeout=5)
            if response.status_code == 200:
                print("✅ Signal CLI REST API is running")
                return True
            else:
                print(f"❌ Signal service returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Signal service: {e}")
            return False
    
    def start_linking_process(self):
        """Start the device linking process"""
        print("\n📱 Starting Device Linking Process")
        print("=" * 50)
        
        print("💡 This method links your bot as a secondary device to your main Signal account.")
        print("   You'll need your phone with Signal app installed.\n")
        
        # Method 1: Try REST API linking
        print("🔄 Method 1: REST API Linking")
        try:
            response = requests.get(f"{self.api_base}/qrcodelink?device_name=idle-bot", timeout=10)
            if response.status_code == 200:
                qr_url = f"{self.api_base}/qrcodelink?device_name=idle-bot"
                print(f"✅ QR code link generated!")
                print(f"🔗 Link: {qr_url}")
                
                open_browser = input("\n🌐 Open link in browser? (y/n): ").strip().lower()
                if open_browser == 'y':
                    webbrowser.open(qr_url)
                    print("✅ Browser opened!")
                
                print("\n📱 To complete linking:")
                print("1. Open Signal app on your phone")
                print("2. Go to Settings → Linked devices")
                print("3. Tap the '+' button")
                print("4. Scan the QR code from the browser")
                
                input("\nPress Enter after scanning the QR code...")
                
                # Check if linking worked
                return self.check_linking_success()
            else:
                print(f"❌ REST API linking failed: {response.status_code}")
        except Exception as e:
            print(f"❌ REST API linking error: {e}")
        
        # Method 2: Try signal-cli linking
        print("\n🔄 Method 2: signal-cli Direct Linking")
        stdout, stderr, code = self.run_docker_command(
            'docker exec signal-api signal-cli link -n "idle-bot"'
        )
        
        if code == 0 and stdout:
            print("✅ signal-cli linking initiated!")
            print("📋 Output:")
            print(stdout)
            
            # Look for QR code data or link
            lines = stdout.split('\n')
            for line in lines:
                if 'tsdevice:' in line or 'sgnl://' in line:
                    print(f"\n🔗 QR Code Data: {line}")
                    print("\n💡 You can:")
                    print("1. Copy this data and paste in Signal app")
                    print("2. Use a QR code generator to create a scannable code")
                    break
            
            input("\nPress Enter after linking in Signal app...")
            return self.check_linking_success()
        else:
            print(f"❌ signal-cli linking failed: {stderr}")
        
        return False
    
    def check_linking_success(self):
        """Check if device linking was successful"""
        print("\n🔍 Checking linking status...")
        
        # Wait a moment for linking to complete
        time.sleep(3)
        
        # Check via REST API
        try:
            response = requests.get(f"{self.api_base}/accounts", timeout=5)
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    print("✅ Device linking successful!")
                    print(f"📱 Linked accounts: {accounts}")
                    return True
        except Exception as e:
            print(f"⚠️  API check failed: {e}")
        
        # Check via signal-cli
        stdout, stderr, code = self.run_docker_command(
            "docker exec signal-api signal-cli listAccounts"
        )
        
        if code == 0 and stdout:
            print("✅ signal-cli shows linked account!")
            print(f"📋 Accounts: {stdout}")
            return True
        
        print("❌ Linking may not have completed successfully")
        return False
    
    def alternative_linking_methods(self):
        """Show alternative linking methods"""
        print("\n🔧 Alternative Linking Methods")
        print("=" * 50)
        
        print("\n1. **Manual QR Code Generation:**")
        print("   - Run: docker exec signal-api signal-cli link -n 'idle-bot'")
        print("   - Copy the tsdevice:// URL")
        print("   - Go to: https://www.qr-code-generator.com/")
        print("   - Paste the URL and generate QR code")
        print("   - Scan with Signal app")
        
        print("\n2. **Signal Desktop Method:**")
        print("   - Install Signal Desktop from signal.org/desktop")
        print("   - Link it to your phone first")
        print("   - Then our bot can use the same linking process")
        
        print("\n3. **Direct URL Method:**")
        print("   - Some Signal apps can open sgnl:// URLs directly")
        print("   - Copy the linking URL and try opening in Signal")
        
        print("\n4. **Reset and Retry:**")
        print("   - docker-compose down")
        print("   - docker volume rm docker_signal-cli-config")
        print("   - docker-compose up -d")
        print("   - Try linking again")
    
    def test_linked_bot(self):
        """Test if the linked bot is working"""
        print("\n🧪 Testing Linked Bot")
        print("=" * 30)
        
        # Try to receive messages
        stdout, stderr, code = self.run_docker_command(
            "docker exec signal-api signal-cli receive"
        )
        
        if code == 0:
            print("✅ Bot can receive messages!")
        else:
            print(f"⚠️  Receive test: {stderr}")
        
        # Check groups
        stdout, stderr, code = self.run_docker_command(
            "docker exec signal-api signal-cli listGroups"
        )
        
        if code == 0:
            print("✅ Bot can access groups!")
            if stdout:
                print(f"📱 Groups: {stdout}")
        else:
            print(f"⚠️  Group access: {stderr}")


def main():
    """Main linking registration process"""
    print("🔗 Signal Bot Registration via Device Linking")
    print("=" * 60)
    print("\nThis method avoids the problematic captcha system by linking")
    print("your bot as a secondary device to your main Signal account.\n")
    
    registrar = SignalLinkingRegistration()
    
    # Check service
    if not registrar.check_service_status():
        print("\n❌ Cannot proceed without signal-cli-rest-api running")
        print("💡 Start with: docker-compose up -d")
        return
    
    print("\n📋 Requirements:")
    print("✓ Signal app installed on your phone")
    print("✓ Active Signal account")
    print("✓ Ability to scan QR codes")
    
    ready = input("\n❓ Do you have these requirements? (y/n): ").strip().lower()
    if ready != 'y':
        print("\n💡 Please install Signal on your phone first, then run this script again.")
        return
    
    # Start linking
    if registrar.start_linking_process():
        print("\n🎉 SUCCESS! Your bot is now linked!")
        print("\n📋 Next steps:")
        print("1. Your bot inherits your phone number")
        print("2. Add the bot to Signal groups")
        print("3. Run: python src/idle_bot.py")
        
        # Test the bot
        test = input("\n🧪 Test the linked bot now? (y/n): ").strip().lower()
        if test == 'y':
            registrar.test_linked_bot()
        
    else:
        print("\n😞 Linking didn't complete successfully.")
        print("📚 Here are some alternatives:")
        registrar.alternative_linking_methods()
        
        print("\n💡 You can also try the captcha-free registration:")
        print("   python register_without_captcha.py")


if __name__ == "__main__":
    main()
