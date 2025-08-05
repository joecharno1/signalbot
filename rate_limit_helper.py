#!/usr/bin/env python3
"""
Signal Rate Limit Helper

This script helps you work around Signal's rate limiting during registration.
"""

import time
import json
import os
from datetime import datetime, timedelta
import subprocess

class RateLimitHelper:
    """Helps manage and work around Signal rate limiting"""
    
    def __init__(self):
        self.state_file = "data/registration_state.json"
        self.load_state()
    
    def load_state(self):
        """Load previous registration attempts"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "attempts": [],
                "phone_numbers": {}
            }
    
    def save_state(self):
        """Save registration state"""
        os.makedirs("data", exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def record_attempt(self, phone_number, success=False):
        """Record a registration attempt"""
        attempt = {
            "phone": phone_number,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        self.state["attempts"].append(attempt)
        
        if phone_number not in self.state["phone_numbers"]:
            self.state["phone_numbers"][phone_number] = []
        self.state["phone_numbers"][phone_number].append(attempt)
        
        self.save_state()
    
    def check_wait_time(self, phone_number):
        """Check how long to wait before next attempt"""
        if phone_number not in self.state["phone_numbers"]:
            return 0, "No previous attempts recorded"
        
        attempts = self.state["phone_numbers"][phone_number]
        if not attempts:
            return 0, "No previous attempts recorded"
        
        last_attempt = datetime.fromisoformat(attempts[-1]["timestamp"])
        time_passed = datetime.now() - last_attempt
        
        # Signal typically rate limits for 10-15 minutes
        wait_time = timedelta(minutes=15) - time_passed
        
        if wait_time.total_seconds() > 0:
            minutes = int(wait_time.total_seconds() / 60)
            seconds = int(wait_time.total_seconds() % 60)
            return wait_time.total_seconds(), f"{minutes} minutes {seconds} seconds"
        else:
            return 0, "Ready to try again"
    
    def get_alternative_numbers(self, current_number):
        """Suggest alternative phone numbers"""
        print("\n📱 Alternative Phone Number Options:")
        print("=" * 50)
        
        suggestions = []
        
        # Check which numbers have been tried
        tried_numbers = list(self.state["phone_numbers"].keys())
        
        print("\n🔍 Recently tried numbers:")
        for num in tried_numbers:
            attempts = self.state["phone_numbers"][num]
            last_attempt = datetime.fromisoformat(attempts[-1]["timestamp"])
            time_ago = datetime.now() - last_attempt
            minutes_ago = int(time_ago.total_seconds() / 60)
            
            wait_seconds, wait_msg = self.check_wait_time(num)
            if wait_seconds > 0:
                print(f"  ❌ {num} - Rate limited ({wait_msg} remaining)")
            else:
                print(f"  ✅ {num} - Ready to use (last tried {minutes_ago} minutes ago)")
                suggestions.append(num)
        
        print("\n💡 Virtual Number Services:")
        print("  1. Google Voice (https://voice.google.com)")
        print("     - Free US numbers")
        print("     - Requires existing US phone")
        print("  2. TextNow (https://www.textnow.com)")
        print("     - Free US/Canada numbers")
        print("     - Works via app or web")
        print("  3. Twilio (https://www.twilio.com)")
        print("     - $1/month per number")
        print("     - Very reliable")
        print("  4. Vonage/Nexmo")
        print("     - Professional service")
        print("     - Good for production bots")
        
        return suggestions
    
    def use_existing_registration(self):
        """Check if we can use an existing registration"""
        print("\n🔍 Checking for existing registrations...")
        
        try:
            # Check signal-cli for registered accounts
            result = subprocess.run(
                ["docker", "exec", "signal-api", "signal-cli", "-a", "+12035442924", "listAccounts"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout:
                print("✅ Found existing registrations:")
                print(result.stdout)
                return True
            
            # Also check via REST API
            import requests
            response = requests.get("http://localhost:8080/v1/accounts", timeout=5)
            if response.status_code == 200:
                accounts = response.json()
                if accounts:
                    print("✅ Found registered accounts via API:")
                    for acc in accounts:
                        print(f"   📱 {acc}")
                    return True
        except Exception as e:
            print(f"⚠️  Error checking registrations: {e}")
        
        return False
    
    def wait_with_countdown(self, seconds):
        """Show countdown while waiting"""
        print(f"\n⏳ Waiting {int(seconds)} seconds...")
        
        for remaining in range(int(seconds), 0, -1):
            mins = remaining // 60
            secs = remaining % 60
            print(f"\r⏱️  {mins:02d}:{secs:02d} remaining...", end="", flush=True)
            time.sleep(1)
        
        print("\r✅ Wait complete!              ")


def main():
    """Main rate limit helper"""
    print("🛡️ Signal Rate Limit Helper")
    print("=" * 50)
    
    helper = RateLimitHelper()
    
    # Check if already registered
    if helper.use_existing_registration():
        print("\n🎉 Great news! You already have a registered account.")
        print("🚀 You can skip registration and run: python src/idle_bot.py")
        return
    
    print("\n⚠️  Rate Limiting Detected!")
    print("Signal limits registration attempts to prevent abuse.")
    
    # Get phone number
    phone = input("\n📱 Enter the phone number you tried to register: ").strip()
    helper.record_attempt(phone, success=False)
    
    # Check wait time
    wait_seconds, wait_msg = helper.check_wait_time(phone)
    
    if wait_seconds > 0:
        print(f"\n⏰ Rate limit active for {phone}")
        print(f"   Time remaining: {wait_msg}")
        
        # Offer options
        print("\n🔧 Options:")
        print("1. Wait for rate limit to expire")
        print("2. Try a different phone number")
        print("3. Check for existing registrations")
        print("4. Exit and try later")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            helper.wait_with_countdown(wait_seconds)
            print("\n✅ Rate limit should be expired now!")
            print("🚀 Run: python register_no_qr.py")
        
        elif choice == "2":
            suggestions = helper.get_alternative_numbers(phone)
            if suggestions:
                print(f"\n✅ These numbers are ready to use: {', '.join(suggestions)}")
            
            new_phone = input("\n📱 Enter new phone number (or press Enter to exit): ").strip()
            if new_phone:
                print(f"\n🚀 Run: python register_no_qr.py")
                print(f"   Use phone number: {new_phone}")
        
        elif choice == "3":
            helper.use_existing_registration()
        
    else:
        print(f"\n✅ No active rate limit for {phone}")
        print("🚀 You can try registration again now!")
        print("   Run: python register_no_qr.py")
    
    # General tips
    print("\n💡 Tips to Avoid Rate Limiting:")
    print("1. Wait at least 15 minutes between attempts")
    print("2. Use fresh captcha tokens (they expire quickly)")
    print("3. Complete registration quickly once started")
    print("4. Consider using a different phone number")
    print("5. Don't refresh or retry too quickly")


if __name__ == "__main__":
    main()
