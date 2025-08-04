#!/usr/bin/env python3
"""
Signal Idle User Bot - Interactive Demo

This script provides an interactive demonstration of the bot's capabilities
without requiring a real Signal connection.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, 'src')

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def simulate_group_activity():
    """Simulate a Signal group with various user activity levels"""
    print_header("🤖 Signal Idle User Bot - Interactive Demo")
    
    print("""
This demo simulates a Signal group with various user activity levels
and demonstrates how the bot would identify and manage idle users.

📱 Simulated Signal Group: "Tech Team Chat"
👥 Total Members: 8 users
⏰ Monitoring Period: 90 days
🎯 Idle Threshold: 30 days
    """)
    
    # Simulate user data
    now = datetime.now()
    users = [
        {
            'name': 'Alice (Admin)',
            'phone': '+1234567890',
            'last_seen': now - timedelta(days=2),
            'messages': 245,
            'role': 'Admin',
            'status': 'Very Active'
        },
        {
            'name': 'Bob (Developer)',
            'phone': '+1234567891',
            'last_seen': now - timedelta(days=7),
            'messages': 156,
            'role': 'Member',
            'status': 'Active'
        },
        {
            'name': 'Charlie (Designer)',
            'phone': '+1234567892',
            'last_seen': now - timedelta(days=15),
            'messages': 89,
            'role': 'Member',
            'status': 'Moderately Active'
        },
        {
            'name': 'Diana (PM)',
            'phone': '+1234567893',
            'last_seen': now - timedelta(days=25),
            'messages': 67,
            'role': 'Member',
            'status': 'Less Active'
        },
        {
            'name': 'Eve (Intern)',
            'phone': '+1234567894',
            'last_seen': now - timedelta(days=35),
            'messages': 23,
            'role': 'Member',
            'status': 'IDLE (35 days)'
        },
        {
            'name': 'Frank (Contractor)',
            'phone': '+1234567895',
            'last_seen': now - timedelta(days=45),
            'messages': 12,
            'role': 'Member',
            'status': 'IDLE (45 days)'
        },
        {
            'name': 'Grace (Ex-employee)',
            'phone': '+1234567896',
            'last_seen': now - timedelta(days=75),
            'messages': 8,
            'role': 'Member',
            'status': 'VERY IDLE (75 days)'
        },
        {
            'name': 'Henry (Bot)',
            'phone': '+1234567897',
            'last_seen': now - timedelta(days=60),
            'messages': 1,
            'role': 'Bot',
            'status': 'PROTECTED (Bot account)'
        }
    ]
    
    return users

def show_current_activity(users):
    """Display current group activity"""
    print_section("📊 Current Group Activity")
    
    print(f"{'Name':<20} {'Phone':<15} {'Last Seen':<12} {'Messages':<10} {'Status'}")
    print("-" * 80)
    
    for user in users:
        days_ago = (datetime.now() - user['last_seen']).days
        last_seen_str = f"{days_ago}d ago"
        
        status_color = ""
        if "IDLE" in user['status']:
            status_color = "🔴"
        elif "Active" in user['status']:
            status_color = "🟢"
        elif "PROTECTED" in user['status']:
            status_color = "🛡️"
        else:
            status_color = "🟡"
        
        print(f"{user['name']:<20} {user['phone']:<15} {last_seen_str:<12} {user['messages']:<10} {status_color} {user['status']}")

def simulate_bot_commands(users):
    """Simulate bot command responses"""
    print_section("🤖 Bot Command Simulation")
    
    # Simulate !stats command
    print("Admin sends: !stats")
    print("Bot responds:")
    print("""
📊 Group Activity Statistics

👥 Total tracked users: 8
✅ Active users: 4
💤 Idle users: 3
🔥 Active last 7 days: 2

⚙️ Current settings:
• Idle threshold: 30 days
• Protected users: 2
• Dry run mode: On
    """)
    
    # Simulate !idle command
    print("\nAdmin sends: !idle")
    print("Bot responds:")
    print("""
🔍 Found 3 idle users (>30 days):

1. +1234567894 (Eve - Intern)
   Last seen: 2025-07-03 14:30
   Days idle: 35
   Messages: 23

