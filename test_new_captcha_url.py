#!/usr/bin/env python3
"""
Test New Captcha URL

This script tests the updated captcha URL and walks through the registration process.
"""

import subprocess
import requests
import webbrowser
import re
import time

class NewCaptchaTest:
    """Test the new captcha URL and registration process"""
    
    def __init__(self, phone_number="+13045641145"):
        self.phone_number = phone_number
        self.captcha_url = "https://signalcaptchas.org/challenge/generate.html"
        self.old_captcha_url = "https://signalcaptchas.org/registration/generate.html"
    
    def run_command(self, cmd):
        """Run a command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return None, str(e), 1
    
    def test_captcha_urls(self):
        """Test both old and new captcha URLs"""
        print("🔍 Testing Captcha URLs...")
        print("=" * 50)
        
        urls_to_test = [
            ("New URL", self.captcha_url),
            ("Old URL", self.old_captcha_url),
            ("Alternative 1", "https://signalcaptchas.org/registration/challenge.html"),
            ("Alternative 2", "https://signalcaptchas.org/captcha/generate.html"),
        ]
        
        working_urls = []
        
        for name, url in urls_to_test:
            print(f"\n📝 Testing {name}: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ URL is accessible")
                    
                    # Check content
                    content = response.text.lower()
                    if "captcha" in content:
                        print("   ✅ Contains captcha content")
                        
                        if "hcaptcha" in content:
                            print("   ✅ Uses hCaptcha")
                        elif "recaptcha" in content:
                            print("   ✅ Uses reCaptcha")
                        
                        if "signal" in content:
                            print("   ✅ Signal-related content found")
                            working_urls.append((name, url))
                        else:
                            print("   ⚠️  No Signal content found")
                    else:
                        print("   ❌ No captcha content found")
                elif response.status_code == 404:
                    print("   ❌ URL not found (404)")
                else:
                    print(f"   ❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error accessing URL: {e}")
        
        return working_urls
    
    def test_registration_flow(self):
        """Test the full registration flow"""
        print(f"\n🔍 Testing Registration Flow...")
        print("=" * 50)
        
        print(f"📱 Testing registration for: {self.phone_number}")
        
        # Step 1: Try registration
        stdout, stderr, code = self.run_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} register"
        )
        
        combined_output = (stdout or "") + (stderr or "")
        print(f"\nRegistration output:")
        print(f"Exit code: {code}")
        print(f"Output: {combined_output}")
        
        if "Captcha required" in combined_output:
            print("\n✅ Captcha is required - this is expected")
            return "captcha_required"
        elif "already registered" in combined_output.lower():
            print("\n✅ Already registered!")
            return "already_registered"
        elif "rate limit" in combined_output.lower():
            print("\n⚠️  Rate limited")
            return "rate_limited"
        elif "SMS" in combined_output or "voice" in combined_output:
            print("\n🎉 Registration may have worked without captcha!")
            return "no_captcha_needed"
        else:
            print("\n❓ Unexpected response")
            return "unknown"
    
    def extract_captcha_patterns(self, url_or_token):
        """Extract captcha token from various formats"""
        patterns = [
            # New format patterns
            r'signalcaptchas://.*?([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            r'signal-captcha[s]?://.*?([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            r'challenge\.([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            # Original patterns
            r'signal-hcaptcha\.([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
            # Just UUID
            r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_token)
            if match:
                return match.group(1)
        
        return None
    
    def guided_registration(self):
        """Walk through guided registration with new URL"""
        print(f"\n🚀 Guided Registration with New Captcha URL")
        print("=" * 60)
        
        # Check registration status first
        reg_status = self.test_registration_flow()
        
        if reg_status == "already_registered":
            print("\n🎉 You're already registered! No need to continue.")
            print("🚀 Run: python src/idle_bot.py")
            return True
        elif reg_status == "rate_limited":
            print("\n⏰ You're rate limited. Wait 15+ minutes or try a different number.")
            return False
        elif reg_status == "no_captcha_needed":
            print("\n🎉 Registration worked without captcha!")
            verification_code = input("📱 Enter SMS verification code: ").strip()
            return self.verify_code(verification_code)
        
        # Need captcha
        print(f"\n📋 Step 1: Get Captcha Token")
        print(f"🔗 Opening: {self.captcha_url}")
        
        open_browser = input("Open captcha URL in browser? (y/n): ").strip().lower()
        if open_browser == 'y':
            webbrowser.open(self.captcha_url)
            print("✅ Browser opened!")
        
        print(f"\n📝 Instructions:")
        print("1. Solve the captcha completely")
        print("2. Right-click on 'Open Signal' button")
        print("3. Select 'Copy link address'")
        print("4. Paste the FULL URL below")
        
        captcha_input = input("\n📋 Paste the captcha URL: ").strip()
        
        if not captcha_input:
            print("❌ No captcha URL provided")
            return False
        
        # Extract token
        captcha_token = self.extract_captcha_patterns(captcha_input)
        
        if not captcha_token:
            print("\n⚠️  Could not extract token automatically")
            print("💡 Look for a UUID like: 5fad97ac-7d06-4e44-b18a-b950b20148ff")
            captcha_token = input("📋 Enter just the token: ").strip()
        else:
            print(f"\n✅ Extracted token: {captcha_token}")
        
        if not captcha_token:
            print("❌ No captcha token available")
            return False
        
        # Register with captcha
        print(f"\n📝 Step 2: Registering with captcha...")
        return self.register_with_captcha(captcha_token)
    
    def register_with_captcha(self, captcha_token):
        """Register using the captcha token"""
        cmd = f'docker exec signal-api signal-cli -a {self.phone_number} register --captcha "{captcha_token}"'
        stdout, stderr, code = self.run_command(cmd)
        
        combined = (stdout or "") + (stderr or "")
        print(f"Registration result: {combined}")
        
        if code == 0 or "SMS" in combined or "voice" in combined:
            print("✅ Registration request sent!")
            verification_code = input("\n📱 Enter SMS verification code: ").strip()
            return self.verify_code(verification_code)
        else:
            print(f"❌ Registration failed: {combined}")
            return False
    
    def verify_code(self, verification_code):
        """Verify the SMS code"""
        if not verification_code:
            return False
        
        print(f"🔄 Verifying code: {verification_code}")
        cmd = f"docker exec signal-api signal-cli -a {self.phone_number} verify {verification_code}"
        stdout, stderr, code = self.run_command(cmd)
        
        if code == 0:
            print("✅ Verification successful!")
            
            # Check final status
            time.sleep(2)
            stdout, stderr, code = self.run_command("docker exec signal-api curl -s http://localhost:8080/v1/accounts")
            
            if self.phone_number in (stdout or ""):
                print(f"🎉 {self.phone_number} is now registered!")
                return True
        
        print(f"❌ Verification failed: {stderr}")
        return False


def main():
    """Main test process"""
    print("🧪 New Captcha URL Test")
    print("=" * 50)
    print("Testing the updated captcha URL and registration process.\n")
    
    tester = NewCaptchaTest()
    
    # Test URLs first
    print("🔍 Testing captcha URLs...")
    working_urls = tester.test_captcha_urls()
    
    if working_urls:
        print(f"\n✅ Found {len(working_urls)} working URL(s):")
        for name, url in working_urls:
            print(f"   • {name}: {url}")
    else:
        print("\n❌ No working captcha URLs found")
    
    # Ask if user wants to try registration
    try_registration = input("\n❓ Try registration with new URL? (y/n): ").strip().lower()
    
    if try_registration == 'y':
        if tester.guided_registration():
            print("\n🎉 SUCCESS! Registration completed!")
            print("🚀 Your bot is ready. Run: python src/idle_bot.py")
        else:
            print("\n😞 Registration didn't complete successfully")
            print("💡 Try: python register_without_captcha.py")
    else:
        if working_urls:
            print(f"\n💡 The new URL works! Update your scripts to use:")
            print(f"   {working_urls[0][1]}")
        else:
            print("\n💡 Consider using alternative registration methods:")
            print("   python register_without_captcha.py")
            print("   python register_via_linking.py")


if __name__ == "__main__":
    main()
