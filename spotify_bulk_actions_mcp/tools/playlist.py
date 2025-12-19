"""
Playlist creation and management tools for MCP.
"""

import csv
from io import StringIO
from typing import Any, Dict, List, Optional

from ..spotify_client import spotify_client
from .search import batch_search_tracks, parse_song_list_csv


def create_playlist(
    name: str,
    description: str = "",
    public: bool = False,
) -> Dict[str, Any]:
    """
    Create a new Spotify playlist.

    Args:
        name: Playlist name
        description: Playlist description
        public: Whether playlist is public (default False)

    Returns:
        Created playlist info
    """
    playlist = spotify_client.create_playlist(
        name=name,
        description=description,
        public=public,
    )

    return {
        "id": playlist["id"],
        "uri": playlist["uri"],
        "name": playlist["name"],
        "url": playlist["external_urls"]["spotify"],
        "public": playlist["public"],
    }


def add_tracks_to_playlist(
    playlist_id: str,
    track_uris: List[str],
) -> Dict[str, Any]:
    """
    Add tracks to a playlist.

    Handles batching automatically (Spotify allows max 100 per request).

    Args:
        playlist_id: Playlist ID (not URI)
        track_uris: List of Spotify track URIs

    Returns:
        Result with count added
    """
    # Filter out any invalid URIs
    valid_uris = [uri for uri in track_uris if uri and uri.startswith("spotify:track:")]

    if not valid_uris:
        return {
            "success": False,
            "error": "No valid track URIs provided",
            "tracks_added": 0,
        }

    spotify_client.add_tracks_to_playlist(playlist_id, valid_uris)

    return {
        "success": True,
        "playlist_id": playlist_id,
        "tracks_added": len(valid_uris),
    }


def create_playlist_from_search_results(
    name: str,
    batch_results: Dict[str, Any],
    include_confidence: str = "high",
    description: str = "",
    public: bool = False,
) -> Dict[str, Any]:
    """
    Create a playlist from batch search results.

    Args:
        name: Playlist name
        batch_results: Results from batch_search_tracks
        include_confidence: Which confidence levels to include:
            - "high": Only high confidence (>= 90%)
            - "high_medium": High and medium (>= 70%)
            - "all": All matches (use with caution)
        description: Playlist description
        public: Whether playlist is public

    Returns:
        Created playlist info with track counts
    """
    # Collect URIs based on confidence setting
    track_uris = []

    if include_confidence in ["high", "high_medium", "all"]:
        for match in batch_results.get("high_confidence", []):
            track_uris.append(match["uri"])

    if include_confidence in ["high_medium", "all"]:
        for match in batch_results.get("medium_confidence", []):
            track_uris.append(match["uri"])

    if include_confidence == "all":
        for match in batch_results.get("low_confidence", []):
            track_uris.append(match["uri"])

    if not track_uris:
        return {
            "success": False,
            "error": "No tracks to add based on confidence filter",
        }

    # Check playlist size limit
    if len(track_uris) > 10000:
        return {
            "success": False,
            "error": f"Too many tracks ({len(track_uris)}). Spotify max is 10,000 per playlist.",
            "suggestion": "Split into multiple playlists",
        }

    # Create playlist
    playlist = create_playlist(name=name, description=description, public=public)

    # Add tracks
    result = add_tracks_to_playlist(playlist["id"], track_uris)

    return {
        "success": True,
        "playlist": playlist,
        "tracks_added": result["tracks_added"],
        "confidence_filter": include_confidence,
        "skipped": {
            "medium": len(batch_results.get("medium_confidence", []))
            if include_confidence == "high"
            else 0,
            "low": len(batch_results.get("low_confidence", []))
            if include_confidence != "all"
            else 0,
            "not_found": len(batch_results.get("not_found", [])),
        },
    }


