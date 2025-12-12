# Spotify Bulk Actions MCP

*Created: 2025-12-12*

## What This Is

Python MCP server for bulk Spotify operations - batch playlist creation, library exports, confidence-scored song matching.

## Playwright for This Project

Use `playwright-spotify-mcp` MCP for this project (not generic playwright).

This keeps browser sessions/logins isolated from other projects. Profile stored at `~/.playwright-spotify-mcp/`.

## Key Features

| Feature | Description |
|---------|-------------|
| Confidence scoring | HIGH/MEDIUM/LOW on song matches |
| Human-in-the-loop | Exports uncertain matches to CSV for review |
| Bulk operations | Handles 500+ songs with rate limiting |
| Library exports | Complete library data extraction |

## Tools (18)

- **Library Analysis**: `check_auth_status`, `get_followed_artists`, `get_saved_tracks`, `get_library_artists`, `get_albums_by_song_count`, `export_library_summary`
- **Search**: `search_track`, `search_track_fuzzy`, `batch_search_tracks`, `get_track_preview_url`
- **Playlists**: `create_playlist`, `add_tracks_to_playlist`, `import_and_create_playlist`, `create_playlist_from_search_results`, `add_reviewed_tracks`, `get_playlist_info`
- **Utilities**: `parse_song_list_csv`, `export_review_csv`

## Links

- **Repo**: https://github.com/khglynn/spotify-bulk-actions-mcp
- **Support**: https://buymeacoffee.com/kevinhg
