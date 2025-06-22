#!/usr/bin/env python3
"""
Main entry point for the Fidelity Discord bot
This script ensures Spotify authentication is set up before running the Discord bot.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name):
    """Run a Python script and return success status"""
    try:
        print(f"🔄 Running {script_name}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              check=True)
        print(f"✅ {script_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ {script_name} not found!")
        return False

def main():
    """Main function that orchestrates the setup and bot startup"""
    print("🎵 Fidelity Discord Bot")
    print("=" * 40)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Check if required files exist
    required_files = ['setup_spotify.py', 'fidelity_no_voice.py']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please make sure you're in the correct directory.")
        return False
    
    # Step 1: Run Spotify setup
    print("\n🔧 Step 1: Setting up Spotify authentication...")
    if not run_script('setup_spotify.py'):
        print("❌ Spotify setup failed. Cannot continue.")
        return False
    
    # Step 2: Run the Discord bot (using no-voice version)
    print("\n🤖 Step 2: Starting Discord bot...")
    if not run_script('fidelity_no_voice.py'):
        print("❌ Discord bot failed to start.")
        return False
    
    print("\n✅ All done! The bot should now be running.")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 