# Modified version that avoids voice-related imports
import os
import sys

# Set environment variable to disable voice support
os.environ['DISCORD_DISABLE_VOICE'] = '1'

try:
    import discord
    from discord.ext import commands
except ImportError as e:
    print(f"❌ Failed to import discord: {e}")
    print("This might be due to missing audio dependencies.")
    sys.exit(1)

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import webbrowser
import time

load_dotenv()  # Load environment variables from .env

# Spotify authentication setup
def create_spotify_client():
    """Create Spotify client with proper authentication"""
    try:
        # Create OAuth manager with cache file
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-library-read user-read-recently-played user-read-currently-playing user-read-playback-state user-read-playback-position playlist-modify-public playlist-modify-private",
            cache_path=".spotify_cache",
            open_browser=False  # Don't try to open browser automatically
        )
        
        # Try to get cached token first
        cached_token = auth_manager.get_cached_token()
        if cached_token:
            print("✅ Found cached Spotify token!")
            return spotipy.Spotify(auth_manager=auth_manager)
        
        # No cached token, need to authenticate manually
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

TOKEN = os.getenv("DISCORD_TOKEN")

# Create intents object
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    if sp:
        try:
            user = sp.current_user()
            print(f"✅ Spotify connected! Logged in as: {user['display_name']}")
        except Exception as e:
            print(f"⚠️  Spotify client error: {e}")
    else:
        print("❌ Spotify client failed to initialize!")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

@bot.command()
async def lastplayed(ctx):
    """Show the last song played on Spotify"""
    if not sp:
        await ctx.send("❌ Spotify client not initialized. Please check your configuration.")
        return
        
    try:
        # Get recently played tracks (limit=1 to get the most recent)
        recent_tracks = sp.current_user_recently_played(limit=1)
        
        if not recent_tracks['items']:
            await ctx.send("No recently played tracks found.")
            return
        
        track = recent_tracks['items'][0]['track']
        played_at = recent_tracks['items'][0]['played_at']
        
        # Format the played time
        played_time = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
        formatted_time = played_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create embed for better presentation
        embed = discord.Embed(
            title="🎵 Last Played Song",
            color=0x1DB954,  # Spotify green
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Track",
            value=f"**{track['name']}**",
            inline=False
        )
        
        embed.add_field(
            name="Artist",
            value=f"**{track['artists'][0]['name']}**",
            inline=True
        )
        
        embed.add_field(
            name="Album",
            value=f"**{track['album']['name']}**",
            inline=True
        )
        
        embed.add_field(
            name="Played At",
            value=f"**{formatted_time}**",
            inline=False
        )
        
        # Add album artwork if available
        if track['album']['images']:
            embed.set_thumbnail(url=track['album']['images'][0]['url'])
        
        # Add Spotify link
        embed.add_field(
            name="Listen on Spotify",
            value=f"[Open in Spotify]({track['external_urls']['spotify']})",
            inline=False
        )
        
        embed.set_footer(text="Powered by Spotify API")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error fetching last played song: {str(e)}")
        print(f"Error in lastplayed command: {e}")

# Add the rest of your commands here...
# (Copy the remaining commands from the original fidelity.py)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        sys.exit(1)
    
    print("🤖 Starting Discord bot...")
    bot.run(TOKEN) 