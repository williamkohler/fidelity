#!/usr/bin/env python3
"""
Spotify Token Generator for Render Deployment
Run this script locally to generate a token JSON that can be used as SPOTIFY_TOKEN environment variable.
"""

import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

def generate_token():
    """Generate a Spotify token and output it as JSON"""
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
            scope="user-library-read user-read-recently-played user-read-currently-playing user-read-playback-state user-read-playback-position playlist-modify-public playlist-modify-private",
            cache_path=".spotify_cache",
            open_browser=False
        )
        
        # Check if we have a cached token
        cached_token = auth_manager.get_cached_token()
        if cached_token:
            print("✅ Found cached Spotify token!")
            sp = spotipy.Spotify(auth_manager=auth_manager)
            user = sp.current_user()
            print(f"Logged in as: {user['display_name']}")
        else:
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
            else:
                print("❌ Invalid redirect URL. Please try again.")
                return False
        
        # Get the current token info
        token_info = auth_manager.get_cached_token()
        if token_info:
            print("\n🎉 Token generated successfully!")
            print("\n📋 Copy this JSON and set it as the SPOTIFY_TOKEN environment variable on Render:")
            print("=" * 60)
            print(json.dumps(token_info, indent=2))
            print("=" * 60)
            print("\n💡 Instructions for Render:")
            print("1. Copy the JSON above")
            print("2. In your Render dashboard, go to your service")
            print("3. Go to Environment → Environment Variables")
            print("4. Add a new variable:")
            print("   - Key: SPOTIFY_TOKEN")
            print("   - Value: [paste the JSON here]")
            print("5. Save and redeploy your application")
            
            return True
        else:
            print("❌ Failed to get token info")
            return False
        
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        return False

if __name__ == "__main__":
    print("🎵 Spotify Token Generator for Render")
    print("=" * 40)
    
    if generate_token():
        print("\n✅ Token generation completed successfully!")
    else:
        print("\n❌ Token generation failed. Please check your configuration.") 