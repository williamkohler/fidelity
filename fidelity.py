import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
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


@bot.command()
async def nowplaying(ctx):
    """Show the currently playing song on Spotify (if any)"""
    if not sp:
        await ctx.send("❌ Spotify client not initialized. Please check your configuration.")
        return
        
    try:
        current_track = sp.current_playback()
        
        if not current_track or not current_track['is_playing']:
            await ctx.send("🎵 No song is currently playing.")
            return
        
        track = current_track['item']
        
        # Create embed for better presentation
        embed = discord.Embed(
            title="🎵 Now Playing",
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
        
        # Add progress bar
        progress_ms = current_track['progress_ms']
        duration_ms = track['duration_ms']
        progress_percent = (progress_ms / duration_ms) * 100
        
        progress_bar = "▬" * 20
        progress_pos = int((progress_percent / 100) * 20)
        progress_bar = progress_bar[:progress_pos] + "🔘" + progress_bar[progress_pos+1:]
        
        embed.add_field(
            name="Progress",
            value=f"`{progress_bar}` {progress_percent:.1f}%",
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
        error_msg = str(e)
        if "401" in error_msg:
            await ctx.send("❌ **Authentication Error**: Your Spotify token has expired or is invalid. Use `!refresh_spotify` to re-authenticate.")
        elif "403" in error_msg:
            await ctx.send("❌ **Permission Error**: The bot doesn't have permission to access your playback state. Please check your Spotify app permissions.")
        elif "404" in error_msg:
            await ctx.send("❌ **Not Found**: No active playback found. Make sure you have Spotify open and playing music.")
        else:
            await ctx.send(f"❌ Error fetching current song: {error_msg}")
        print(f"Error in nowplaying command: {e}")

@bot.command()
async def spotify_status(ctx):
    """Check if Spotify client is working"""
    if sp:
        try:
            # Try to get user profile to test connection
            user = sp.current_user()
            await ctx.send(f"✅ Spotify connected! Logged in as: **{user['display_name']}**")
        except Exception as e:
            await ctx.send(f"❌ Spotify client error: {str(e)}")
    else:
        await ctx.send("❌ Spotify client not initialized.")

@bot.command()
async def refresh_spotify(ctx):
    """Refresh Spotify authentication"""
    global sp
    try:
        # Remove cached token to force re-authentication
        if os.path.exists(".spotify_cache"):
            os.remove(".spotify_cache")
            print("Removed cached Spotify token")
        
        await ctx.send("🔄 Refreshing Spotify authentication... Please run the bot again to re-authenticate.")
        print("Spotify cache cleared. Please restart the bot to re-authenticate.")
        
    except Exception as e:
        await ctx.send(f"❌ Error refreshing Spotify: {str(e)}")
        print(f"Error refreshing Spotify: {e}")

@bot.command()
async def fplaylist(ctx, *, song_query):
    """Add a song to the Discord playlist by searching for it"""
    if not sp:
        await ctx.send("❌ Spotify client not initialized. Please check your configuration.")
        return
    
    # Playlist ID extracted from the URL
    PLAYLIST_ID = "6SgFT2PKfNovHZpP1Egow7"
    
    try:
        # Search for the song
        await ctx.send(f"🔍 Searching for: **{song_query}**")
        search_results = sp.search(q=song_query, type='track', limit=5)
        
        if not search_results['tracks']['items']:
            await ctx.send("❌ No songs found matching your search query.")
            return
        
        # Get the first (best) result
        track = search_results['tracks']['items'][0]
        
        # Add the track to the playlist
        sp.playlist_add_items(PLAYLIST_ID, [track['uri']])
        
        # Create embed for confirmation
        embed = discord.Embed(
            title="✅ Song Added to Playlist!",
            description=f"Added to [Discord Playlist](https://open.spotify.com/playlist/{PLAYLIST_ID})",
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
        
        # Add album artwork if available
        if track['album']['images']:
            embed.set_thumbnail(url=track['album']['images'][0]['url'])
        
        # Add Spotify link
        embed.add_field(
            name="Listen on Spotify",
            value=f"[Open in Spotify]({track['external_urls']['spotify']})",
            inline=False
        )
        
        embed.set_footer(text=f"Added by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            await ctx.send("❌ **Authentication Error**: Your Spotify token has expired or is invalid. Use `!refresh_spotify` to re-authenticate.")
        elif "403" in error_msg:
            await ctx.send("❌ **Permission Error**: The bot doesn't have permission to modify this playlist. Please check playlist permissions.")
        elif "404" in error_msg:
            await ctx.send("❌ **Playlist Not Found**: The playlist could not be found. Please check the playlist ID.")
        else:
            await ctx.send(f"❌ Error adding song to playlist: {error_msg}")
        print(f"Error in addtoplaylist command: {e}")

@bot.command()
async def addcurrent(ctx):
    """Add the currently playing song to the Discord playlist"""
    if not sp:
        await ctx.send("❌ Spotify client not initialized. Please check your configuration.")
        return
    
    # Playlist ID extracted from the URL
    PLAYLIST_ID = "6SgFT2PKfNovHZpP1Egow7"
    
    try:
        # Get currently playing track
        current_track = sp.current_playback()
        
        if not current_track or not current_track['is_playing']:
            await ctx.send("🎵 No song is currently playing. Use `!addtoplaylist <song name>` to search for a song instead.")
            return
        
        track = current_track['item']
        
        # Add the track to the playlist
        sp.playlist_add_items(PLAYLIST_ID, [track['uri']])
        
        # Create embed for confirmation
        embed = discord.Embed(
            title="✅ Current Song Added to Playlist!",
            description=f"Added to [Discord Playlist](https://open.spotify.com/playlist/{PLAYLIST_ID})",
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
        
        # Add album artwork if available
        if track['album']['images']:
            embed.set_thumbnail(url=track['album']['images'][0]['url'])
        
        # Add Spotify link
        embed.add_field(
            name="Listen on Spotify",
            value=f"[Open in Spotify]({track['external_urls']['spotify']})",
            inline=False
        )
        
        embed.set_footer(text=f"Added by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg:
            await ctx.send("❌ **Authentication Error**: Your Spotify token has expired or is invalid. Use `!refresh_spotify` to re-authenticate.")
        elif "403" in error_msg:
            await ctx.send("❌ **Permission Error**: The bot doesn't have permission to modify this playlist. Please check playlist permissions.")
        elif "404" in error_msg:
            await ctx.send("❌ **Playlist Not Found**: The playlist could not be found. Please check the playlist ID.")
        else:
            await ctx.send(f"❌ Error adding current song to playlist: {error_msg}")
        print(f"Error in addcurrent command: {e}")

bot.run(TOKEN)
