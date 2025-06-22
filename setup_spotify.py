#!/usr/bin/env python3
"""
Spotify Authentication Setup Script
Run this script to authenticate with Spotify before running the Discord bot.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

def setup_spotify():
    """Setup Spotify authentication"""
    load_dotenv()
    
    # Check if environment variables are set
    required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease add these to your .env file and try again.")
        return False
    
    try:
        # Create OAuth manager
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-library-read user-read-recently-played user-read-currently-playing user-read-playback-state user-read-playback-position",
            cache_path=".spotify_cache",
            open_browser=False  # Don't try to open browser automatically
        )
        
        # Check if we have a cached token
        cached_token = auth_manager.get_cached_token()
        if cached_token:
            print("✅ Found cached Spotify token!")
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            print(f"Logged in as: {user['display_name']}")
            return True
        
        # No cached token, need to authenticate
        print("🔐 No cached token found. Starting Spotify authentication...")
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
            
            # Test the connection
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            print(f"✅ Successfully authenticated as: {user['display_name']}")
            print("🎉 Spotify setup complete! You can now run the Discord bot.")
            
            return True
        else:
            print("❌ Invalid redirect URL. Please try again.")
            return False
        
    except Exception as e:
        print(f"❌ Error during Spotify setup: {e}")
        return False

if __name__ == "__main__":
    print("🎵 Spotify Authentication Setup")
    print("=" * 40)
    
    if setup_spotify():
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check your configuration.") 