def import_and_create_playlist(
    name: str,
    csv_content: str,
    include_confidence: str = "high",
    description: str = "",
    public: bool = False,
) -> Dict[str, Any]:
    """
    Full workflow: Parse CSV, search all tracks, create playlist.

    This is the main tool for bulk playlist creation.

    Args:
        name: Playlist name
        csv_content: CSV with columns: title, artist
        include_confidence: "high", "high_medium", or "all"
        description: Playlist description
        public: Whether playlist is public

    Returns:
        Complete results including search stats and playlist info
    """
    # Parse CSV
    songs = parse_song_list_csv(csv_content)

    if not songs:
        return {
            "success": False,
            "error": "No songs found in CSV. Expected columns: title, artist",
        }

    # Batch search
    search_results = batch_search_tracks(songs)

    # Create playlist with matching tracks
    playlist_result = create_playlist_from_search_results(
        name=name,
        batch_results=search_results,
        include_confidence=include_confidence,
        description=description,
        public=public,
    )

    return {
        "search_summary": search_results["summary"],
        "playlist_result": playlist_result,
        "needs_review": {
            "medium_confidence": search_results["medium_confidence"]
            if include_confidence == "high"
            else [],
            "low_confidence": search_results["low_confidence"],
            "not_found": search_results["not_found"],
        },
    }


def add_reviewed_tracks(
    playlist_id: str,
    reviewed_csv: str,
) -> Dict[str, Any]:
    """
    Add tracks from a reviewed CSV to an existing playlist.

    The CSV should have an 'action' column:
    - 'approve': Add the matched track
    - 'reject': Skip this track
    - spotify:track:xxx: Use this specific URI instead

    Args:
        playlist_id: Existing playlist ID
        reviewed_csv: Reviewed CSV content

    Returns:
        Result with counts
    """
    reader = csv.DictReader(StringIO(reviewed_csv))

    approved_uris = []
    rejected = 0
    custom = 0

    for row in reader:
        action = row.get("action", "").strip()

        if action == "approve":
            uri = row.get("spotify_uri", "")
            if uri:
                approved_uris.append(uri)
        elif action == "reject" or action == "":
            rejected += 1
        elif action.startswith("spotify:track:"):
            approved_uris.append(action)
            custom += 1

    if not approved_uris:
        return {
            "success": False,
            "tracks_added": 0,
            "rejected": rejected,
            "error": "No tracks approved in review",
        }

    result = add_tracks_to_playlist(playlist_id, approved_uris)

    return {
        "success": True,
        "tracks_added": result["tracks_added"],
        "custom_replacements": custom,
        "rejected": rejected,
        "playlist_id": playlist_id,
    }


def get_playlist_info(playlist_id: str) -> Dict[str, Any]:
    """
    Get information about a playlist.

    Args:
        playlist_id: Playlist ID

    Returns:
        Playlist details
    """
    try:
        playlist = spotify_client.client.playlist(playlist_id)
        tracks = spotify_client.get_playlist_tracks(playlist_id)

        return {
            "id": playlist["id"],
            "name": playlist["name"],
            "description": playlist.get("description", ""),
            "url": playlist["external_urls"]["spotify"],
            "owner": playlist["owner"]["display_name"],
            "public": playlist["public"],
            "track_count": len(tracks),
            "followers": playlist["followers"]["total"],
        }
    except Exception as e:
        return {
            "error": str(e),
        }


