"""
Search and matching tools for MCP.
Includes fuzzy matching and confidence scoring for bulk operations.
"""

import csv
import json
import sys
import time
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from thefuzz import fuzz

from ..spotify_client import spotify_client


def calculate_match_confidence(
    query_title: str,
    query_artist: str,
    result_title: str,
    result_artists: List[str],
) -> float:
    """
    Calculate confidence score for a track match.

    Returns:
        Float between 0 and 1
    """
    # Title similarity (most important)
    title_score = fuzz.ratio(query_title.lower(), result_title.lower()) / 100

    # Artist similarity (check against all artists on the track)
    artist_scores = [
        fuzz.ratio(query_artist.lower(), artist.lower()) / 100
        for artist in result_artists
    ]
    artist_score = max(artist_scores) if artist_scores else 0

    # Weighted average (title slightly more important)
    confidence = (title_score * 0.55) + (artist_score * 0.45)

    return round(confidence, 3)


def search_track(
    title: str,
    artist: str,
    limit: int = 5,
) -> Dict[str, Any]:
    """
    Search for a single track and return matches with confidence scores.

    Args:
        title: Track title
        artist: Artist name
        limit: Max results to return

    Returns:
        Search results with confidence scores
    """
    results = spotify_client.search_track_by_name_artist(title, artist, limit=limit)

    matches = []
    for track in results:
        artists = [a["name"] for a in track["artists"]]
        confidence = calculate_match_confidence(title, artist, track["name"], artists)

        matches.append({
            "title": track["name"],
            "artists": artists,
            "album": track["album"]["name"],
            "uri": track["uri"],
            "id": track["id"],
            "confidence": confidence,
            "preview_url": track.get("preview_url"),
            "duration_ms": track["duration_ms"],
            "popularity": track.get("popularity", 0),
        })

    # Sort by confidence
    matches.sort(key=lambda x: x["confidence"], reverse=True)

    best_match = matches[0] if matches else None

    return {
        "query": {"title": title, "artist": artist},
        "best_match": best_match,
        "all_matches": matches,
        "match_found": best_match is not None and best_match["confidence"] >= 0.7,
    }


