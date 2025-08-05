#!/usr/bin/env python3
"""
Virtual Number Registration Guide

This script helps you set up and use virtual phone numbers
to register your Signal bot when rate limited.
"""

import webbrowser
import time

class VirtualNumberGuide:
    """Guide for using virtual numbers with Signal"""
    
    def __init__(self):
        self.services = {
            "1": {
                "name": "Google Voice",
                "url": "https://voice.google.com",
                "cost": "Free",
                "requirements": "US phone number for verification",
                "pros": ["Free", "Reliable", "Permanent number"],
                "cons": ["Requires existing US number", "US only"],
                "steps": [
                    "Sign in to your Google account",
                    "Choose a Google Voice number",
                    "Verify with your existing phone",
                    "Use the new number for Signal registration"
                ]
            },
            "2": {
                "name": "TextNow",
                "url": "https://www.textnow.com",
                "cost": "Free (with ads)",
                "requirements": "Email address",
                "pros": ["Completely free", "No phone required", "Works internationally"],
                "cons": ["Ads in app", "Numbers can be recycled if inactive"],
                "steps": [
                    "Create a TextNow account",
                    "Choose a free phone number",
                    "Install app or use web version",
                    "Receive SMS for Signal verification"
                ]
            },
            "3": {
                "name": "Twilio",
                "url": "https://www.twilio.com/try-twilio",
                "cost": "$1-2/month per number",
                "requirements": "Credit card",
                "pros": ["Very reliable", "API access", "Many countries"],
                "cons": ["Costs money", "More complex setup"],
                "steps": [
                    "Sign up for Twilio account",
                    "Add payment method",
                    "Buy a phone number ($1/month)",
                    "Use number for Signal registration",
                    "Can receive SMS via Twilio console"
                ]
            },
            "4": {
                "name": "Burner",
                "url": "https://www.burnerapp.com",
                "cost": "$4.99/month",
                "requirements": "Smartphone app",
                "pros": ["Easy to use", "Temporary numbers", "Good privacy"],
                "cons": ["Costs money", "App required"],
                "steps": [
                    "Download Burner app",
                    "Start free trial or subscribe",
                    "Create a burner number",
                    "Use for Signal registration"
                ]
            },
            "5": {
                "name": "MySudo",
                "url": "https://mysudo.com",
                "cost": "Free tier available",
                "requirements": "Smartphone",
                "pros": ["Privacy focused", "Multiple numbers", "Secure"],
                "cons": ["Limited free tier", "App required"],
                "steps": [
                    "Download MySudo app",
                    "Create account",
                    "Generate a Sudo with phone number",
                    "Use for Signal verification"
                ]
            }
        }
    
    def show_menu(self):
        """Display virtual number options"""
        print("\n📱 Virtual Number Services for Signal Bot")
        print("=" * 60)
        print("\nChoose a service based on your needs:\n")
        
        for key, service in self.services.items():
            print(f"{key}. {service['name']} - {service['cost']}")
            print(f"   Requirements: {service['requirements']}")
        
        print("\n6. Compare all services")
        print("7. Test if your current number works")
        print("8. Exit")
    
    def show_service_details(self, service_key):
        """Show detailed information about a service"""
        if service_key not in self.services:
            print("❌ Invalid selection")
            return
        
        service = self.services[service_key]
        
        print(f"\n📱 {service['name']}")
        print("=" * 60)
        print(f"🌐 Website: {service['url']}")
        print(f"💰 Cost: {service['cost']}")
        print(f"📋 Requirements: {service['requirements']}")
        
        print("\n✅ Pros:")
        for pro in service['pros']:
            print(f"   • {pro}")
        
        print("\n❌ Cons:")
        for con in service['cons']:
            print(f"   • {con}")
        
        print("\n📝 Setup Steps:")
        for i, step in enumerate(service['steps'], 1):
            print(f"   {i}. {step}")
        
        open_browser = input("\n🌐 Open website in browser? (y/n): ").strip().lower()
        if open_browser == 'y':
            webbrowser.open(service['url'])
            print("✅ Opened in browser!")
    
    def compare_services(self):
        """Compare all virtual number services"""
        print("\n📊 Virtual Number Services Comparison")
        print("=" * 80)
        print(f"{'Service':<15} {'Cost':<20} {'Best For':<45}")
        print("-" * 80)
        
        comparisons = {
            "Google Voice": "US users with existing phone",
            "TextNow": "Free option, no phone needed",
            "Twilio": "Developers, reliable automation",
            "Burner": "Privacy conscious, temporary use",
            "MySudo": "Multiple identities, privacy"
        }
        
        for key, service in self.services.items():
            name = service['name']
            cost = service['cost']
            best_for = comparisons.get(name, "General use")
            print(f"{name:<15} {cost:<20} {best_for:<45}")
        
        print("\n💡 Recommendations:")
        print("• Rate limited? Try TextNow (quickest setup)")
        print("• Need reliability? Use Twilio")
        print("• US-based? Google Voice is free and permanent")
        print("• Privacy focused? MySudo or Burner")
    
    def test_number_format(self):
        """Test if a phone number is properly formatted"""
        print("\n📱 Phone Number Format Tester")
        print("=" * 40)
        
        number = input("Enter phone number to test: ").strip()
        
        # Check format
        issues = []
        
        if not number.startswith('+'):
            issues.append("Missing '+' prefix")
            
        if number.startswith('+1') and len(number) != 12:
            issues.append("US numbers should be +1 followed by 10 digits")
        
        if not number[1:].isdigit():
            issues.append("Contains non-numeric characters")
        
        if issues:
            print(f"\n❌ Format issues found:")
            for issue in issues:
                print(f"   • {issue}")
            
            # Suggest correction
            if not number.startswith('+'):
                if number.startswith('1') and len(number) == 11:
                    print(f"\n💡 Did you mean: +{number}")
                elif len(number) == 10:
                    print(f"\n💡 Did you mean: +1{number}")
        else:
            print(f"\n✅ {number} appears to be properly formatted!")
            print("🚀 Ready to use for Signal registration")
    
    def quick_setup_guide(self):
        """Quick setup for rate-limited users"""
        print("\n⚡ Quick Setup for Rate-Limited Users")
        print("=" * 50)
        print("\n🎯 Fastest Option: TextNow\n")
        
        steps = [
            "Go to https://www.textnow.com",
            "Click 'Sign Up Free'",
            "Enter email and create password",
            "Choose area code (any US/Canada)",
            "Select a phone number",
            "Open web app or mobile app",
            "Run: python register_no_qr.py",
            "Use your new TextNow number",
            "Check TextNow for the SMS code"
        ]
        
        for i, step in enumerate(steps, 1):
            print(f"{i}. {step}")
            if i in [1, 6, 7]:
                input("   Press Enter when ready to continue...")
        
        print("\n✅ You should now have a working virtual number!")


def main():
    """Main virtual number guide"""
    guide = VirtualNumberGuide()
    
    print("🆘 Signal Bot Registration - Virtual Number Helper")
    print("=" * 60)
    print("\nThis tool helps you get a virtual phone number to bypass rate limiting.")
    
    # Quick check
    rate_limited = input("\n❓ Are you currently rate-limited? (y/n): ").strip().lower()
    
    if rate_limited == 'y':
        print("\n⚡ Let's get you a virtual number quickly!")
        quick = input("Want the quickest solution? (y/n): ").strip().lower()
        
        if quick == 'y':
            guide.quick_setup_guide()
            return
    
    while True:
        guide.show_menu()
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice in ["1", "2", "3", "4", "5"]:
            guide.show_service_details(choice)
        elif choice == "6":
            guide.compare_services()
        elif choice == "7":
            guide.test_number_format()
        elif choice == "8":
            print("\n👋 Good luck with your Signal bot!")
            break
        else:
            print("❌ Invalid selection")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
