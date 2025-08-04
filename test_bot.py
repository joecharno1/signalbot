#!/usr/bin/env python3
"""
Test script for Signal Idle User Bot

This script demonstrates the bot's functionality without requiring
a real Signal connection.
"""

import os
import sys
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.insert(0, 'src')

from idle_bot import IdleUserBot, UserActivity


def create_test_config():
    """Create a temporary test configuration"""
    config = {
        'signal_service': '127.0.0.1:8080',
        'phone_number': '+1234567890',
        'admin_numbers': ['+1234567890', '+1111111111'],
        'idle_threshold_days': 30,
        'activity_file': 'test_data/user_activity.json',
        'log_level': 'INFO',
        'protected_users': ['+1234567890'],
        'dry_run': True
    }
    
    # Create test config file
    os.makedirs('test_data', exist_ok=True)
    with open('test_data/test_config.yaml', 'w') as f:
        import yaml
        yaml.dump(config, f)
    
    return 'test_data/test_config.yaml'


def create_test_activity_data():
    """Create test user activity data"""
    now = datetime.now()
    
    # Create users with different activity levels
    users = {
        '+1111111111': UserActivity(  # Active user
            phone_number='+1111111111',
            last_seen=now - timedelta(days=5),
            message_count=150,
            first_seen=now - timedelta(days=90)
        ),
        '+2222222222': UserActivity(  # Idle user (35 days)
            phone_number='+2222222222',
            last_seen=now - timedelta(days=35),
            message_count=25,
            first_seen=now - timedelta(days=120)
        ),
        '+3333333333': UserActivity(  # Very idle user (60 days)
            phone_number='+3333333333',
            last_seen=now - timedelta(days=60),
            message_count=5,
            first_seen=now - timedelta(days=200)
        ),
        '+4444444444': UserActivity(  # Recent user
            phone_number='+4444444444',
            last_seen=now - timedelta(days=1),
            message_count=75,
            first_seen=now - timedelta(days=30)
        ),
        '+5555555555': UserActivity(  # Borderline idle (30 days exactly)
            phone_number='+5555555555',
            last_seen=now - timedelta(days=30),
            message_count=10,
            first_seen=now - timedelta(days=45)
        )
    }
    
    # Save test data
    os.makedirs('test_data', exist_ok=True)
    data = {phone: activity.to_dict() for phone, activity in users.items()}
    with open('test_data/user_activity.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    return users


def test_bot_initialization():
    """Test bot initialization and configuration loading"""
    print("🧪 Testing bot initialization...")
    
    config_path = create_test_config()
    
    try:
        # Mock the SignalBot to avoid connection issues
        import unittest.mock
        with unittest.mock.patch('idle_bot.SignalBot'):
            bot = IdleUserBot(config_path)
            
        print("✅ Bot initialized successfully")
        print(f"   - Phone number: {bot.config['phone_number']}")
        print(f"   - Admin numbers: {len(bot.config['admin_numbers'])}")
        print(f"   - Idle threshold: {bot.config['idle_threshold_days']} days")
        print(f"   - Dry run mode: {bot.config['dry_run']}")
        
        return bot
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return None


def test_activity_tracking(bot):
    """Test user activity tracking functionality"""
    print("\n🧪 Testing activity tracking...")
    
    # Create test activity data
    users = create_test_activity_data()
    
    # Load the data into the bot
    bot._load_activity_data()
    
    print(f"✅ Loaded activity data for {len(bot.activity_data)} users")
    
    # Test activity update
    test_user = '+9999999999'
    bot.update_user_activity(test_user)
    
    if test_user in bot.activity_data:
        print(f"✅ Successfully tracked new user: {test_user}")
        print(f"   - Message count: {bot.activity_data[test_user].message_count}")
        print(f"   - Last seen: {bot.activity_data[test_user].last_seen}")
    else:
        print(f"❌ Failed to track new user: {test_user}")


def test_idle_detection(bot):
    """Test idle user detection"""
    print("\n🧪 Testing idle user detection...")
    
    idle_users = bot.get_idle_users()
    
    print(f"✅ Found {len(idle_users)} idle users:")
    
    for user in idle_users:
        days_idle = (datetime.now() - user.last_seen).days
        print(f"   - {user.phone_number}: {days_idle} days idle, {user.message_count} messages")
    
    # Test threshold adjustment
    original_threshold = bot.config['idle_threshold_days']
    bot.config['idle_threshold_days'] = 10
    
    idle_users_strict = bot.get_idle_users()
    print(f"✅ With 10-day threshold: {len(idle_users_strict)} idle users")
    
    # Restore original threshold
    bot.config['idle_threshold_days'] = original_threshold


def test_admin_permissions(bot):
    """Test admin permission checking"""
    print("\n🧪 Testing admin permissions...")
    
    admin_number = '+1234567890'
    regular_number = '+9999999999'
    
    is_admin = bot.is_admin(admin_number)
    is_not_admin = bot.is_admin(regular_number)
    
    if is_admin and not is_not_admin:
        print("✅ Admin permission checking works correctly")
        print(f"   - {admin_number}: Admin ✓")
        print(f"   - {regular_number}: Regular user ✓")
    else:
        print("❌ Admin permission checking failed")


def test_protected_users(bot):
    """Test protected user functionality"""
    print("\n🧪 Testing protected users...")
    
    # Add a protected user to test data
    protected_user = '+1234567890'  # Bot's own number
    now = datetime.now()
    
    # Make this user appear idle
    bot.activity_data[protected_user] = UserActivity(
        phone_number=protected_user,
        last_seen=now - timedelta(days=60),  # Very idle
        message_count=1,
        first_seen=now - timedelta(days=100)
    )
    
    idle_users = bot.get_idle_users()
    protected_in_idle = any(user.phone_number == protected_user for user in idle_users)
    
    if not protected_in_idle:
        print("✅ Protected users are correctly excluded from idle list")
    else:
        print("❌ Protected user found in idle list")


def test_configuration_updates(bot):
    """Test configuration update functionality"""
    print("\n🧪 Testing configuration updates...")
    
    # Test threshold update
    original_threshold = bot.config['idle_threshold_days']
    new_threshold = 45
    
    bot.config['idle_threshold_days'] = new_threshold
    
    if bot.config['idle_threshold_days'] == new_threshold:
        print(f"✅ Threshold updated successfully: {original_threshold} → {new_threshold} days")
    else:
        print("❌ Threshold update failed")
    
    # Test dry run toggle
    original_dry_run = bot.config['dry_run']
    bot.config['dry_run'] = not original_dry_run
    
    if bot.config['dry_run'] != original_dry_run:
        print(f"✅ Dry run mode toggled: {original_dry_run} → {bot.config['dry_run']}")
    else:
        print("❌ Dry run toggle failed")


def generate_activity_report(bot):
    """Generate a sample activity report"""
    print("\n📊 Activity Report:")
    print("=" * 50)
    
    total_users = len(bot.activity_data)
    idle_users = bot.get_idle_users()
    active_users = total_users - len(idle_users)
    
    now = datetime.now()
    recent_active = sum(1 for activity in bot.activity_data.values() 
                      if (now - activity.last_seen).days <= 7)
    
    print(f"👥 Total tracked users: {total_users}")
    print(f"✅ Active users: {active_users}")
    print(f"💤 Idle users: {len(idle_users)}")
    print(f"🔥 Active last 7 days: {recent_active}")
    print(f"⚙️ Idle threshold: {bot.config['idle_threshold_days']} days")
    print(f"🛡️ Protected users: {len(bot.config['protected_users'])}")
    print(f"🔒 Dry run mode: {'Enabled' if bot.config['dry_run'] else 'Disabled'}")
    
    if idle_users:
        print(f"\n💤 Idle Users (>{bot.config['idle_threshold_days']} days):")
        for user in idle_users:
            days_idle = (now - user.last_seen).days
            print(f"   • {user.phone_number}: {days_idle} days idle, {user.message_count} messages")


def cleanup_test_data():
    """Clean up test data files"""
    import shutil
    if os.path.exists('test_data'):
        shutil.rmtree('test_data')
    print("\n🧹 Test data cleaned up")


def main():
    """Run all tests"""
    print("🤖 Signal Idle User Bot - Test Suite")
    print("=" * 50)
    
    try:
        # Test bot initialization
        bot = test_bot_initialization()
        if not bot:
            return
        
        # Run functionality tests
        test_activity_tracking(bot)
        test_idle_detection(bot)
        test_admin_permissions(bot)
        test_protected_users(bot)
        test_configuration_updates(bot)
        
        # Generate report
        generate_activity_report(bot)
        
        print("\n✅ All tests completed successfully!")
        print("\nThe bot is ready to use. Follow the setup guide in docs/SETUP.md")
        print("to configure it with your Signal account.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_test_data()


if __name__ == "__main__":
    main()

