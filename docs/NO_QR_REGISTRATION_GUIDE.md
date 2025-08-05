# No QR Code Registration Guide

This guide explains how to register your Signal bot without scanning a QR code.

## Overview

Traditional Signal registration often requires scanning a QR code with a smartphone. Our new registration process eliminates this requirement by using SMS or voice verification directly.

## Prerequisites

1. **Docker Desktop** installed and running
2. **Python 3.9+** installed
3. **A phone number** that can receive SMS or voice calls
4. **Internet connection**

## Step-by-Step Registration

### Step 1: Setup

```powershell
# Windows PowerShell
.\setup_no_qr.ps1

# Linux/Mac
./setup_no_qr.sh
```

This will:
- Start the Signal CLI REST API in Docker
- Install Python dependencies
- Prepare the environment

### Step 2: Get a Captcha Token

1. Visit: https://signalcaptchas.org/challenge/generate.html
2. Complete the captcha challenge
3. When you see the "Open Signal" button:
   - **Right-click** on the button
   - Select **"Copy link address"**
   - You'll get a URL like: `signalcaptchas://signal-captcha/5fad97ac-7d06-4e44-b18a-b950b20148ff.registration...`

### Step 3: Run Registration Script

```bash
python register_no_qr.py
```

### Step 4: Choose Registration Method

The script will show:
```
🔧 Registration Options (No QR Code Required):
1. SMS verification (most common)
2. Voice call verification
3. REST API method (advanced)
4. Exit
```

**Recommended: Choose option 1 (SMS)**

### Step 5: Enter Captcha

When prompted:
1. Paste the FULL URL you copied from the captcha page
2. The script will automatically extract the token
3. If extraction fails, it will ask for just the UUID part

### Step 6: Receive Verification Code

- **SMS**: You'll receive a text message with a 6-digit code
- **Voice**: You'll receive a phone call that speaks the code
- Write down the code carefully

### Step 7: Enter Verification Code

Type the 6-digit code when prompted. The script will verify your registration.

### Step 8: Success!

Once verified, you'll see:
```
🎉 SUCCESS! Your Signal bot is registered!
✅ Registered number: +12035442924
```

## Registration Methods Explained

### SMS Verification (Option 1)
- **Pros**: Fast, reliable, works with most numbers
- **Cons**: Requires SMS-capable number
- **Best for**: Most users

### Voice Call Verification (Option 2)
- **Pros**: Works with landlines, clear code delivery
- **Cons**: Slightly slower, must answer call
- **Best for**: When SMS isn't available

### REST API Method (Option 3)
- **Pros**: Direct API access, scriptable
- **Cons**: More technical, same captcha requirement
- **Best for**: Advanced users, automation

## Troubleshooting

### "Captcha Required" Error
- The captcha token may have expired (they expire in ~5 minutes)
- Get a fresh captcha and try again immediately

### "Invalid Captcha" Error
- Make sure you copied the ENTIRE URL, not just part of it
- The token format should be: `5fad97ac-7d06-4e44-b18a-b950b20148ff`

### SMS/Voice Not Received
1. Check the phone number format (include country code: +1 for US)
2. Try the other verification method
3. Wait 2-3 minutes - sometimes there's a delay
4. Check spam/blocked messages

### "Already Registered" Message
- This is good! Your number is already registered
- Skip registration and run: `python src/idle_bot.py`

### Rate Limiting

**If you see "rate limit exceeded" or similar errors:**

1. **Run the Rate Limit Helper**:
   ```bash
   python rate_limit_helper.py
   ```
   This tool will:
   - Check how long you need to wait
   - Suggest alternative phone numbers
   - Show a countdown timer
   - Track your registration attempts

2. **Wait Times**:
   - Signal typically enforces a 10-15 minute cooldown
   - Some rate limits can last up to 24 hours
   - The exact time depends on how many attempts were made

3. **Immediate Solutions**:
   - Use a different phone number
   - Try a virtual number service (see below)
   - Check if you already have a registered account

4. **Virtual Number Services** (to bypass rate limits):
   - **Google Voice** (free US numbers)
   - **TextNow** (free US/Canada numbers)
   - **Twilio** ($1/month, very reliable)
   - **Burner** (temporary numbers)

5. **Prevention Tips**:
   - Get a fresh captcha for each attempt
   - Complete registration within 5 minutes
   - Don't refresh or retry immediately
   - Use correct phone format (+1 for US)

### Docker Issues
```powershell
# Check if Docker is running
docker ps

# Restart the Signal container
docker-compose down
docker-compose up -d
```

## Tips for Success

1. **Have everything ready**: 
   - Phone nearby for SMS/calls
   - Captcha page open
   - Terminal ready

2. **Work quickly**: Captcha tokens expire in minutes

3. **Use SMS first**: It's the most reliable method

4. **Keep the phone number**: You'll need it for bot configuration

## Alternative: Using a Virtual Number

You can use services like:
- Google Voice (US)
- TextNow
- Twilio
- Other VoIP services

Requirements:
- Must be able to receive SMS or voice calls
- Must not be already registered with Signal

## After Registration

1. **Configure the bot**:
   ```bash
   nano config/bot_config.yaml
   ```

2. **Add bot to groups**:
   - Add the registered number to your Signal groups
   - Make the bot an admin (required for removing users)

3. **Start the bot**:
   ```bash
   python src/idle_bot.py
   ```

## Security Notes

- The registration process is the same as Signal's official process
- Your phone number is tied to the bot's Signal account
- Keep your bot's credentials secure
- The bot can only access groups it's added to

## Need Help?

If you're still having issues:

1. Check the logs:
   ```bash
   docker logs signal-api
   ```

2. Verify the service is running:
   ```bash
   curl http://localhost:8080/v1/about
   ```

3. Try the demo mode first:
   ```bash
   python demo_bot.py
   ```

Remember: No QR code scanning required! The entire process can be done from the command line.
