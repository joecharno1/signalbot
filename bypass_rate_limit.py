#!/usr/bin/env python3
"""
Quick Rate Limit Bypass for Signal Bot Registration

This script provides immediate solutions when you're rate limited.
"""

import time
import subprocess
import requests
import json
import os

def print_banner():
    """Print emergency help banner"""
    print("\n" + "🚨" * 20)
    print("🚨 RATE LIMIT BYPASS - EMERGENCY HELP 🚨")
    print("🚨" * 20 + "\n")

def check_existing_accounts():
    """Quick check for already registered accounts"""
    print("🔍 Checking for existing registrations...")
    
    try:
        response = requests.get("http://localhost:8080/v1/accounts", timeout=5)
        if response.status_code == 200:
            accounts = response.json()
            if accounts:
                print("\n✅ GOOD NEWS! Found registered accounts:")
                for acc in accounts:
                    print(f"   📱 {acc}")
                print("\n🎉 You don't need to register again!")
                print("🚀 Just run: python src/idle_bot.py")
                return True
    except:
        pass
    
    print("❌ No existing registrations found")
    return False

def immediate_solutions():
    """Provide immediate solutions for rate limiting"""
    print("\n⚡ IMMEDIATE SOLUTIONS:")
    print("=" * 50)
    
    print("\n1️⃣ FASTEST: Use TextNow (5 minutes)")
    print("   • Go to: https://www.textnow.com")
    print("   • Sign up with email (no phone needed)")
    print("   • Get free US/Canada number instantly")
    print("   • Use web browser - no app needed!")
    
    print("\n2️⃣ RELIABLE: Use Google Voice (10 minutes)")
    print("   • Go to: https://voice.google.com")
    print("   • Sign in with Google account")
    print("   • Choose a number (requires US phone)")
    print("   • Free and permanent")
    
    print("\n3️⃣ DEVELOPER: Use Twilio (15 minutes)")
    print("   • Sign up: https://www.twilio.com/try-twilio")
    print("   • Get $15 free credit")
    print("   • Buy number for $1/month")
    print("   • Very reliable for bots")

def textnow_quick_guide():
    """Ultra-quick TextNow setup"""
    print("\n📱 TextNow Quick Setup (Fastest Option)")
    print("=" * 50)
    
    print("\n🚀 Open this link: https://www.textnow.com/signup")
    input("\nPress Enter when the page is open...")
    
    print("\n✅ Step 1: Create Account")
    print("   • Enter any email")
    print("   • Create a password")
    print("   • Click 'Sign Up Free'")
    input("\nPress Enter when done...")
    
    print("\n✅ Step 2: Get Number")
    print("   • Choose any area code")
    print("   • Pick a number you like")
    print("   • Click 'Select'")
    input("\nPress Enter when you have your number...")
    
    number = input("\n📱 Enter your new TextNow number (with +1): ")
    
    print(f"\n✅ Great! Your number is: {number}")
    print("\n✅ Step 3: Register with Signal")
    print("   1. Keep TextNow open in browser")
    print("   2. Run: python register_no_qr.py")
    print(f"   3. Use number: {number}")
    print("   4. Check TextNow for SMS code")
    
    return number

def wait_time_calculator(phone_number):
    """Calculate remaining wait time"""
    # Check if we have a state file
    state_file = "data/registration_state.json"
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
            
        if phone_number in state.get("phone_numbers", {}):
            attempts = state["phone_numbers"][phone_number]
            if attempts:
                from datetime import datetime, timedelta
                last_attempt = datetime.fromisoformat(attempts[-1]["timestamp"])
                elapsed = datetime.now() - last_attempt
                wait_time = timedelta(minutes=15) - elapsed
                
                if wait_time.total_seconds() > 0:
                    minutes = int(wait_time.total_seconds() / 60)
                    return minutes
    
    return 0

def main():
    """Main bypass helper"""
    print_banner()
    
    # First, check if already registered
    if check_existing_accounts():
        return
    
    print("\n😤 So you're rate limited? Let's fix this NOW!\n")
    
    # Get their situation
    phone = input("📱 What number got rate limited? (or press Enter to skip): ").strip()
    
    if phone:
        wait_mins = wait_time_calculator(phone)
        if wait_mins > 0:
            print(f"\n⏰ {phone} needs to wait ~{wait_mins} more minutes")
        else:
            print(f"\n✅ {phone} might be ready to try again!")
            retry = input("Want to retry with this number? (y/n): ").strip().lower()
            if retry == 'y':
                print("\n🚀 Run: python register_no_qr.py")
                return
    
    print("\n🎯 Let's get you a NEW number instead!")
    print("\nOptions:")
    print("1. TextNow - FREE & FAST (recommended)")
    print("2. Show all virtual number options")
    print("3. I'll handle it myself")
    
    choice = input("\nSelect (1-3): ").strip()
    
    if choice == "1":
        new_number = textnow_quick_guide()
        
        # Save the new number for reference
        os.makedirs("data", exist_ok=True)
        with open("data/virtual_numbers.txt", "a") as f:
            f.write(f"{new_number} - TextNow - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print("\n✅ All set! Your virtual number is saved.")
        print("🚀 Now run: python register_no_qr.py")
        
    elif choice == "2":
        print("\n🚀 Running virtual number guide...")
        subprocess.run([sys.executable, "virtual_number_guide.py"])
        
    else:
        immediate_solutions()
        print("\n💡 Pick any service above and get a number")
        print("🚀 Then run: python register_no_qr.py")
    
    print("\n📌 Remember:")
    print("• Keep your virtual number service open")
    print("• Watch for the SMS verification code")
    print("• Complete registration quickly")
    print("\n🍀 Good luck!")


if __name__ == "__main__":
    import sys
    main()
