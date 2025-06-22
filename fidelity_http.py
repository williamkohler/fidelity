#!/usr/bin/env python3
"""
HTTP-based Discord bot that avoids audio dependencies
This version uses Discord's HTTP API directly instead of discord.py
"""

import os
import sys
import json
import time
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import threading

load_dotenv()

# Discord HTTP API configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_API_BASE = "https://discord.com/api/v10"

# Spotify authentication setup
def create_spotify_client():
    """Create Spotify client with proper authentication"""
    try:
        # Check if we have a pre-authenticated token in environment variables
        spotify_token = os.getenv("SPOTIFY_TOKEN")
        if spotify_token:
            print("✅ Found Spotify token in environment variables!")
            try:
                # Parse the token JSON
                token_info = json.loads(spotify_token)
                auth_manager = SpotifyOAuth(
                    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                    scope="user-library-read user-read-recently-played user-read-currently-playing user-read-playback-state user-read-playback-position playlist-modify-public playlist-modify-private"
                )
                auth_manager._save_token_info(token_info)
                return spotipy.Spotify(auth_manager=auth_manager)
            except Exception as e:
                print(f"⚠️  Error using environment token: {e}")
        
        # Create OAuth manager with cache file
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-library-read user-read-recently-played user-read-currently-playing user-read-playback-state user-read-playback-position playlist-modify-public playlist-modify-private",
            cache_path=".spotify_cache",
            open_browser=False
        )
        
        # Try to get cached token first
        cached_token = auth_manager.get_cached_token()
        if cached_token:
            print("✅ Found cached Spotify token!")
            return spotipy.Spotify(auth_manager=auth_manager)
        
        # No cached token and no environment token - check if we're in a non-interactive environment
        if not sys.stdin.isatty() or os.getenv('RENDER') or os.getenv('HEROKU'):
            print("❌ No Spotify authentication found and running in non-interactive environment.")
            print("Please either:")
            print("1. Set SPOTIFY_TOKEN environment variable with your token JSON")
            print("2. Upload a .spotify_cache file to your deployment")
            print("3. Run authentication locally first")
            return None
        
        # No cached token, need to authenticate manually (only in interactive environments)
        print("🔐 No cached token found. Please authenticate with Spotify...")
        print(f"Redirect URI: {os.getenv('SPOTIFY_REDIRECT_URI')}")
        
        # Get authorization URL
        auth_url = auth_manager.get_authorize_url()
        print(f"\n📋 Please visit this URL in your browser:")
        print(f"{auth_url}")
        print("\nAfter authorization, you'll be redirected to a URL that looks like:")
        print(f"{os.getenv('SPOTIFY_REDIRECT_URI')}?code=...")
        print("\nCopy the entire URL and paste it here:")
        
        # Get the redirect URL from user
        redirect_url = input("Paste the redirect URL: ").strip()
        
        # Extract the authorization code
        if "?code=" in redirect_url:
            code = redirect_url.split("?code=")[1].split("&")[0]
            auth_manager.get_access_token(code)
            print("✅ Authentication successful!")
            return spotipy.Spotify(auth_manager=auth_manager)
        else:
            print("❌ Invalid redirect URL. Please try again.")
            return None
    
    except Exception as e:
        print(f"Error creating Spotify client: {e}")
        return None

# Initialize Spotify client
sp = create_spotify_client()

