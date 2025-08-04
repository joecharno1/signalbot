# Signal Idle User Bot

A Signal bot that monitors group activity and can identify and remove idle users from Signal group chats.

## Features

- 📊 **Activity Tracking**: Monitors user activity in Signal groups
- 💤 **Idle Detection**: Identifies users who haven't been active for a configurable period
- 🛡️ **Protected Users**: Whitelist users who should never be removed
- 🔍 **Dry Run Mode**: Preview removals before actually removing users
- 👑 **Admin Controls**: Restrict bot commands to designated administrators
- 📈 **Statistics**: View group activity statistics and trends
- ⚙️ **Configurable**: Adjust idle thresholds and other settings via commands

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd signal-idle-bot
   ./setup.sh
   ```

2. **Configure**
   ```bash
   # Edit configuration files
   cp .env.example .env
   nano .env  # Add your phone number and admin numbers
   nano config/bot_config.yaml  # Adjust bot settings
   ```

3. **Start Signal CLI REST API**
   ```bash
   cd docker
   docker-compose up -d
   ```

4. **Register Bot Phone Number**
   - Visit http://localhost:8080/v1/qrcodelink?device_name=idle-bot
   - Scan QR code with your Signal app (Settings > Linked devices)

5. **Run the Bot**
   ```bash
   python3 src/idle_bot.py
   ```

## Commands

### Admin Commands (require admin privileges)

- `!idle` - Check for idle users
- `!remove-idle` - Remove idle users (respects dry-run setting)
- `!stats` - Show activity statistics
- `!config` - Show current configuration
- `!config threshold <days>` - Set idle threshold
- `!config dry_run <true/false>` - Toggle dry run mode

### General Commands

- `!help` - Show available commands

## Configuration

### Environment Variables (.env)
```bash
BOT_PHONE_NUMBER=+1234567890
SIGNAL_SERVICE=127.0.0.1:8080
ADMIN_NUMBERS=+1234567890,+0987654321
IDLE_THRESHOLD_DAYS=30
DRY_RUN=true
```

### Bot Configuration (config/bot_config.yaml)
```yaml
signal_service: "127.0.0.1:8080"
phone_number: "+1234567890"
admin_numbers:
  - "+1234567890"
idle_threshold_days: 30
protected_users:
  - "+1234567890"  # Bot's own number
dry_run: true
activity_file: "data/user_activity.json"
log_level: "INFO"
```

## Safety Features

- **Dry Run Mode**: Enabled by default, shows what would be removed without actually doing it
- **Protected Users**: Whitelist users who should never be removed
- **Admin Only**: Critical commands require admin privileges
- **Activity Tracking**: Persistent storage of user activity data

## Requirements

- Python 3.9+
- Docker and Docker Compose
- Signal phone number for the bot
- Admin access to Signal group

## Architecture

```
Signal Group Chat
        ↓
Signal Idle User Bot (Python)
        ↓
signalbot framework
        ↓
signal-cli-rest-api (Docker)
        ↓
signal-cli (Java)
        ↓
Signal Protocol
```

## Security Considerations

- Store configuration files securely
- Limit admin access to trusted users
- Use dry-run mode until you're confident in the setup
- Regularly backup user activity data
- Keep signal-cli-rest-api updated

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This bot is not affiliated with Signal or Open Whisper Systems. Use at your own risk and ensure compliance with Signal's terms of service and your local laws regarding automated messaging.

