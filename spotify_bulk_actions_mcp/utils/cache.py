"""
Local caching utilities for library data.
Reduces API calls by caching library snapshots.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


def get_cache_dir() -> Path:
    """Get the cache directory path."""
    cache_dir = Path(__file__).parent.parent.parent / ".spotify_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def save_cache(key: str, data: Any, ttl_hours: int = 24) -> None:
    """
    Save data to cache with expiration.

    Args:
        key: Cache key (filename without extension)
        data: Data to cache (must be JSON serializable)
        ttl_hours: Time-to-live in hours
    """
    cache_dir = get_cache_dir()
    cache_file = cache_dir / f"{key}.json"

    cache_entry = {
        "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
        "cached_at": datetime.now().isoformat(),
        "data": data,
    }

    with open(cache_file, "w") as f:
        json.dump(cache_entry, f, indent=2)

    print(f"Cached {key} (expires in {ttl_hours}h)", file=sys.stderr)


def load_cache(key: str) -> Optional[Any]:
    """
    Load data from cache if not expired.

    Args:
        key: Cache key

    Returns:
        Cached data or None if expired/missing
    """
    cache_dir = get_cache_dir()
    cache_file = cache_dir / f"{key}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r") as f:
            cache_entry = json.load(f)

        expires_at = datetime.fromisoformat(cache_entry["expires_at"])
        if datetime.now() > expires_at:
            print(f"Cache expired for {key}", file=sys.stderr)
            return None

        return cache_entry["data"]
    except (json.JSONDecodeError, KeyError):
        return None


def clear_cache(key: Optional[str] = None) -> None:
    """
    Clear cache entries.

    Args:
        key: Specific key to clear, or None for all
    """
    cache_dir = get_cache_dir()

    if key:
        cache_file = cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
            print(f"Cleared cache for {key}", file=sys.stderr)
    else:
        for cache_file in cache_dir.glob("*.json"):
            if cache_file.name != "token.cache":
                cache_file.unlink()
        print("Cleared all cache entries", file=sys.stderr)
