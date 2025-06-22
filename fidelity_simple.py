#!/usr/bin/env python3
"""
Simple Discord bot that uses polling to avoid WebSocket dependencies
This version periodically checks for new messages and responds to commands
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

load_dotenv()

# Discord configuration
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

class SimpleDiscordBot:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_message_id = None
        self.processed_messages = set()
        
    def get_guilds(self):
        """Get list of guilds (servers) the bot is in"""
        response = self.session.get(f"{DISCORD_API_BASE}/users/@me/guilds")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get guilds: {response.status_code}")
            return []
    
    def get_channels(self, guild_id):
        """Get list of channels in a guild"""
        response = self.session.get(f"{DISCORD_API_BASE}/guilds/{guild_id}/channels")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get channels: {response.status_code}")
            return []
    
    def get_messages(self, channel_id, limit=10):
        """Get recent messages from a channel"""
        response = self.session.get(f"{DISCORD_API_BASE}/channels/{channel_id}/messages?limit={limit}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get messages: {response.status_code}")
            return []
    
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
    
    def handle_command(self, message_data):
        """Handle bot commands"""
        try:
            content = message_data.get('content', '')
            channel_id = message_data.get('channel_id')
            author = message_data.get('author', {})
            message_id = message_data.get('id')
            
            # Ignore messages from bots
            if author.get('bot', False):
                return
            
            # Ignore already processed messages
            if message_id in self.processed_messages:
                return
            
            # Add to processed messages
            self.processed_messages.add(message_id)
            
            # Keep only last 1000 processed messages to avoid memory issues
            if len(self.processed_messages) > 1000:
                self.processed_messages = set(list(self.processed_messages)[-500:])
            
            # Check if message starts with command prefix
            if not content.startswith('!'):
                return
            
            # Parse command
            parts = content.split(' ', 1)
            command = parts[0][1:].lower()  # Remove '!' and convert to lowercase
            args = parts[1] if len(parts) > 1 else ""
            
            print(f"Received command: {command} with args: {args}")
            
            # Handle commands
            if command == "hello":
                self.send_message(channel_id, "Hello, world!")
            
            elif command == "lastplayed":
                if not sp:
                    self.send_message(channel_id, "❌ Spotify client not initialized. Please check your configuration.")
                    return
                
                try:
                    recent_tracks = sp.current_user_recently_played(limit=1)
                    
                    if not recent_tracks['items']:
                        self.send_message(channel_id, "No recently played tracks found.")
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
                    
                    embed = self.create_embed(
                        title="🎵 Last Played Song",
                        color=0x1DB954,
                        fields=fields,
                        thumbnail=thumbnail,
                        footer=footer
                    )
                    
                    self.send_message(channel_id, "", embed=embed)
                    
                except Exception as e:
                    self.send_message(channel_id, f"❌ Error fetching last played song: {str(e)}")
                    print(f"Error in lastplayed command: {e}")
            
            elif command == "nowplaying":
                if not sp:
                    self.send_message(channel_id, "❌ Spotify client not initialized. Please check your configuration.")
                    return
                
                try:
                    current_track = sp.current_playback()
                    
                    if not current_track or not current_track['is_playing']:
                        self.send_message(channel_id, "🎵 No song is currently playing.")
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
                    
                    embed = self.create_embed(
                        title="🎵 Now Playing",
                        color=0x1DB954,
                        fields=fields,
                        thumbnail=thumbnail,
                        footer=footer
                    )
                    
                    self.send_message(channel_id, "", embed=embed)
                    
                except Exception as e:
                    self.send_message(channel_id, f"❌ Error fetching current song: {str(e)}")
                    print(f"Error in nowplaying command: {e}")
            
            elif command == "spotify_status":
                if sp:
                    try:
                        user = sp.current_user()
                        self.send_message(channel_id, f"✅ Spotify connected! Logged in as: **{user['display_name']}**")
                    except Exception as e:
                        self.send_message(channel_id, f"❌ Spotify client error: {str(e)}")
                else:
                    self.send_message(channel_id, "❌ Spotify client not initialized.")
            
            else:
                self.send_message(channel_id, f"Unknown command: {command}")
                
        except Exception as e:
            print(f"Error handling command: {e}")
    
    def run(self):
        """Run the bot with polling"""
        print("🤖 Starting simple Discord bot...")
        
        # Get guilds (servers) the bot is in
        guilds = self.get_guilds()
        if not guilds:
            print("❌ Bot is not in any servers!")
            return
        
        print(f"✅ Bot is in {len(guilds)} server(s)")
        
        # Get all text channels from all guilds
        all_channels = []
        for guild in guilds:
            guild_id = guild['id']
            channels = self.get_channels(guild_id)
            text_channels = [ch for ch in channels if ch['type'] == 0]  # 0 = text channel
            all_channels.extend(text_channels)
        
        if not all_channels:
            print("❌ No text channels found!")
            return
        
        print(f"✅ Monitoring {len(all_channels)} text channel(s)")
        
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
        print("\nPolling for messages every 5 seconds...")
        
        # Poll for messages
        while True:
            try:
                for channel in all_channels:
                    channel_id = channel['id']
                    messages = self.get_messages(channel_id, limit=5)
                    
                    for message in messages:
                        self.handle_command(message)
                
                time.sleep(5)  # Poll every 5 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Bot stopped by user.")
                break
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(10)  # Wait longer on error

def main():
    """Main function"""
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        sys.exit(1)
    
    try:
        bot = SimpleDiscordBot(DISCORD_TOKEN)
        bot.run()
        
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 