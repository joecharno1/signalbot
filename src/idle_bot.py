#!/usr/bin/env python3
"""
Signal Idle User Bot

A Signal bot that monitors group activity and can identify and remove idle users.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

from signalbot import SignalBot, Command, Context
import yaml


@dataclass
class UserActivity:
    """Track user activity data"""
    phone_number: str
    last_seen: datetime
    message_count: int = 0
    first_seen: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'phone_number': self.phone_number,
            'last_seen': self.last_seen.isoformat(),
            'message_count': self.message_count,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            phone_number=data['phone_number'],
            last_seen=datetime.fromisoformat(data['last_seen']),
            message_count=data.get('message_count', 0),
            first_seen=datetime.fromisoformat(data['first_seen']) if data.get('first_seen') else None
        )


class IdleUserBot:
    """Signal bot for managing idle users in groups"""
    
    def __init__(self, config_path: str = "config/bot_config.yaml"):
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
        
        # Initialize Signal bot
        self.bot = SignalBot({
            "signal_service": self.config['signal_service'],
            "phone_number": self.config['phone_number']
        })
        
        # Register commands
        self._register_commands()
    
    def _load_config(self) -> dict:
        """Load bot configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'signal_service': os.environ.get('SIGNAL_SERVICE', '127.0.0.1:8080'),
            'phone_number': os.environ.get('PHONE_NUMBER', ''),
            'admin_numbers': [],
            'idle_threshold_days': 30,
            'activity_file': 'data/user_activity.json',
            'log_level': 'INFO',
            'protected_users': [],
            'dry_run': True
        }
    
    def _load_activity_data(self):
        """Load user activity data from file"""
        if self.activity_file.exists():
            try:
                with open(self.activity_file, 'r') as f:
                    data = json.load(f)
                    for phone, activity_dict in data.items():
                        self.activity_data[phone] = UserActivity.from_dict(activity_dict)
                self.logger.info(f"Loaded activity data for {len(self.activity_data)} users")
            except Exception as e:
                self.logger.error(f"Error loading activity data: {e}")
    
    def _save_activity_data(self):
        """Save user activity data to file"""
        try:
            data = {phone: activity.to_dict() for phone, activity in self.activity_data.items()}
            with open(self.activity_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving activity data: {e}")
    
    def _register_commands(self):
        """Register bot commands"""
        self.bot.register(MessageTracker(self))
        self.bot.register(IdleCheckCommand(self))
        self.bot.register(RemoveIdleCommand(self))
        self.bot.register(ActivityStatsCommand(self))
        self.bot.register(HelpCommand(self))
        self.bot.register(ConfigCommand(self))
    
    def is_admin(self, phone_number: str) -> bool:
        """Check if user is an admin"""
        return phone_number in self.config.get('admin_numbers', [])
    
    def update_user_activity(self, phone_number: str):
        """Update user activity timestamp"""
        now = datetime.now()
        if phone_number in self.activity_data:
            self.activity_data[phone_number].last_seen = now
            self.activity_data[phone_number].message_count += 1
        else:
            self.activity_data[phone_number] = UserActivity(
                phone_number=phone_number,
                last_seen=now,
                message_count=1,
                first_seen=now
            )
        self._save_activity_data()
    
    def get_idle_users(self) -> List[UserActivity]:
        """Get list of idle users based on threshold"""
        threshold = timedelta(days=self.config.get('idle_threshold_days', 30))
        cutoff_date = datetime.now() - threshold
        protected = set(self.config.get('protected_users', []))
        
        idle_users = []
        for activity in self.activity_data.values():
            if (activity.last_seen < cutoff_date and 
                activity.phone_number not in protected):
                idle_users.append(activity)
        
        return sorted(idle_users, key=lambda x: x.last_seen)
    
    def start(self):
        """Start the bot"""
        self.logger.info("Starting Signal Idle User Bot...")
        self.bot.start()


class MessageTracker(Command):
    """Track all messages for activity monitoring"""
    
    def __init__(self, idle_bot: IdleUserBot):
        self.idle_bot = idle_bot
    
    async def handle(self, c: Context):
        """Handle all incoming messages to track activity"""
        if c.message.source:
            self.idle_bot.update_user_activity(c.message.source)


class IdleCheckCommand(Command):
    """Command to check for idle users"""
    
    def __init__(self, idle_bot: IdleUserBot):
        self.idle_bot = idle_bot
    
    async def handle(self, c: Context):
        if not c.message.text or not c.message.text.startswith("!idle"):
            return
        
        if not self.idle_bot.is_admin(c.message.source):
            await c.send("❌ Only admins can use this command.")
            return
        
        idle_users = self.idle_bot.get_idle_users()
        threshold_days = self.idle_bot.config.get('idle_threshold_days', 30)
        
        if not idle_users:
            await c.send(f"✅ No idle users found (threshold: {threshold_days} days)")
            return
        
        response = f"🔍 Found {len(idle_users)} idle users (>{threshold_days} days):\n\n"
        
        for i, user in enumerate(idle_users[:10], 1):  # Limit to 10 users
            days_idle = (datetime.now() - user.last_seen).days
            response += f"{i}. {user.phone_number}\n"
            response += f"   Last seen: {user.last_seen.strftime('%Y-%m-%d %H:%M')}\n"
            response += f"   Days idle: {days_idle}\n"
            response += f"   Messages: {user.message_count}\n\n"
        
        if len(idle_users) > 10:
            response += f"... and {len(idle_users) - 10} more users\n"
        
        response += f"\nUse `!remove-idle` to remove these users"
        if self.idle_bot.config.get('dry_run', True):
            response += " (dry-run mode enabled)"
        
        await c.send(response)


class RemoveIdleCommand(Command):
    """Command to remove idle users"""
    
    def __init__(self, idle_bot: IdleUserBot):
        self.idle_bot = idle_bot
    
    async def handle(self, c: Context):
        if not c.message.text or not c.message.text.startswith("!remove-idle"):
            return
        
        if not self.idle_bot.is_admin(c.message.source):
            await c.send("❌ Only admins can use this command.")
            return
        
        idle_users = self.idle_bot.get_idle_users()
        
        if not idle_users:
            await c.send("✅ No idle users to remove.")
            return
        
        dry_run = self.idle_bot.config.get('dry_run', True)
        
        if dry_run:
            response = f"🔍 DRY RUN: Would remove {len(idle_users)} idle users:\n\n"
            for user in idle_users[:5]:
                days_idle = (datetime.now() - user.last_seen).days
                response += f"• {user.phone_number} ({days_idle} days idle)\n"
            
            if len(idle_users) > 5:
                response += f"... and {len(idle_users) - 5} more\n"
            
            response += "\nTo actually remove users, set 'dry_run: false' in config"
            await c.send(response)
        else:
            # Note: Actual user removal would require group admin permissions
            # and proper Signal API calls. This is a placeholder for the logic.
            response = f"⚠️ REMOVAL FEATURE NOT IMPLEMENTED\n\n"
            response += f"Would remove {len(idle_users)} users:\n"
            for user in idle_users[:5]:
                response += f"• {user.phone_number}\n"
            
            response += "\n⚠️ Actual removal requires:\n"
            response += "1. Bot to have admin permissions in group\n"
            response += "2. Implementation of group member removal API calls\n"
            response += "3. Proper error handling and confirmation\n"
            
            await c.send(response)


class ActivityStatsCommand(Command):
    """Command to show activity statistics"""
    
    def __init__(self, idle_bot: IdleUserBot):
        self.idle_bot = idle_bot
    
    async def handle(self, c: Context):
        if not c.message.text or not c.message.text.startswith("!stats"):
            return
        
        if not self.idle_bot.is_admin(c.message.source):
            await c.send("❌ Only admins can use this command.")
            return
        
        total_users = len(self.idle_bot.activity_data)
        idle_users = len(self.idle_bot.get_idle_users())
        active_users = total_users - idle_users
        
        if total_users == 0:
            await c.send("📊 No activity data available yet.")
            return
        
        # Calculate activity stats
        now = datetime.now()
        recent_active = sum(1 for activity in self.idle_bot.activity_data.values() 
                          if (now - activity.last_seen).days <= 7)
        
        response = f"📊 Group Activity Statistics\n\n"
        response += f"👥 Total tracked users: {total_users}\n"
        response += f"✅ Active users: {active_users}\n"
        response += f"💤 Idle users: {idle_users}\n"
        response += f"🔥 Active last 7 days: {recent_active}\n\n"
        
        response += f"⚙️ Current settings:\n"
        response += f"• Idle threshold: {self.idle_bot.config.get('idle_threshold_days', 30)} days\n"
        response += f"• Protected users: {len(self.idle_bot.config.get('protected_users', []))}\n"
        response += f"• Dry run mode: {'On' if self.idle_bot.config.get('dry_run', True) else 'Off'}\n"
        
        await c.send(response)


class ConfigCommand(Command):
    """Command to show/update configuration"""
    
    def __init__(self, idle_bot: IdleUserBot):
        self.idle_bot = idle_bot
    
    async def handle(self, c: Context):
        if not c.message.text or not c.message.text.startswith("!config"):
            return
        
        if not self.idle_bot.is_admin(c.message.source):
            await c.send("❌ Only admins can use this command.")
            return
        
        parts = c.message.text.split()
        
        if len(parts) == 1:
            # Show current config
            response = "⚙️ Current Configuration:\n\n"
            response += f"• Idle threshold: {self.idle_bot.config.get('idle_threshold_days', 30)} days\n"
            response += f"• Dry run mode: {'On' if self.idle_bot.config.get('dry_run', True) else 'Off'}\n"
            response += f"• Protected users: {len(self.idle_bot.config.get('protected_users', []))}\n"
            response += f"• Admin numbers: {len(self.idle_bot.config.get('admin_numbers', []))}\n\n"
            response += "Use `!config <setting> <value>` to update settings"
            await c.send(response)
        
        elif len(parts) == 3:
            setting, value = parts[1], parts[2]
            
            if setting == "threshold":
                try:
                    days = int(value)
                    self.idle_bot.config['idle_threshold_days'] = days
                    await c.send(f"✅ Idle threshold set to {days} days")
                except ValueError:
                    await c.send("❌ Invalid number for threshold")
            
            elif setting == "dry_run":
                if value.lower() in ['true', 'on', '1']:
                    self.idle_bot.config['dry_run'] = True
                    await c.send("✅ Dry run mode enabled")
                elif value.lower() in ['false', 'off', '0']:
                    self.idle_bot.config['dry_run'] = False
                    await c.send("✅ Dry run mode disabled")
                else:
                    await c.send("❌ Use 'true' or 'false' for dry_run")
            
            else:
                await c.send("❌ Unknown setting. Available: threshold, dry_run")


class HelpCommand(Command):
    """Help command showing available commands"""
    
    def __init__(self, idle_bot: IdleUserBot):
        self.idle_bot = idle_bot
    
    async def handle(self, c: Context):
        if not c.message.text or not c.message.text.startswith("!help"):
            return
        
        response = "🤖 Signal Idle User Bot - Commands:\n\n"
        
        if self.idle_bot.is_admin(c.message.source):
            response += "👑 Admin Commands:\n"
            response += "• `!idle` - Check for idle users\n"
            response += "• `!remove-idle` - Remove idle users\n"
            response += "• `!stats` - Show activity statistics\n"
            response += "• `!config` - Show/update configuration\n"
            response += "• `!config threshold <days>` - Set idle threshold\n"
            response += "• `!config dry_run <true/false>` - Toggle dry run mode\n\n"
        
        response += "ℹ️ General Commands:\n"
        response += "• `!help` - Show this help message\n\n"
        
        if not self.idle_bot.is_admin(c.message.source):
            response += "Note: Most commands require admin privileges."
        
        await c.send(response)


if __name__ == "__main__":
    bot = IdleUserBot()
    bot.start()

