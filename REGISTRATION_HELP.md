# Signal Registration Troubleshooting Guide

## Current Issue: Captcha Registration Failing

Your Signal bot is **very close to being functional**! The main issue is with the captcha registration process. Here are several solutions to try:

## Solution 1: Try a Fresh Captcha (Recommended)

1. **Get a new captcha token:**
   - Go to: https://signalcaptchas.org/registration/generate.html
   - Solve the captcha completely
   - Right-click on "Open Signal" button and select "Copy link address"
   - Extract the captcha token from the URL

2. **Example of extracting the token:**
   ```
   Full URL: signalcaptchas://signal-captcha/5fad97ac-7d06-4e44-b18a-b950b20148ff.registration.P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   
   Extract just: 5fad97ac-7d06-4e44-b18a-b950b20148ff
   ```

3. **Register with the new token:**
   ```powershell
   docker exec signal-api signal-cli -a +12035442924 register --captcha "YOUR_NEW_TOKEN_HERE"
   ```

## Solution 2: Alternative Registration Methods

### Option A: Use Different Phone Number
If you have access to another phone number, try registering that instead.

### Option B: Link as Secondary Device
If you have Signal running on your main phone:

1. **Start linking process:**
   ```powershell
   docker exec signal-api signal-cli link -n "idle-bot"
   ```

2. **This will generate a QR code link - copy it and open in browser**

3. **Scan with your main Signal app:**
   - Settings → Linked devices → "+" → Scan QR code

## Solution 3: Manual Configuration Bypass

For development/testing, you can modify the bot to work without registration:

1. **Edit the bot configuration** to use a mock mode
2. **Test all functionality** except actual Signal messaging
3. **Integrate with real Signal later**

## Solution 4: Docker Container Reset

Sometimes the signal-cli container gets into a bad state:

```powershell
# Stop and remove current container
docker-compose down
docker volume rm docker_signal-cli-config

# Start fresh
docker-compose up -d

# Try registration again with fresh captcha
```

## What Works Already ✅

Your setup is excellent! Here's what's confirmed working:

- ✅ **Signal CLI REST API**: Running and healthy
- ✅ **Python Environment**: All dependencies installed
- ✅ **Bot Code**: Complete and tested successfully  
- ✅ **Configuration**: Properly structured
- ✅ **Docker Setup**: Working correctly
- ✅ **Demo Mode**: Bot functionality verified

## Next Steps

1. **Try Solution 1** with a fresh captcha token
2. **If that fails**, try Solution 2B (linking as secondary device)
3. **If still issues**, contact me and we'll implement Solution 3

## Demo Bot Results

The demo shows your bot will have these features once registered:
- 📊 Activity tracking and idle user detection
- 💤 Configurable idle thresholds (currently 30 days)
- 🛡️ Protected users (never removed)
- 🔒 Dry run mode (safe testing)
- 👑 Admin-only dangerous commands
- 📈 Activity statistics and reporting

## Signal Group Setup (Once Registered)

1. **Add bot to Signal group**
2. **Make bot a group admin** (required for removing users)
3. **Test with commands:**
   - `!help` - Show available commands
   - `!stats` - View activity statistics  
   - `!idle` - Check for idle users
   - `!config` - Show current settings

## Safety Features Built In

- **Dry Run Mode**: Enabled by default - shows what would happen without doing it
- **Protected Users**: Bot's own number and admins are never removed
- **Admin Controls**: Only designated admins can use removal commands
- **Activity Tracking**: Persistent storage of user activity data
- **Configurable Thresholds**: Adjust idle detection sensitivity

Your bot is essentially ready - we just need to get past the Signal registration step!
