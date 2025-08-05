#!/usr/bin/env python3
"""
Demo Signal Idle User Bot

A demo version that simulates Signal bot functionality without requiring
a real Signal connection. Useful for testing and development.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List
from dataclasses import dataclass
from pathlib import Path
import yaml

# Import the original bot classes
from src.idle_bot import IdleUserBot, UserActivity

class DemoSignalBot:
    """Mock Signal bot for demo purposes"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.registered_commands = []
        
    def register(self, command):
        """Register a command handler"""
        self.registered_commands.append(command)
        self.logger.info(f"Registered command: {type(command).__name__}")
    
    def start(self):
        """Start the demo bot"""
        self.logger.info("Demo bot started - simulating Signal connection")
        self.logger.info(f"Phone number: {self.config['phone_number']}")
        self.logger.info(f"Signal service: {self.config['signal_service']}")
        
        # Simulate some demo interactions
        asyncio.run(self._run_demo())
    
    async def _run_demo(self):
        """Run demo scenarios"""
        print("\n" + "="*60)
        print("🤖 SIGNAL IDLE USER BOT - DEMO MODE")
        print("="*60)
        print(f"📱 Bot Phone: {self.config['phone_number']}")
        print(f"🔗 Signal Service: {self.config['signal_service']}")
        print(f"👑 Admins: {len(self.config.get('admin_numbers', []))}")
        print(f"🛡️ Protected Users: {len(self.config.get('protected_users', []))}")
        print(f"⏰ Idle Threshold: {self.config.get('idle_threshold_days', 30)} days")
        print(f"🔒 Dry Run Mode: {'On' if self.config.get('dry_run', True) else 'Off'}")
        print("="*60)
        
        # Simulate waiting for messages
        print("\n🔄 Bot is running and monitoring for messages...")
        print("💡 In real mode, the bot would:")
        print("   • Monitor all group messages for user activity")
        print("   • Track last seen timestamps for each user") 
        print("   • Respond to admin commands like !idle, !stats, !help")
        print("   • Remove idle users when dry_run is disabled")
        
        print("\n📝 Available Commands (for admins):")
        print("   • !help - Show help message")
        print("   • !idle - Check for idle users")
        print("   • !remove-idle - Remove idle users (respects dry_run)")
        print("   • !stats - Show activity statistics")
        print("   • !config - Show/update configuration")
        print("   • !config threshold <days> - Set idle threshold")
        print("   • !config dry_run <true/false> - Toggle dry run mode")
        
        print("\n🔧 To make this bot functional with real Signal:")
        print("   1. Register the bot phone number with Signal")
        print("   2. Add the bot to your Signal group")
        print("   3. Make the bot an admin in the group")
        print("   4. Replace DemoSignalBot with real SignalBot")
        
        print("\n⚠️  IMPORTANT SAFETY FEATURES:")
        print("   • Dry run mode is ENABLED by default")
        print("   • Protected users are never removed")
        print("   • Only admins can use dangerous commands")
        print("   • All activity is logged and tracked")
        
        # Keep running for demo
        try:
            while True:
                await asyncio.sleep(30)
                print(f"⚡ {datetime.now().strftime('%H:%M:%S')} - Bot is monitoring... (Press Ctrl+C to stop)")
        except KeyboardInterrupt:
            print("\n🛑 Demo bot stopped by user")


class DemoIdleUserBot(IdleUserBot):
    """Demo version of the Idle User Bot"""
    
    def __init__(self, config_path: str = "config/bot_config.yaml"):
        # Initialize parent class but skip Signal bot initialization
        self.config_path = config_path
        self.config = self._load_config()
        self.activity_data: Dict[str, UserActivity] = {}
        self.activity_file = Path(self.config.get('activity_file', 'data/user_activity.json'))
        self.activity_file.parent.mkdir(exist_ok=True)
        
        # Load existing activity data
        self._load_activity_data()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize DEMO Signal bot instead of real one
        self.bot = DemoSignalBot({
            "signal_service": self.config['signal_service'],
            "phone_number": self.config['phone_number']
        })
        
        # Register commands
        self._register_commands()
        
        # Create some demo activity data if none exists
        self._create_demo_data()
    
    def _create_demo_data(self):
        """Create demo activity data for testing"""
        if not self.activity_data:
            now = datetime.now()
            
            # Create sample users with different activity levels
            demo_users = {
                '+15551234567': UserActivity(  # Active user
                    phone_number='+15551234567',
                    last_seen=now - timedelta(days=2),
                    message_count=150,
                    first_seen=now - timedelta(days=90)
                ),
                '+15551234568': UserActivity(  # Idle user (35 days)
                    phone_number='+15551234568',
                    last_seen=now - timedelta(days=35),
                    message_count=25,
                    first_seen=now - timedelta(days=120)
                ),
                '+15551234569': UserActivity(  # Very idle user (60 days)
                    phone_number='+15551234569',
                    last_seen=now - timedelta(days=60),
                    message_count=5,
                    first_seen=now - timedelta(days=200)
                ),
                '+15551234570': UserActivity(  # Recent user
                    phone_number='+15551234570',
                    last_seen=now - timedelta(hours=6),
                    message_count=75,
                    first_seen=now - timedelta(days=30)
                ),
                '+15551234571': UserActivity(  # Borderline idle (30 days exactly)
                    phone_number='+15551234571',
                    last_seen=now - timedelta(days=30),
                    message_count=10,
                    first_seen=now - timedelta(days=45)
                )
            }
            
            self.activity_data.update(demo_users)
            self._save_activity_data()
            self.logger.info(f"Created demo activity data for {len(demo_users)} users")


def main():
    """Run the demo bot"""
    print("🚀 Starting Signal Idle User Bot in DEMO MODE...")
    
    try:
        demo_bot = DemoIdleUserBot()
        demo_bot.start()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

