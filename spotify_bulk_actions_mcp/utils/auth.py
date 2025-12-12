"""
OAuth authentication utilities for Spotify API.
Uses spotipy's built-in OAuth flow with local caching.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Required scopes for all our operations
SCOPES = [
    "user-library-read",      # Read saved tracks/albums
    "user-library-modify",    # Save/unsave tracks/albums
    "user-follow-read",       # Read followed artists
    "user-follow-modify",     # Follow/unfollow artists
    "playlist-read-private",  # Read private playlists
    "playlist-read-collaborative",
    "playlist-modify-public", # Create/edit public playlists
    "playlist-modify-private", # Create/edit private playlists
    "user-read-private",      # Read user profile
    "user-top-read",          # Read top artists/tracks
    "user-read-recently-played",  # Read recently played tracks
]

def get_cache_path() -> Path:
    """Get the path to the token cache file."""
    cache_dir = Path(__file__).parent.parent.parent / ".spotify_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "token.cache"


def get_spotify_client(interactive: bool = False) -> Optional[spotipy.Spotify]:
    """
    Get an authenticated Spotify client.

    Args:
        interactive: If True, will open browser for auth if needed.
                    If False, returns None if not authenticated.

    Returns:
        Authenticated Spotify client or None
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback")

    if not client_id or not client_secret:
        if interactive:
            print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set", file=sys.stderr)
            print("Copy .env.example to .env and fill in your credentials", file=sys.stderr)
        return None

    cache_path = get_cache_path()

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=" ".join(SCOPES),
        cache_path=str(cache_path),
        open_browser=interactive,
    )

    # Check if we have a valid token
    token_info = auth_manager.get_cached_token()

    if not token_info and not interactive:
        return None

    if not token_info and interactive:
        # This will open browser and wait for callback
        auth_manager.get_access_token(as_dict=False)

    return spotipy.Spotify(auth_manager=auth_manager)


def is_authenticated() -> bool:
    """Check if we have valid cached credentials."""
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback")

    if not client_id or not client_secret:
        return False

    cache_path = get_cache_path()
    if not cache_path.exists():
        return False

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=" ".join(SCOPES),
        cache_path=str(cache_path),
        open_browser=False,
    )

    token_info = auth_manager.get_cached_token()
    return token_info is not None


def clear_auth_cache():
    """Clear the authentication cache (for re-auth)."""
    cache_path = get_cache_path()
    if cache_path.exists():
        cache_path.unlink()
        print("Authentication cache cleared.", file=sys.stderr)