2. +1234567895 (Frank - Contractor)
   Last seen: 2025-06-23 09:15
   Days idle: 45
   Messages: 12

3. +1234567896 (Grace - Ex-employee)
   Last seen: 2025-05-24 16:45
   Days idle: 75
   Messages: 8

Use `!remove-idle` to remove these users (dry-run mode enabled)
    """)

def simulate_removal_process(users):
    """Simulate the user removal process"""
    print_section("⚠️ User Removal Simulation")
    
    print("Admin sends: !remove-idle")
    print("Bot responds (DRY RUN MODE):")
    print("""
🔍 DRY RUN: Would remove 3 idle users:

• +1234567894 (Eve - Intern) - 35 days idle
• +1234567895 (Frank - Contractor) - 45 days idle  
• +1234567896 (Grace - Ex-employee) - 75 days idle

To actually remove users, set 'dry_run: false' in config

⚠️ SAFETY FEATURES ACTIVE:
✅ Dry run mode prevents accidental removals
✅ Protected users (bots, admins) are excluded
✅ Admin-only commands prevent unauthorized use
✅ Activity data is preserved for audit trail
    """)

def show_configuration_options():
    """Show configuration and customization options"""
    print_section("⚙️ Configuration Options")
    
    print("""
The bot can be customized with these settings:

📅 IDLE THRESHOLD
   • Default: 30 days
   • Adjustable: 1-365 days
   • Command: !config threshold <days>

🛡️ PROTECTED USERS
   • Bot accounts (automatic)
   • Admins (configurable)
   • VIP members (manual list)

👑 ADMIN CONTROLS
   • Multiple admin phone numbers
   • Admin-only command restrictions
   • Configuration change permissions

🔒 SAFETY FEATURES
   • Dry run mode (default: enabled)
   • Activity data backup
   • Removal confirmation
   • Audit logging

📊 MONITORING
   • Real-time activity tracking
   • Statistical reports
   • Trend analysis
   • Export capabilities
    """)

def show_setup_requirements():
    """Show what's needed to set up the bot"""
    print_section("🚀 Setup Requirements")
    
    print("""
To use this bot in your Signal group, you need:

📱 SIGNAL REQUIREMENTS:
   ✓ Dedicated phone number for the bot
   ✓ Signal account linked to that number
   ✓ Admin access to your Signal group
   ✓ Group with members to monitor

💻 TECHNICAL REQUIREMENTS:
   ✓ Linux/macOS/Windows computer or server
   ✓ Python 3.9+ installed
   ✓ Docker for signal-cli-rest-api
   ✓ Internet connection
   ✓ Basic command line knowledge

⚙️ SETUP PROCESS:
   1. Clone the bot repository
   2. Configure phone numbers and settings
   3. Start signal-cli-rest-api with Docker
   4. Link bot phone number via QR code
   5. Add bot to your Signal group
   6. Grant bot admin permissions
   7. Test with dry run mode
   8. Enable live mode when ready

📚 DOCUMENTATION:
   • README.md - Overview and quick start
   • docs/SETUP.md - Detailed setup guide
   • docs/TROUBLESHOOTING.md - Common issues
   • Example configurations included
    """)

def main():
    """Run the interactive demo"""
    users = simulate_group_activity()
    
    show_current_activity(users)
    simulate_bot_commands(users)
    simulate_removal_process(users)
    show_configuration_options()
    show_setup_requirements()
    
    print_header("✅ Demo Complete")
    print("""
This demonstration showed how the Signal Idle User Bot:

🔍 Monitors user activity automatically
📊 Provides detailed statistics and reports  
💤 Identifies idle users based on configurable thresholds
🛡️ Protects important users from removal
⚠️ Uses dry run mode for safety
👑 Restricts admin functions to authorized users
📱 Integrates seamlessly with Signal groups

The bot is production-ready and includes comprehensive documentation,
safety features, and troubleshooting guides.

Next steps:
1. Review the code in src/idle_bot.py
2. Follow the setup guide in docs/SETUP.md
3. Configure for your Signal group
4. Test in dry run mode first
5. Deploy for live use

Happy bot building! 🤖
    """)

if __name__ == "__main__":
    main()

