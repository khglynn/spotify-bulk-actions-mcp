#!/usr/bin/env python3
"""
Spotify MCP Server

A Model Context Protocol server for Spotify library analysis
and playlist management.

Run with: spotify-bulk-actions-mcp
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastmcp import FastMCP

from spotify_bulk_actions_mcp.utils.auth import is_authenticated, get_spotify_client
from spotify_bulk_actions_mcp.tools import library, search, playlist

# Create the MCP server
mcp = FastMCP(
    "Spotify Library Manager",
    instructions="Analyze your Spotify library and create playlists from song lists",
)


# =============================================================================
# Authentication & User Info
# =============================================================================


@mcp.tool()
def check_auth_status() -> dict:
    """
    Check if Spotify authentication is set up and working.

    Returns current user info if authenticated.
    """
    if not is_authenticated():
        return {
            "authenticated": False,
            "message": "Not authenticated. Run 'python setup_auth.py' to authenticate.",
        }

    try:
        client = get_spotify_client()
        if client is None:
            return {
                "authenticated": False,
                "message": "Failed to get Spotify client. Check credentials.",
            }

        user = client.current_user()
        return {
            "authenticated": True,
            "user": {
                "id": user["id"],
                "display_name": user.get("display_name"),
                "email": user.get("email"),
                "country": user.get("country"),
                "product": user.get("product"),  # premium, free, etc.
            },
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
        }


# =============================================================================
# Library Analysis Tools
# =============================================================================


@mcp.tool()
def get_top_artists(
    time_range: str = "medium_term",
    limit: int = 50,
) -> dict:
    """
    Get your top artists based on listening history.

    Great for understanding your music taste and finding festival lineups.

    Args:
        time_range: Time period:
            - "short_term": Last 4 weeks
            - "medium_term": Last 6 months (default)
            - "long_term": All time
        limit: Number of results (max 50)

    Returns:
        Ranked list of your top artists with genres and popularity.
    """
    return library.get_top_artists(time_range=time_range, limit=limit)


@mcp.tool()
def get_top_tracks(
    time_range: str = "medium_term",
    limit: int = 50,
) -> dict:
    """
    Get your top tracks based on listening history.

    Args:
        time_range: Time period:
            - "short_term": Last 4 weeks
            - "medium_term": Last 6 months (default)
            - "long_term": All time
        limit: Number of results (max 50)

    Returns:
        Ranked list of your top tracks with artist and album info.
    """
    return library.get_top_tracks(time_range=time_range, limit=limit)


@mcp.tool()
def get_recently_played(limit: int = 50) -> dict:
    """
    Get your recently played tracks.

    Args:
        limit: Number of results (max 50)

    Returns:
        List of recently played tracks with timestamps.
    """
    return library.get_recently_played(limit=limit)


@mcp.tool()
def get_followed_artists(use_cache: bool = True) -> dict:
    """
    Get all artists you follow on Spotify.

    Args:
        use_cache: Use cached data if available (faster, default True)

    Returns:
        List of followed artists with names, genres, popularity, and images.
    """
    return library.get_followed_artists(use_cache=use_cache)


@mcp.tool()
def get_saved_tracks(use_cache: bool = True) -> dict:
    """
    Get all your liked/saved songs on Spotify.

    Note: This may take 1-2 minutes for large libraries (10k songs).

    Args:
        use_cache: Use cached data if available (faster, default True)

    Returns:
        List of saved tracks with title, artist, album, and metadata.
    """
    return library.get_saved_tracks(use_cache=use_cache)


@mcp.tool()
def get_library_artists(use_cache: bool = True) -> dict:
    """
    Get unique artists from your saved songs, sorted by song count.

    This shows artists you have saved songs from (even if not followed),
    ranked by how many songs you've saved.

    Args:
        use_cache: Use cached data if available

    Returns:
        Artists with their saved song counts, sorted most-to-least.
    """
    return library.get_library_artists(use_cache=use_cache)


@mcp.tool()
def get_albums_by_song_count(min_songs: int = 6, use_cache: bool = True) -> dict:
    """
    Find albums where you have N or more saved songs.

    Great for finding albums worth buying on vinyl!

    Args:
        min_songs: Minimum saved songs to include album (default 6)
        use_cache: Use cached data if available

    Returns:
        Albums meeting the threshold, with artwork URLs and song lists.
    """
    return library.get_albums_by_song_count(min_songs=min_songs, use_cache=use_cache)


@mcp.tool()
def export_library_summary(use_cache: bool = True) -> dict:
    """
    Export a complete summary of your Spotify library.

    Includes:
    - Followed artists
    - Top artists by saved song count
    - Albums with most saved songs

    Args:
        use_cache: Use cached data if available

    Returns:
        Complete library summary with statistics.
    """
    return library.export_library_summary(use_cache=use_cache)


# =============================================================================
# Library Modification Tools
# =============================================================================


@mcp.tool()
def follow_artists(artist_ids: list) -> dict:
    """
    Follow artists on Spotify.

    Args:
        artist_ids: List of Spotify artist IDs to follow

    Returns:
        Result with count of artists followed.

    Example:
        follow_artists(["0OdUWJ0sBjDrqHygGUXeCF"])  # Follow Band of Horses
    """
    return library.follow_artists(artist_ids=artist_ids)


@mcp.tool()
def unfollow_artists(artist_ids: list, confirm: bool = False) -> dict:
    """
    Unfollow artists on Spotify.

    For safety, returns a preview unless confirm=True.

    Args:
        artist_ids: List of Spotify artist IDs to unfollow
        confirm: Set to True to actually unfollow (default False for preview)

    Returns:
        Preview of what will be unfollowed, or result if confirmed.
    """
    return library.unfollow_artists(artist_ids=artist_ids, confirm=confirm)


@mcp.tool()
def save_tracks(track_ids: list) -> dict:
    """
    Save tracks to your Spotify library (like/heart them).

    Args:
        track_ids: List of Spotify track IDs to save

    Returns:
        Result with count of tracks saved.

    Example:
        save_tracks(["3n3Ppam7vgaVa1iaRUc9Lp"])  # Save "Mr. Brightside"
    """
    return library.save_tracks(track_ids=track_ids)


@mcp.tool()
def unsave_tracks(track_ids: list, confirm: bool = False) -> dict:
    """
    Remove tracks from your Spotify library.

    For safety, returns a preview unless confirm=True.

    Args:
        track_ids: List of Spotify track IDs to remove
        confirm: Set to True to actually remove (default False for preview)

    Returns:
        Preview of what will be removed, or result if confirmed.
    """
    return library.unsave_tracks(track_ids=track_ids, confirm=confirm)


# =============================================================================
# Search Tools
# =============================================================================


@mcp.tool()
def search_track(title: str, artist: str, limit: int = 5) -> dict:
    """
    Search for a single track and get matches with confidence scores.

    Args:
        title: Track title
        artist: Artist name
        limit: Max results to return (default 5)

    Returns:
        Search results ranked by confidence, with preview URLs.
    """
    return search.search_track(title=title, artist=artist, limit=limit)


@mcp.tool()
def search_track_fuzzy(title: str, artist: str, limit: int = 10) -> dict:
    """
    Broader fuzzy search when exact match fails.

    Tries multiple strategies:
    1. Exact title + artist
    2. Title only
    3. Simplified title (removing parentheses, etc.)

    Args:
        title: Track title
        artist: Artist name
        limit: Max results per strategy

    Returns:
        Combined results from all search strategies.
    """
    return search.search_track_fuzzy(title=title, artist=artist, limit=limit)


@mcp.tool()
def batch_search_tracks(songs: list, delay_seconds: float = 0.2) -> dict:
    """
    Search for multiple tracks with confidence scoring.

    Categorizes results:
    - HIGH (>= 90%): Safe to auto-add
    - MEDIUM (70-89%): Should review
    - LOW (< 70%): Needs attention
    - NOT FOUND: No results

    Args:
        songs: List of {"title": "...", "artist": "..."} dicts
        delay_seconds: Delay between API calls (default 0.2s for rate limiting)

    Returns:
        Categorized results with statistics.

    Example input:
        [
            {"title": "Bohemian Rhapsody", "artist": "Queen"},
            {"title": "Hotel California", "artist": "Eagles"}
        ]
    """
    return search.batch_search_tracks(songs=songs, delay_seconds=delay_seconds)


@mcp.tool()
def get_track_preview_url(track_uri: str) -> dict:
    """
    Get the 30-second preview URL for a track.

    Args:
        track_uri: Spotify track URI (e.g., "spotify:track:xxx")

    Returns:
        Track info with preview URL (if available).
    """
    return search.get_track_preview_url(track_uri=track_uri)


# =============================================================================
# Playlist Tools
# =============================================================================


@mcp.tool()
def create_playlist(name: str, description: str = "", public: bool = False) -> dict:
    """
    Create a new Spotify playlist.

    Args:
        name: Playlist name
        description: Playlist description
        public: Whether playlist is public (default False)

    Returns:
        Created playlist info with URL.
    """
    return playlist.create_playlist(name=name, description=description, public=public)


@mcp.tool()
def add_tracks_to_playlist(playlist_id: str, track_uris: list) -> dict:
    """
    Add tracks to an existing playlist.

    Handles batching automatically (Spotify max 100 per request).

    Args:
        playlist_id: Playlist ID (not URI)
        track_uris: List of Spotify track URIs

    Returns:
        Result with count of tracks added.
    """
    return playlist.add_tracks_to_playlist(playlist_id=playlist_id, track_uris=track_uris)


@mcp.tool()
def create_playlist_from_search_results(
    name: str,
    batch_results: dict,
    include_confidence: str = "high",
    description: str = "",
    public: bool = False,
) -> dict:
    """
    Create a playlist from batch search results.

    Args:
        name: Playlist name
        batch_results: Results from batch_search_tracks
        include_confidence: Which confidence levels to include:
            - "high": Only >= 90% matches (safest)
            - "high_medium": >= 70% matches
            - "all": All matches (use with caution)
        description: Playlist description
        public: Whether playlist is public

    Returns:
        Created playlist info with statistics.
    """
    return playlist.create_playlist_from_search_results(
        name=name,
        batch_results=batch_results,
        include_confidence=include_confidence,
        description=description,
        public=public,
    )


@mcp.tool()
def import_and_create_playlist(
    name: str,
    csv_content: str,
    include_confidence: str = "high",
    description: str = "",
    public: bool = False,
) -> dict:
    """
    Full workflow: Parse song list CSV, search all tracks, create playlist.

    This is the main tool for bulk playlist creation from a list of songs.

    CSV format:
        title,artist
        Bohemian Rhapsody,Queen
        Hotel California,Eagles

    Args:
        name: Playlist name
        csv_content: CSV content with columns: title, artist
        include_confidence: "high", "high_medium", or "all"
        description: Playlist description
        public: Whether playlist is public

    Returns:
        Complete results including search stats, created playlist, and songs needing review.
    """
    return playlist.import_and_create_playlist(
        name=name,
        csv_content=csv_content,
        include_confidence=include_confidence,
        description=description,
        public=public,
    )


@mcp.tool()
def add_reviewed_tracks(playlist_id: str, reviewed_csv: str) -> dict:
    """
    Add tracks from a reviewed CSV to an existing playlist.

    Use this after reviewing uncertain matches from a batch search.

    The CSV should have an 'action' column:
    - 'approve': Add the matched track
    - 'reject': Skip this track
    - spotify:track:xxx: Use this specific URI instead

    Args:
        playlist_id: Existing playlist ID
        reviewed_csv: Reviewed CSV content with 'action' column

    Returns:
        Result with counts of added/rejected tracks.
    """
    return playlist.add_reviewed_tracks(playlist_id=playlist_id, reviewed_csv=reviewed_csv)


@mcp.tool()
def get_playlist_info(playlist_id: str) -> dict:
    """
    Get information about a playlist.

    Args:
        playlist_id: Playlist ID

    Returns:
        Playlist details including name, track count, and URL.
    """
    return playlist.get_playlist_info(playlist_id=playlist_id)


@mcp.tool()
def get_playlist_tracks(playlist_id: str) -> dict:
    """
    Get all tracks from a playlist.

    Args:
        playlist_id: Playlist ID

    Returns:
        List of all tracks with artist, album, and position info.
    """
    return playlist.get_playlist_tracks(playlist_id=playlist_id)


@mcp.tool()
def export_playlist_to_csv(playlist_id: str) -> dict:
    """
    Export a playlist to CSV format.

    Great for backing up playlists or sharing song lists.

    Args:
        playlist_id: Playlist ID

    Returns:
        CSV content with title, artist, album, and Spotify URI.
    """
    return playlist.export_playlist_to_csv(playlist_id=playlist_id)


@mcp.tool()
def compare_playlists(playlist_id_1: str, playlist_id_2: str) -> dict:
    """
    Compare two playlists to find shared and unique tracks.

    Args:
        playlist_id_1: First playlist ID
        playlist_id_2: Second playlist ID

    Returns:
        Comparison showing shared tracks and tracks unique to each playlist.
    """
    return playlist.compare_playlists(
        playlist_id_1=playlist_id_1,
        playlist_id_2=playlist_id_2,
    )


@mcp.tool()
def find_duplicate_tracks(playlist_id: str) -> dict:
    """
    Find duplicate tracks in a playlist.

    Args:
        playlist_id: Playlist ID

    Returns:
        List of duplicate tracks with their positions.
    """
    return playlist.find_duplicate_tracks(playlist_id=playlist_id)


@mcp.tool()
def remove_duplicate_tracks(playlist_id: str, confirm: bool = False) -> dict:
    """
    Remove duplicate tracks from a playlist, keeping the first occurrence.

    For safety, returns a preview unless confirm=True.

    Args:
        playlist_id: Playlist ID
        confirm: Set to True to actually remove duplicates

    Returns:
        Preview of duplicates to remove, or result if confirmed.
    """
    return playlist.remove_duplicate_tracks(playlist_id=playlist_id, confirm=confirm)


@mcp.tool()
def remove_tracks_from_playlist(
    playlist_id: str,
    track_uris: list,
    confirm: bool = False,
) -> dict:
    """
    Remove specific tracks from a playlist.

    For safety, returns a preview unless confirm=True.

    Args:
        playlist_id: Playlist ID
        track_uris: List of Spotify track URIs to remove
        confirm: Set to True to actually remove

    Returns:
        Preview of what will be removed, or result if confirmed.
    """
    return playlist.remove_tracks_from_playlist(
        playlist_id=playlist_id,
        track_uris=track_uris,
        confirm=confirm,
    )


@mcp.tool()
def reorder_playlist_tracks(
    playlist_id: str,
    range_start: int,
    insert_before: int,
    range_length: int = 1,
) -> dict:
    """
    Move tracks within a playlist.

    Args:
        playlist_id: Playlist ID
        range_start: Position of first track to move (0-indexed)
        insert_before: Position to insert before (0-indexed)
        range_length: Number of tracks to move (default 1)

    Returns:
        Result of the reorder operation.
    """
    return playlist.reorder_playlist_tracks(
        playlist_id=playlist_id,
        range_start=range_start,
        insert_before=insert_before,
        range_length=range_length,
    )


# =============================================================================
# Utility Tools
# =============================================================================


@mcp.tool()
def parse_song_list_csv(csv_content: str) -> dict:
    """
    Parse a CSV of songs into a structured list.

    Use this to validate your CSV before batch searching.

    Expected CSV format:
        title,artist
        Song Name,Artist Name

    Args:
        csv_content: CSV content as string

    Returns:
        Parsed list of songs ready for batch_search_tracks.
    """
    songs = search.parse_song_list_csv(csv_content)
    return {
        "count": len(songs),
        "songs": songs,
        "ready_for_search": len(songs) > 0,
    }


@mcp.tool()
def export_review_csv(batch_results: dict) -> dict:
    """
    Export medium/low confidence matches to a CSV for human review.

    Args:
        batch_results: Results from batch_search_tracks

    Returns:
        CSV content to review and edit.
    """
    csv_content = search.export_review_csv(batch_results)
    return {
        "csv_content": csv_content,
        "instructions": (
            "Edit the 'action' column:\n"
            "- 'approve': Add the matched track\n"
            "- 'reject': Skip this track\n"
            "- spotify:track:xxx: Use a different track URI\n"
            "Then use add_reviewed_tracks() to add to playlist."
        ),
    }


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Entry point for the MCP server."""
    print("Starting Spotify MCP Server...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