def search_track_fuzzy(
    title: str,
    artist: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Broader fuzzy search when exact match fails.

    Tries multiple search strategies:
    1. Exact title + artist
    2. Title only
    3. Simplified title (remove parentheses, etc.)

    Args:
        title: Track title
        artist: Artist name
        limit: Max results per strategy

    Returns:
        Combined results from all strategies
    """
    all_matches = []
    seen_uris = set()

    # Strategy 1: Exact search
    results1 = spotify_client.search_track_by_name_artist(title, artist, limit=limit)
    for track in results1:
        if track["uri"] not in seen_uris:
            seen_uris.add(track["uri"])
            artists = [a["name"] for a in track["artists"]]
            confidence = calculate_match_confidence(title, artist, track["name"], artists)
            all_matches.append({
                "title": track["name"],
                "artists": artists,
                "album": track["album"]["name"],
                "uri": track["uri"],
                "id": track["id"],
                "confidence": confidence,
                "preview_url": track.get("preview_url"),
                "strategy": "exact",
            })

    # Strategy 2: Title only (broader)
    results2 = spotify_client.search_track(f'track:"{title}"', limit=limit)
    for track in results2:
        if track["uri"] not in seen_uris:
            seen_uris.add(track["uri"])
            artists = [a["name"] for a in track["artists"]]
            confidence = calculate_match_confidence(title, artist, track["name"], artists)
            all_matches.append({
                "title": track["name"],
                "artists": artists,
                "album": track["album"]["name"],
                "uri": track["uri"],
                "id": track["id"],
                "confidence": confidence,
                "preview_url": track.get("preview_url"),
                "strategy": "title_only",
            })

    # Strategy 3: Simplified title
    import re
    simplified_title = re.sub(r"\([^)]*\)", "", title).strip()
    simplified_title = re.sub(r"\[[^\]]*\]", "", simplified_title).strip()

    if simplified_title != title:
        results3 = spotify_client.search_track_by_name_artist(
            simplified_title, artist, limit=limit
        )
        for track in results3:
            if track["uri"] not in seen_uris:
                seen_uris.add(track["uri"])
                artists = [a["name"] for a in track["artists"]]
                confidence = calculate_match_confidence(
                    title, artist, track["name"], artists
                )
                all_matches.append({
                    "title": track["name"],
                    "artists": artists,
                    "album": track["album"]["name"],
                    "uri": track["uri"],
                    "id": track["id"],
                    "confidence": confidence,
                    "preview_url": track.get("preview_url"),
                    "strategy": "simplified",
                })

    # Sort by confidence
    all_matches.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "query": {"title": title, "artist": artist},
        "matches": all_matches[:limit],
        "strategies_tried": ["exact", "title_only", "simplified"],
    }


def batch_search_tracks(
    songs: List[Dict[str, str]],
    delay_seconds: float = 0.2,
) -> Dict[str, Any]:
    """
    Search for multiple tracks with confidence scoring.

    Categorizes results into HIGH (auto-add), MEDIUM (review), LOW (needs attention).

    Args:
        songs: List of {"title": "...", "artist": "..."} dicts
        delay_seconds: Delay between API calls (default 0.2s)

    Returns:
        Categorized results with statistics
    """
    high_confidence = []  # >= 0.90
    medium_confidence = []  # 0.70 - 0.89
    low_confidence = []  # < 0.70
    not_found = []

    total = len(songs)

    for i, song in enumerate(songs):
        title = song.get("title", "")
        artist = song.get("artist", "")

        if not title:
            not_found.append({"query": song, "reason": "Empty title"})
            continue

        print(f"Searching {i + 1}/{total}: {title} - {artist}", file=sys.stderr)

        try:
            result = search_track(title, artist, limit=3)

            if result["best_match"]:
                match = result["best_match"]
                match["original_query"] = song

                confidence = match["confidence"]
                if confidence >= 0.90:
                    high_confidence.append(match)
                elif confidence >= 0.70:
                    medium_confidence.append(match)
                else:
                    low_confidence.append(match)
            else:
                not_found.append({"query": song, "reason": "No results"})

        except Exception as e:
            not_found.append({"query": song, "reason": str(e)})

        time.sleep(delay_seconds)

    return {
        "summary": {
            "total_searched": total,
            "high_confidence": len(high_confidence),
            "medium_confidence": len(medium_confidence),
            "low_confidence": len(low_confidence),
            "not_found": len(not_found),
        },
        "high_confidence": high_confidence,
        "medium_confidence": medium_confidence,
        "low_confidence": low_confidence,
        "not_found": not_found,
    }


def parse_song_list_csv(csv_content: str) -> List[Dict[str, str]]:
    """
    Parse a CSV of songs into a list.

    Expected format:
    title,artist
    Song Name,Artist Name

    Args:
        csv_content: CSV content as string

    Returns:
        List of {"title": "...", "artist": "..."} dicts
    """
    songs = []
    reader = csv.DictReader(StringIO(csv_content))

    for row in reader:
        # Handle various column name formats
        title = row.get("title") or row.get("Title") or row.get("song") or row.get("Song") or ""
        artist = row.get("artist") or row.get("Artist") or row.get("band") or row.get("Band") or ""

        if title.strip():
            songs.append({
                "title": title.strip(),
                "artist": artist.strip(),
            })

    return songs


def export_review_csv(batch_results: Dict[str, Any]) -> str:
    """
    Export medium and low confidence matches to a CSV for review.

    Args:
        batch_results: Results from batch_search_tracks

    Returns:
        CSV content as string
    """
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "original_title",
        "original_artist",
        "matched_title",
        "matched_artists",
        "confidence",
        "spotify_uri",
        "preview_url",
        "action",  # User fills in: approve, reject, or replacement_uri
    ])

    # Medium confidence (likely correct, just verify)
    for match in batch_results.get("medium_confidence", []):
        query = match.get("original_query", {})
        writer.writerow([
            query.get("title", ""),
            query.get("artist", ""),
            match["title"],
            ", ".join(match["artists"]),
            match["confidence"],
            match["uri"],
            match.get("preview_url", ""),
            "approve",  # Default suggestion
        ])

    # Low confidence (needs attention)
    for match in batch_results.get("low_confidence", []):
        query = match.get("original_query", {})
        writer.writerow([
            query.get("title", ""),
            query.get("artist", ""),
            match["title"],
            ", ".join(match["artists"]),
            match["confidence"],
            match["uri"],
            match.get("preview_url", ""),
            "",  # User must decide
        ])

    # Not found
    for item in batch_results.get("not_found", []):
        query = item.get("query", {})
        writer.writerow([
            query.get("title", ""),
            query.get("artist", ""),
            "",
            "",
            0,
            "",
            "",
            "",  # User must find manually
        ])

    return output.getvalue()


def get_track_preview_url(track_uri: str) -> Dict[str, Any]:
    """
    Get the preview URL for a track.

    Args:
        track_uri: Spotify track URI (spotify:track:xxx)

    Returns:
        Track info with preview URL
    """
    # Extract track ID from URI
    track_id = track_uri.split(":")[-1]

    try:
        track = spotify_client.client.track(track_id)
        return {
            "title": track["name"],
            "artists": [a["name"] for a in track["artists"]],
            "preview_url": track.get("preview_url"),
            "has_preview": track.get("preview_url") is not None,
            "external_url": track["external_urls"].get("spotify"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "has_preview": False,
        }