class DiscordHTTPBot:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_gateway_url(self):
        """Get the WebSocket gateway URL"""
        response = self.session.get(f"{DISCORD_API_BASE}/gateway")
        if response.status_code == 200:
            return response.json()["url"]
        else:
            raise Exception(f"Failed to get gateway URL: {response.status_code}")
    
    def send_message(self, channel_id, content, embed=None):
        """Send a message to a Discord channel"""
        data = {"content": content}
        if embed:
            data["embeds"] = [embed]
        
        response = self.session.post(
            f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
            return None
    
    def create_embed(self, title, description=None, color=0x1DB954, fields=None, thumbnail=None, footer=None):
        """Create a Discord embed"""
        embed = {
            "title": title,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if description:
            embed["description"] = description
        
        if fields:
            embed["fields"] = fields
        
        if thumbnail:
            embed["thumbnail"] = {"url": thumbnail}
        
        if footer:
            embed["footer"] = footer
        
        return embed

def handle_command(bot, channel_id, command, args):
    """Handle bot commands"""
    if command == "hello":
        bot.send_message(channel_id, "Hello, world!")
    
    elif command == "lastplayed":
        if not sp:
            bot.send_message(channel_id, "❌ Spotify client not initialized. Please check your configuration.")
            return
        
        try:
            recent_tracks = sp.current_user_recently_played(limit=1)
            
            if not recent_tracks['items']:
                bot.send_message(channel_id, "No recently played tracks found.")
                return
            
            track = recent_tracks['items'][0]['track']
            played_at = recent_tracks['items'][0]['played_at']
            
            played_time = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
            formatted_time = played_time.strftime("%Y-%m-%d %H:%M:%S")
            
            fields = [
                {"name": "Track", "value": f"**{track['name']}**", "inline": False},
                {"name": "Artist", "value": f"**{track['artists'][0]['name']}**", "inline": True},
                {"name": "Album", "value": f"**{track['album']['name']}**", "inline": True},
                {"name": "Played At", "value": f"**{formatted_time}**", "inline": False},
                {"name": "Listen on Spotify", "value": f"[Open in Spotify]({track['external_urls']['spotify']})", "inline": False}
            ]
            
            thumbnail = track['album']['images'][0]['url'] if track['album']['images'] else None
            footer = {"text": "Powered by Spotify API"}
            
            embed = bot.create_embed(
                title="🎵 Last Played Song",
                color=0x1DB954,
                fields=fields,
                thumbnail=thumbnail,
                footer=footer
            )
            
            bot.send_message(channel_id, "", embed=embed)
            
        except Exception as e:
            bot.send_message(channel_id, f"❌ Error fetching last played song: {str(e)}")
            print(f"Error in lastplayed command: {e}")
    
    elif command == "nowplaying":
        if not sp:
            bot.send_message(channel_id, "❌ Spotify client not initialized. Please check your configuration.")
            return
        
        try:
            current_track = sp.current_playback()
            
            if not current_track or not current_track['is_playing']:
                bot.send_message(channel_id, "🎵 No song is currently playing.")
                return
            
            track = current_track['item']
            
            fields = [
                {"name": "Track", "value": f"**{track['name']}**", "inline": False},
                {"name": "Artist", "value": f"**{track['artists'][0]['name']}**", "inline": True},
                {"name": "Album", "value": f"**{track['album']['name']}**", "inline": True},
                {"name": "Listen on Spotify", "value": f"[Open in Spotify]({track['external_urls']['spotify']})", "inline": False}
            ]
            
            thumbnail = track['album']['images'][0]['url'] if track['album']['images'] else None
            footer = {"text": "Powered by Spotify API"}
            
            embed = bot.create_embed(
                title="🎵 Now Playing",
                color=0x1DB954,
                fields=fields,
                thumbnail=thumbnail,
                footer=footer
            )
            
            bot.send_message(channel_id, "", embed=embed)
            
        except Exception as e:
            bot.send_message(channel_id, f"❌ Error fetching current song: {str(e)}")
            print(f"Error in nowplaying command: {e}")
    
    elif command == "spotify_status":
        if sp:
            try:
                user = sp.current_user()
                bot.send_message(channel_id, f"✅ Spotify connected! Logged in as: **{user['display_name']}**")
            except Exception as e:
                bot.send_message(channel_id, f"❌ Spotify client error: {str(e)}")
        else:
            bot.send_message(channel_id, "❌ Spotify client not initialized.")
    
    else:
        bot.send_message(channel_id, f"Unknown command: {command}")

def main():
    """Main function"""
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        sys.exit(1)
    
    print("🤖 Starting HTTP-based Discord bot...")
    
    try:
        bot = DiscordHTTPBot(DISCORD_TOKEN)
        
        # Test connection
        gateway_url = bot.get_gateway_url()
        print(f"✅ Connected to Discord gateway: {gateway_url}")
        
        if sp:
            try:
                user = sp.current_user()
                print(f"✅ Spotify connected! Logged in as: {user['display_name']}")
            except Exception as e:
                print(f"⚠️  Spotify client error: {e}")
        else:
            print("❌ Spotify client failed to initialize!")
        
        print("🎵 Bot is ready! Commands available:")
        print("- !hello")
        print("- !lastplayed")
        print("- !nowplaying")
        print("- !spotify_status")
        
        # Keep the bot running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 