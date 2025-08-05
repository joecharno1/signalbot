#!/usr/bin/env python3
"""
Signal Bot Registration Helper

This script helps you register your bot's phone number with Signal.
"""

import subprocess
import sys
import time
import re

def run_command(cmd):
    """Run a command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return None, str(e), 1

def extract_captcha_from_url(url):
    """Extract captcha token from Signal captcha URL"""
    # Pattern: signal-hcaptcha.UUID.registration.JWT
    match = re.search(r'signal-hcaptcha\.([a-f0-9-]+)\.registration', url)
    if match:
        return match.group(1)
    
    # Try just UUID pattern
    match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', url)
    if match:
        return match.group(1)
    
    return None

def main():
    print("🤖 Signal Bot Registration Helper")
    print("=" * 50)
    
    phone_number = "+13045641145"
    print(f"📱 Registering phone number: {phone_number}")
    
    # Step 1: Initial registration attempt
    print("\n📝 Step 1: Attempting registration...")
    stdout, stderr, code = run_command(f"docker exec signal-api signal-cli -a {phone_number} register")
    
    if stdout is None:
        stdout = ""
    if stderr is None:
        stderr = ""
    
    if "Captcha required" in stdout or "Captcha required" in stderr:
        print("✅ Registration initiated - captcha required")
        print("\n🔗 Please visit: https://signalcaptchas.org/challenge/generate.html")
        print("1. Solve the captcha")
        print("2. Right-click 'Open Signal' and copy the link")
        print("3. Paste the FULL URL here")
        
        captcha_url = input("\n📋 Paste the captcha URL: ").strip()
        
        # Extract captcha token
        captcha_token = extract_captcha_from_url(captcha_url)
        
        if not captcha_token:
            # If extraction failed, ask for manual input
            print("\n⚠️  Could not extract captcha automatically.")
            print("The captcha token is the UUID part (like: 5fad97ac-7d06-4e44-b18a-b950b20148ff)")
            captcha_token = input("📋 Enter just the captcha token: ").strip()
        else:
            print(f"\n✅ Extracted captcha token: {captcha_token}")
        
        # Step 2: Register with captcha
        print(f"\n📝 Step 2: Registering with captcha...")
        cmd = f'docker exec signal-api signal-cli -a {phone_number} register --captcha "{captcha_token}"'
        stdout, stderr, code = run_command(cmd)
        
        stdout = stdout or ""
        stderr = stderr or ""
        
        if code == 0 or "SMS" in stdout or "voice" in stdout:
            print("✅ Registration request sent!")
            print("\n📱 You should receive an SMS with a verification code")
            
            # Step 3: Verify with SMS code
            sms_code = input("\n📋 Enter the SMS verification code: ").strip()
            
            print(f"\n📝 Step 3: Verifying with code {sms_code}...")
            cmd = f"docker exec signal-api signal-cli -a {phone_number} verify {sms_code}"
            stdout, stderr, code = run_command(cmd)
            
            if code == 0:
                print("✅ Phone number successfully verified!")
                
                # Check if account is registered
                print("\n🔍 Checking registration status...")
                stdout, stderr, code = run_command("docker exec signal-api curl -s http://localhost:8080/v1/accounts")
                
                stdout = stdout or ""
                if phone_number in stdout:
                    print(f"✅ Bot successfully registered as {phone_number}")
                    print("\n🎉 Your Signal bot is now ready to use!")
                    print("\n📋 Next steps:")
                    print("1. Add the bot to your Signal group")
                    print("2. Make the bot an admin in the group")
                    print("3. Run: python src/idle_bot.py")
                else:
                    print("⚠️  Registration may need a moment to complete")
                    print("Try running: python src/idle_bot.py in a minute")
            else:
                print(f"❌ Verification failed: {stderr}")
                print("\n💡 Common issues:")
                print("- Wrong verification code")
                print("- Code expired (try getting a new one)")
        else:
            print(f"❌ Registration with captcha failed: {stderr}")
            print("\n💡 Try getting a fresh captcha token")
    
    elif (stdout and "already registered" in stdout.lower()) or (stderr and "already registered" in stderr.lower()):
        print("✅ Phone number is already registered!")
        print("🚀 You can start using the bot immediately")
        print("\nRun: python src/idle_bot.py")
    
    else:
        print(f"❌ Unexpected response: {stdout} {stderr}")

if __name__ == "__main__":
    main()