def update_playlist(
    playlist_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    public: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update playlist details (name, description, public status).

    Args:
        playlist_id: Playlist ID
        name: New playlist name (optional)
        description: New playlist description (optional)
        public: New public status (optional)

    Returns:
        Updated playlist info
    """
    try:
        # Update the playlist
        spotify_client.update_playlist_details(
            playlist_id=playlist_id,
            name=name,
            description=description,
            public=public,
        )

        # Return updated info
        return get_playlist_info(playlist_id)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =============================================================================
# Playlist Analysis Tools
# =============================================================================


def get_playlist_tracks(playlist_id: str) -> Dict[str, Any]:
    """
    Get all tracks from a playlist.

    Args:
        playlist_id: Playlist ID

    Returns:
        List of tracks with details
    """
    try:
        playlist = spotify_client.client.playlist(playlist_id, fields="name,id")
        tracks = spotify_client.get_playlist_tracks(playlist_id)

        simplified = []
        for i, item in enumerate(tracks):
            track = item.get("track")
            if track is None:
                continue

            simplified.append({
                "position": i + 1,
                "name": track["name"],
                "id": track["id"],
                "uri": track["uri"],
                "artists": [{"name": a["name"], "id": a["id"]} for a in track["artists"]],
                "album": track["album"]["name"],
                "added_at": item.get("added_at"),
                "added_by": item.get("added_by", {}).get("id"),
            })

        return {
            "playlist_name": playlist["name"],
            "playlist_id": playlist_id,
            "track_count": len(simplified),
            "tracks": simplified,
        }
    except Exception as e:
        return {"error": str(e)}


def export_playlist_to_csv(playlist_id: str) -> Dict[str, Any]:
    """
    Export a playlist to CSV format.

    Args:
        playlist_id: Playlist ID

    Returns:
        CSV content for the playlist
    """
    result = get_playlist_tracks(playlist_id)
    if "error" in result:
        return result

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["position", "title", "artist", "album", "spotify_uri", "added_at"])

    for track in result["tracks"]:
        artist_names = ", ".join(a["name"] for a in track["artists"])
        writer.writerow([
            track["position"],
            track["name"],
            artist_names,
            track["album"],
            track["uri"],
            track.get("added_at", ""),
        ])

    return {
        "playlist_name": result["playlist_name"],
        "track_count": result["track_count"],
        "csv_content": output.getvalue(),
    }


def compare_playlists(playlist_id_1: str, playlist_id_2: str) -> Dict[str, Any]:
    """
    Compare two playlists to find overlap and differences.

    Args:
        playlist_id_1: First playlist ID
        playlist_id_2: Second playlist ID

    Returns:
        Comparison results with shared tracks and unique tracks
    """
    result1 = get_playlist_tracks(playlist_id_1)
    result2 = get_playlist_tracks(playlist_id_2)

    if "error" in result1:
        return {"error": f"Playlist 1: {result1['error']}"}
    if "error" in result2:
        return {"error": f"Playlist 2: {result2['error']}"}

    # Build sets of track IDs
    tracks1 = {t["id"]: t for t in result1["tracks"]}
    tracks2 = {t["id"]: t for t in result2["tracks"]}

    ids1 = set(tracks1.keys())
    ids2 = set(tracks2.keys())

    shared_ids = ids1 & ids2
    only_in_1 = ids1 - ids2
    only_in_2 = ids2 - ids1

    return {
        "playlist_1": {
            "name": result1["playlist_name"],
            "id": playlist_id_1,
            "track_count": len(tracks1),
        },
        "playlist_2": {
            "name": result2["playlist_name"],
            "id": playlist_id_2,
            "track_count": len(tracks2),
        },
        "comparison": {
            "shared_count": len(shared_ids),
            "only_in_playlist_1": len(only_in_1),
            "only_in_playlist_2": len(only_in_2),
        },
        "shared_tracks": [
            {"name": tracks1[tid]["name"], "artists": tracks1[tid]["artists"], "id": tid}
            for tid in shared_ids
        ],
        "only_in_playlist_1": [
            {"name": tracks1[tid]["name"], "artists": tracks1[tid]["artists"], "id": tid}
            for tid in only_in_1
        ],
        "only_in_playlist_2": [
            {"name": tracks2[tid]["name"], "artists": tracks2[tid]["artists"], "id": tid}
            for tid in only_in_2
        ],
    }


def find_duplicate_tracks(playlist_id: str) -> Dict[str, Any]:
    """
    Find duplicate tracks in a playlist.

    Args:
        playlist_id: Playlist ID

    Returns:
        List of duplicate tracks with their positions
    """
    result = get_playlist_tracks(playlist_id)
    if "error" in result:
        return result

    # Track occurrences by track ID
    occurrences: Dict[str, List[Dict]] = {}
    for track in result["tracks"]:
        tid = track["id"]
        if tid not in occurrences:
            occurrences[tid] = []
        occurrences[tid].append({
            "position": track["position"],
            "name": track["name"],
            "artists": track["artists"],
            "uri": track["uri"],
        })

    # Find duplicates
    duplicates = [
        {
            "track_id": tid,
            "name": entries[0]["name"],
            "artists": entries[0]["artists"],
            "occurrences": len(entries),
            "positions": [e["position"] for e in entries],
            "uri": entries[0]["uri"],
        }
        for tid, entries in occurrences.items()
        if len(entries) > 1
    ]

    return {
        "playlist_name": result["playlist_name"],
        "playlist_id": playlist_id,
        "total_tracks": result["track_count"],
        "duplicate_count": len(duplicates),
        "duplicates": duplicates,
    }


def remove_duplicate_tracks(
    playlist_id: str,
    confirm: bool = False,
) -> Dict[str, Any]:
    """
    Remove duplicate tracks from a playlist, keeping the first occurrence.

    For safety, this returns a preview unless confirm=True.

    Args:
        playlist_id: Playlist ID
        confirm: Set to True to actually remove duplicates

    Returns:
        Preview or result of duplicate removal
    """
    duplicates_result = find_duplicate_tracks(playlist_id)
    if "error" in duplicates_result:
        return duplicates_result

    if duplicates_result["duplicate_count"] == 0:
        return {
            "success": True,
            "message": "No duplicates found in playlist",
            "removed": 0,
        }

    # Collect URIs to remove (all except first occurrence)
    to_remove = []
    for dup in duplicates_result["duplicates"]:
        # Skip first position, remove the rest
        for pos in dup["positions"][1:]:
            to_remove.append(dup["uri"])

    if not confirm:
        return {
            "preview": True,
            "playlist_name": duplicates_result["playlist_name"],
            "duplicates_found": duplicates_result["duplicate_count"],
            "tracks_to_remove": len(to_remove),
            "duplicates": duplicates_result["duplicates"],
            "message": "Set confirm=True to remove duplicates (keeps first occurrence)",
        }

    # Remove duplicates
    spotify_client.remove_tracks_from_playlist(playlist_id, to_remove)

    return {
        "success": True,
        "playlist_name": duplicates_result["playlist_name"],
        "removed": len(to_remove),
        "duplicates_fixed": duplicates_result["duplicate_count"],
    }


# =============================================================================
# Playlist Editing Tools
# =============================================================================


def remove_tracks_from_playlist(
    playlist_id: str,
    track_uris: List[str],
    confirm: bool = False,
) -> Dict[str, Any]:
    """
    Remove specific tracks from a playlist.

    For safety, this returns a preview unless confirm=True.

    Args:
        playlist_id: Playlist ID
        track_uris: List of Spotify track URIs to remove
        confirm: Set to True to actually remove

    Returns:
        Preview or result of removal
    """
    if not track_uris:
        return {"success": False, "error": "No track URIs provided"}

    # Validate URIs
    valid_uris = [uri for uri in track_uris if uri and uri.startswith("spotify:track:")]
    if not valid_uris:
        return {"success": False, "error": "No valid track URIs provided"}

    if not confirm:
        return {
            "preview": True,
            "playlist_id": playlist_id,
            "tracks_to_remove": len(valid_uris),
            "track_uris": valid_uris,
            "message": "Set confirm=True to proceed with removal",
        }

    spotify_client.remove_tracks_from_playlist(playlist_id, valid_uris)

    return {
        "success": True,
        "playlist_id": playlist_id,
        "removed": len(valid_uris),
        "track_uris": valid_uris,
    }


def reorder_playlist_tracks(
    playlist_id: str,
    range_start: int,
    insert_before: int,
    range_length: int = 1,
) -> Dict[str, Any]:
    """
    Move tracks within a playlist.

    Args:
        playlist_id: Playlist ID
        range_start: Position of first track to move (0-indexed)
        insert_before: Position to insert before (0-indexed)
        range_length: Number of tracks to move (default 1)

    Returns:
        Result of reorder operation
    """
    try:
        spotify_client.reorder_playlist_tracks(
            playlist_id=playlist_id,
            range_start=range_start,
            insert_before=insert_before,
            range_length=range_length,
        )

        return {
            "success": True,
            "playlist_id": playlist_id,
            "moved_from": range_start,
            "moved_to": insert_before,
            "tracks_moved": range_length,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
