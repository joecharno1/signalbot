# Signal Idle User Bot - Troubleshooting Guide

This guide helps you resolve common issues with the Signal Idle User Bot.

## Common Issues

### 1. Bot Not Responding to Commands

**Symptoms**: Bot doesn't respond to `!help` or other commands

**Possible Causes & Solutions**:

1. **Bot not running**
   ```bash
   # Check if bot process is running
   ps aux | grep idle_bot.py
   
   # Restart the bot
   python3 src/idle_bot.py
   ```

2. **Signal CLI REST API not running**
   ```bash
   # Check Docker container status
   cd docker
   docker-compose ps
   
   # Check logs
   docker-compose logs signal-cli-rest-api
   
   # Restart if needed
   docker-compose restart signal-cli-rest-api
   ```

3. **Phone number not registered**
   ```bash
   # Check registration status
   curl http://localhost:8080/v1/about
   
   # Should return your bot's phone number
   ```

4. **Wrong configuration**
   ```bash
   # Verify bot configuration
   cat config/bot_config.yaml
   
   # Check phone number matches registration
   ```

### 2. "Only admins can use this command" Error

**Symptoms**: Getting admin error even though you should be an admin

**Solutions**:

1. **Check admin configuration**
   ```yaml
   # In config/bot_config.yaml
   admin_numbers:
     - "+1234567890"  # Your exact phone number
   ```

2. **Verify phone number format**
   - Must include country code with + prefix
   - Example: `+1234567890` not `1234567890`
   - Check your number in Signal settings

3. **Check message source**
   ```bash
   # Look at bot logs to see what number is sending messages
   tail -f logs/bot.log
   ```

### 3. Docker Container Won't Start

**Symptoms**: signal-cli-rest-api container fails to start

**Solutions**:

1. **Check Docker logs**
   ```bash
   docker-compose logs signal-cli-rest-api
   ```

2. **Port already in use**
   ```bash
   # Check what's using port 8080
   sudo netstat -tulpn | grep 8080
   
   # Kill process or change port in docker-compose.yml
   ```

3. **Insufficient permissions**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 docker/signal-cli-config
   ```

4. **Docker daemon not running**
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

### 4. QR Code Linking Fails

**Symptoms**: Cannot link bot as secondary device

**Solutions**:

1. **Check QR code URL**
   - Visit: http://localhost:8080/v1/qrcodelink?device_name=idle-bot
   - Refresh if QR code doesn't appear

2. **Signal app issues**
   - Update Signal app to latest version
   - Try linking from different device
   - Clear Signal app cache

3. **Network connectivity**
   ```bash
   # Test API connectivity
   curl http://localhost:8080/v1/about
   
   # Check firewall settings
   sudo ufw status
   ```

### 5. Bot Can't Remove Users

**Symptoms**: Bot shows users to remove but removal fails

**Solutions**:

1. **Check bot permissions**
   - Bot must be group admin in Signal
   - Bot must have permission to remove members

2. **Dry run mode enabled**
   ```bash
   # Check if dry run is enabled
   !config
   
   # Disable dry run (CAREFUL!)
   !config dry_run false
   ```

3. **API limitations**
   - Current implementation shows removal preview only
   - Actual removal requires additional Signal API integration

### 6. Activity Data Not Saving

**Symptoms**: Bot doesn't remember user activity between restarts

**Solutions**:

1. **Check file permissions**
   ```bash
   # Ensure data directory is writable
   ls -la data/
   chmod 755 data/
   ```

2. **Disk space**
   ```bash
   # Check available disk space
   df -h
   ```

3. **Configuration path**
   ```yaml
   # In config/bot_config.yaml
   activity_file: "data/user_activity.json"  # Correct path
   ```

### 7. High Memory Usage

**Symptoms**: Bot or Docker container using too much memory

**Solutions**:

1. **Switch signal-cli mode**
   ```yaml
   # In docker-compose.yml, try different modes
   environment:
     - MODE=native  # Lower memory usage
     # - MODE=json-rpc  # Higher performance but more memory
   ```

2. **Restart containers periodically**
   ```bash
   # Add to crontab for daily restart
   0 2 * * * cd /path/to/signal-idle-bot/docker && docker-compose restart
   ```

### 8. Python Dependencies Issues

**Symptoms**: Import errors or missing modules

**Solutions**:

1. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   
   # Or with virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Python version**
   ```bash
   # Check Python version (need 3.9+)
   python3 --version
   
   # Update if needed
   sudo apt update && sudo apt install python3.11
   ```

## Debugging Tips

### Enable Debug Logging

1. **Update configuration**
   ```yaml
   # In config/bot_config.yaml
   log_level: "DEBUG"
   ```

2. **Check logs**
   ```bash
   # Run bot with verbose output
   python3 src/idle_bot.py
   ```

### Test Signal CLI Directly

1. **Test API endpoints**
   ```bash
   # Check service status
   curl http://localhost:8080/v1/about
   
   # Test sending message
   curl -X POST -H "Content-Type: application/json" \
     'http://localhost:8080/v2/send' \
     -d '{"message": "Test", "number": "+1234567890", "recipients": ["+0987654321"]}'
   ```

### Monitor Docker Containers

1. **Real-time logs**
   ```bash
   docker-compose logs -f signal-cli-rest-api
   ```

2. **Container stats**
   ```bash
   docker stats signal-cli-rest-api
   ```

## Getting Help

### Log Collection

When reporting issues, include:

1. **Bot logs**
   ```bash
   python3 src/idle_bot.py > bot.log 2>&1
   ```

2. **Docker logs**
   ```bash
   docker-compose logs signal-cli-rest-api > docker.log
   ```

3. **Configuration** (remove sensitive data)
   ```bash
   cat config/bot_config.yaml
   ```

4. **System information**
   ```bash
   uname -a
   python3 --version
   docker --version
   docker-compose --version
   ```

### Support Channels

- GitHub Issues: Report bugs and feature requests
- Documentation: Check README.md and setup guides
- Signal CLI: https://github.com/AsamK/signal-cli for signal-cli issues
- Signal CLI REST API: https://github.com/bbernhard/signal-cli-rest-api

## Prevention

### Regular Maintenance

1. **Update containers**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

2. **Backup configuration**
   ```bash
   tar -czf backup-$(date +%Y%m%d).tar.gz config/ data/
   ```

3. **Monitor logs**
   ```bash
   # Set up log rotation
   sudo logrotate -f /etc/logrotate.conf
   ```

### Health Checks

1. **Automated testing**
   ```bash
   # Create a simple health check script
   #!/bin/bash
   curl -f http://localhost:8080/v1/about || exit 1
   ```

2. **Monitoring**
   - Set up alerts for container failures
   - Monitor bot responsiveness
   - Track activity data growth

