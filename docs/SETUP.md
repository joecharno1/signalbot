# Signal Idle User Bot - Detailed Setup Guide

This guide walks you through setting up the Signal Idle User Bot step by step.

## Prerequisites

### System Requirements
- Linux, macOS, or Windows with WSL2
- Python 3.9 or higher
- Docker and Docker Compose
- Internet connection
- Signal account with a phone number

### Signal Requirements
- A dedicated phone number for the bot (can be a secondary number)
- Admin access to the Signal group you want to manage
- Signal app installed on your primary device

## Step 1: Initial Setup

1. **Download the Bot**
   ```bash
   git clone <repository-url>
   cd signal-idle-bot
   ```

2. **Run Setup Script**
   ```bash
   ./setup.sh
   ```
   This will:
   - Create necessary directories
   - Copy configuration templates
   - Install Python dependencies

## Step 2: Configuration

### 2.1 Environment Configuration

1. **Copy and edit environment file**
   ```bash
   cp .env.example .env
   nano .env
   ```

2. **Update the following values**:
   ```bash
   # Your bot's phone number (must be different from your personal number)
   BOT_PHONE_NUMBER=+1234567890
   
   # Admin phone numbers (who can control the bot)
   ADMIN_NUMBERS=+1234567890,+0987654321
   
   # How many days of inactivity before considering a user idle
   IDLE_THRESHOLD_DAYS=30
   
   # Safety mode - set to false only when you're ready for real removals
   DRY_RUN=true
   ```

### 2.2 Bot Configuration

1. **Edit bot configuration**
   ```bash
   nano config/bot_config.yaml
   ```

2. **Update key settings**:
   ```yaml
   # Bot's phone number (same as in .env)
   phone_number: "+1234567890"
   
   # Admin numbers (who can use bot commands)
   admin_numbers:
     - "+1234567890"  # Your number
     - "+0987654321"  # Other admins
   
   # Users who should never be removed (even if idle)
   protected_users:
     - "+1234567890"  # Bot's own number
     - "+0987654321"  # Other protected users
   
   # Safety setting - keep true until ready for real removals
   dry_run: true
   
   # Days of inactivity before considering user idle
   idle_threshold_days: 30
   ```

## Step 3: Start Signal CLI REST API

1. **Start the Docker service**
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Verify it's running**
   ```bash
   docker-compose logs signal-cli-rest-api
   curl http://localhost:8080/v1/about
   ```

## Step 4: Register Bot Phone Number

### 4.1 Link as Secondary Device (Recommended)

1. **Open the QR code link**
   - Visit: http://localhost:8080/v1/qrcodelink?device_name=idle-bot
   - A QR code will appear

2. **Link with Signal app**
   - Open Signal on your phone
   - Go to Settings > Linked devices
   - Tap the "+" button
   - Scan the QR code

3. **Verify linking**
   ```bash
   curl http://localhost:8080/v1/about
   ```
   Should show your phone number is registered.

### 4.2 Register New Number (Alternative)

If you have a separate phone number for the bot:

1. **Register the number**
   ```bash
   curl -X POST "http://localhost:8080/v1/register/+1234567890"
   ```

2. **Verify with SMS code**
   ```bash
   curl -X POST "http://localhost:8080/v1/register/+1234567890/verify/123456"
   ```

## Step 5: Test the Bot

1. **Start the bot**
   ```bash
   cd ..  # Back to project root
   python3 src/idle_bot.py
   ```

2. **Test in Signal**
   - Add the bot to your Signal group
   - Send `!help` to see available commands
   - Try `!stats` to see if the bot responds

## Step 6: Configure Group Permissions

1. **Make bot a group admin** (required for removing users)
   - In Signal group settings
   - Add bot as admin
   - Grant permission to remove members

2. **Test idle detection**
   ```
   !idle          # Check for idle users
   !stats         # View activity statistics
   !config        # Show current settings
   ```

## Step 7: Production Setup

### 7.1 Disable Dry Run Mode

⚠️ **IMPORTANT**: Only do this when you're confident the bot is working correctly!

1. **Update configuration**
   ```bash
   nano config/bot_config.yaml
   ```
   Change: `dry_run: false`

2. **Or use command**
   Send in Signal: `!config dry_run false`

### 7.2 Set Up as Service (Optional)

Create a systemd service for automatic startup:

1. **Create service file**
   ```bash
   sudo nano /etc/systemd/system/signal-idle-bot.service
   ```

2. **Add service configuration**
   ```ini
   [Unit]
   Description=Signal Idle User Bot
   After=network.target docker.service
   Requires=docker.service
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/signal-idle-bot
   ExecStart=/usr/bin/python3 src/idle_bot.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**
   ```bash
   sudo systemctl enable signal-idle-bot
   sudo systemctl start signal-idle-bot
   sudo systemctl status signal-idle-bot
   ```

## Verification Checklist

- [ ] Docker containers are running
- [ ] Bot phone number is registered/linked
- [ ] Bot responds to `!help` command
- [ ] Admin commands work for admin users
- [ ] Non-admin users cannot use admin commands
- [ ] `!idle` command shows idle users (if any)
- [ ] `!stats` command shows activity data
- [ ] Bot is added to target Signal group
- [ ] Bot has admin permissions in group
- [ ] Configuration files are properly secured

## Next Steps

1. **Monitor Activity**: Let the bot run for a few days to collect activity data
2. **Review Idle Users**: Use `!idle` to see who would be affected
3. **Adjust Settings**: Fine-tune idle threshold and protected users
4. **Test Dry Run**: Verify the bot identifies the right users
5. **Go Live**: Disable dry run mode when ready

## Security Best Practices

- Keep configuration files secure and backed up
- Regularly update signal-cli-rest-api Docker image
- Monitor bot logs for unusual activity
- Use strong, unique phone number for the bot
- Limit admin access to trusted users only
- Test thoroughly before disabling dry run mode

## Troubleshooting

If you encounter issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems and solutions.

