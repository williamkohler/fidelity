# Deployment Guide for Fidelity Discord Bot

## The Problem: audioop Module Error

The main issue you're encountering is the `ModuleNotFoundError: No module named 'audioop'` error. This happens because:

1. **Discord.py includes voice functionality by default** - Even if your bot doesn't use voice features, importing `discord.py` triggers the import of voice-related modules
2. **audioop module is missing** - The `audioop` module is part of Python's standard library but isn't always available in containerized environments like Render
3. **System dependencies** - Audio processing requires system-level libraries that aren't installed by default

## Solutions (Try in Order)

### Solution 1: Use py-cord (Recommended)
We've updated `requirements.txt` to use `py-cord` instead of `discord.py`. This library often has better compatibility with cloud platforms.

**Files to use:**
- `requirements.txt` (already updated)
- `fidelity.py` (original file)
- `main.py` (original file)

### Solution 2: Use No-Voice Version
If Solution 1 doesn't work, use the no-voice version that avoids voice-related imports.

**Files to use:**
- `requirements_minimal.txt`
- `fidelity_no_voice.py`
- `main.py` (already updated to use no-voice version)

### Solution 3: Install System Dependencies
If you need to stick with the original `discord.py`, use the build script to install system dependencies.

**Files to use:**
- `requirements.txt` (with discord.py)
- `build.sh` (build script)
- `render.yaml` (deployment config)
- `fidelity.py` (original file)
- `main.py` (revert to original)

## Deployment Steps

### For Render Deployment:

1. **Choose your solution** from above
2. **Set environment variables** in Render:
   - `DISCORD_TOKEN`
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REDIRECT_URI`

3. **Deploy using one of these methods:**

#### Method A: Using render.yaml (Solution 3)
```bash
# Use the render.yaml file for automatic deployment
# This will use the build.sh script to install dependencies
```

#### Method B: Manual deployment (Solutions 1 & 2)
```bash
# Set build command:
pip install -r requirements.txt

# Set start command:
python main.py
```

## Troubleshooting

### If you still get audioop errors:

1. **Check Python version** - Make sure you're using Python 3.11 or later
2. **Try the no-voice version** - Use `fidelity_no_voice.py` instead
3. **Use py-cord** - Switch to `py-cord` in requirements.txt
4. **Install system dependencies** - Use the build script approach

### Common Issues:

- **Missing environment variables** - Make sure all required env vars are set in Render
- **Spotify authentication** - The bot will handle Spotify auth automatically
- **Discord token issues** - Ensure your Discord bot token is valid and has proper permissions

## File Structure

```
fidelity/
├── main.py                    # Main entry point
├── fidelity.py               # Original bot (with voice support)
├── fidelity_no_voice.py      # No-voice version
├── setup_spotify.py          # Spotify authentication
├── requirements.txt          # py-cord version
├── requirements_minimal.txt  # discord.py version
├── build.sh                  # Build script for system deps
├── render.yaml              # Render deployment config
└── DEPLOYMENT.md            # This file
```

## Testing Locally

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

This should help you successfully deploy your Discord bot to Render! 