# Fidelity Discord Bot - Deployment Guide

## Overview
This Discord bot integrates with Spotify to provide music-related commands. It can show currently playing songs, recently played tracks, and add songs to playlists.

## Files Structure
```
├── main.py                    # Entry point for Render deployment
├── fidelity_no_voice.py       # Main bot (no voice support - for Render)
├── fidelity.py                # Original bot (with voice support)
├── setup_spotify.py           # Spotify authentication setup
├── requirements_minimal.txt   # Minimal dependencies for Render
├── requirements.txt           # Full dependencies (includes voice)
├── render.yaml               # Render deployment configuration
└── build.sh                  # Build script (optional)
```

## Render Deployment

### Prerequisites
1. **Discord Bot Token**: Create a Discord application and bot at https://discord.com/developers/applications
2. **Spotify API Credentials**: Create a Spotify app at https://developer.spotify.com/dashboard
3. **Render Account**: Sign up at https://render.com

### Environment Variables
Set these in your Render service:
- `DISCORD_TOKEN`: Your Discord bot token
- `SPOTIFY_CLIENT_ID`: Your Spotify client ID
- `SPOTIFY_CLIENT_SECRET`: Your Spotify client secret
- `SPOTIFY_REDIRECT_URI`: Your Spotify redirect URI (e.g., `http://localhost:8080/callback`)

### Deployment Steps

1. **Connect your repository** to Render
2. **Create a new Web Service**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements_minimal.txt`
   - **Start Command**: `python main.py`
   - **Environment**: Python 3.11.0

4. **Set environment variables** in the Render dashboard

### Why requirements_minimal.txt?
The main `requirements.txt` includes `py-cord` which has voice dependencies that require the `audioop` module. This module is not available on Render's environment, causing the deployment to fail.

The `requirements_minimal.txt` uses `discord.py` instead, which has better support for environments without audio dependencies.

### Authentication Flow
1. The bot starts and runs `setup_spotify.py`
2. If no cached token exists, it will prompt for authentication
3. You'll need to visit the Spotify authorization URL
4. After authorization, paste the redirect URL back to complete setup

## Local Development

### With Voice Support
```bash
pip install -r requirements.txt
python fidelity.py
```

### Without Voice Support (for testing Render deployment)
```bash
pip install -r requirements_minimal.txt
python fidelity_no_voice.py
```

## Commands
- `!hello` - Basic greeting
- `!lastplayed` - Show last played song
- `!nowplaying` - Show currently playing song
- `!spotify_status` - Check Spotify connection
- `!refresh_spotify` - Refresh Spotify authentication
- `!fplaylist <song>` - Add song to playlist by search
- `!addcurrent` - Add currently playing song to playlist

## Troubleshooting

### "No module named 'audioop'" Error
This error occurs when using `py-cord` on environments without audio support (like Render). Solutions:

1. **Use `discord.py` instead** (recommended):
   - Use `requirements_minimal.txt` instead of `requirements.txt`
   - Use `fidelity_no_voice.py` instead of `fidelity.py`

2. **Install audio dependencies** (if you need voice support):
   - Use the `build.sh` script which installs system audio libraries
   - This requires more complex setup and may not work on all platforms

### Spotify Authentication Issues
- Ensure all environment variables are set correctly
- Check that your Spotify app has the correct redirect URI
- Use `!refresh_spotify` to clear cached tokens and re-authenticate

### Discord Bot Issues
- Verify your bot token is correct
- Ensure the bot has the necessary permissions in your Discord server
- Check that the bot is invited to your server with proper scopes 