# Discord Spotify Bot

A Discord bot that integrates with Spotify to show your last played song and currently playing track.

## Features

- `!lastplayed` - Shows the last song you played on Spotify
- `!nowplaying` - Shows the currently playing song (if any)
- `!spotify_status` - Check if Spotify connection is working
- `!hello` - Basic hello command

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DISCORD_TOKEN=your_discord_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### 3. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token and add it to your `.env` file
5. Enable the necessary intents (Message Content Intent)
6. Invite the bot to your server with these permissions:
   - Send Messages
   - Embed Links
   - Read Message History

### 4. Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy the Client ID and Client Secret
4. Add `http://127.0.0.1:8888/callback` to your app's Redirect URIs
5. Save the settings

### 5. Spotify Authentication

Run the setup script to authenticate with Spotify:

```bash
python setup_spotify.py
```

This will:
- Check your environment variables
- Open a browser for Spotify authentication
- Cache your authentication token for future use

### 6. Run the Bot

```bash
python fidelity.py
```

## Usage

Once the bot is running and connected to your Discord server, you can use these commands:

- `!lastplayed` - Shows your last played song with album artwork and Spotify link
- `!nowplaying` - Shows currently playing song with progress bar
- `!spotify_status` - Check if Spotify connection is working
- `!hello` - Basic test command

## Troubleshooting

### Authentication Issues
- Make sure your redirect URI matches exactly: `http://127.0.0.1:8888/callback`
- If browser doesn't open automatically, manually visit the authorization URL
- Check that your Spotify app has the correct redirect URI in the dashboard

### Bot Not Responding
- Ensure the bot has the necessary permissions in your Discord server
- Check that the bot token is correct in your `.env` file
- Verify that Message Content Intent is enabled in the Discord Developer Portal

### Spotify Commands Not Working
- Run `!spotify_status` to check if Spotify is connected
- If not connected, run `python setup_spotify.py` again
- Make sure you have an active Spotify account and have played music recently

## File Structure

```
fidelity/
├── fidelity.py          # Main Discord bot
├── setup_spotify.py     # Spotify authentication helper
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # Environment variables (create this)
└── .spotify_cache      # Spotify authentication cache (auto-generated)
```

## Permissions Required

The bot needs these Discord permissions:
- Send Messages
- Embed Links
- Read Message History

The Spotify integration requires these scopes:
- `user-library-read`
- `user-read-recently-played`
- `user-read-currently-playing` 