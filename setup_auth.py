#!/usr/bin/env python3
"""
One-time authentication setup for Spotify MCP Server.

Run this script to authenticate with Spotify:
    python setup_auth.py

This will:
1. Check for credentials in .env file
2. Open a browser for Spotify login
3. Save the authentication token locally
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print("Error: .env file not found!")
    print("")
    print("To set up credentials:")
    print("  1. Copy .env.example to .env")
    print("  2. Edit .env with your Spotify API credentials")
    print("  3. Run this script again")
    print("")
    print("Get credentials at: https://developer.spotify.com/dashboard")
    sys.exit(1)

load_dotenv(env_path)

import os

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

if not client_id or not client_secret:
    print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
    sys.exit(1)

if client_id == "your_client_id_here":
    print("Error: Please replace placeholder values in .env with your actual credentials")
    sys.exit(1)

print("=" * 60)
print("Spotify MCP Server - Authentication Setup")
print("=" * 60)
print("")
print("This will open a browser window for you to log in to Spotify.")
print("After logging in, you'll be redirected back and authentication will complete.")
print("")
print("Press Enter to continue (or Ctrl+C to cancel)...")

try:
    input()
except KeyboardInterrupt:
    print("\nCancelled.")
    sys.exit(0)

from spotify_bulk_actions_mcp.utils.auth import get_spotify_client, is_authenticated, SCOPES

print("")
print("Opening browser for Spotify login...")
print("")

# This will open browser and wait for callback
client = get_spotify_client(interactive=True)

if client is None:
    print("Error: Authentication failed!")
    sys.exit(1)

# Verify it worked
try:
    user = client.current_user()
    print("")
    print("=" * 60)
    print("✓ Authentication successful!")
    print("=" * 60)
    print("")
    print(f"  Logged in as: {user.get('display_name', user['id'])}")
    print(f"  User ID: {user['id']}")
    print(f"  Account type: {user.get('product', 'unknown')}")
    print("")
    print("Scopes authorized:")
    for scope in SCOPES:
        print(f"  - {scope}")
    print("")
    print("You can now use the Spotify MCP Server!")
    print("")
    print("To test, run:")
    print("  spotify-bulk-actions-mcp")
    print("")

except Exception as e:
    print(f"Error verifying authentication: {e}")
    sys.exit(1)
