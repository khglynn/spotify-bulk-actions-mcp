# Spotify Bulk Actions MCP

*Created: 2025-12-12* · **Last verified:** 2026-11-13

## What This Is

Python MCP server for bulk Spotify operations - batch playlist creation, library exports, confidence-scored song matching.

## Key Features

| Feature | Description |
|---------|-------------|
| Confidence scoring | HIGH/MEDIUM/LOW on song matches |
| Human-in-the-loop | Exports uncertain matches to CSV for review |
| Bulk operations | Handles 500+ songs with rate limiting |
| Library exports | Complete library data extraction |

## Tools (33)

- **Library Analysis**: `check_auth_status`, `get_followed_artists`, `get_saved_tracks`, `get_library_artists`, `get_albums_by_song_count`, `export_library_summary`
- **Listening Insights**: `get_top_artists`, `get_top_tracks`, `get_recently_played`
- **Bulk Library Actions**: `follow_artists`, `unfollow_artists`, `save_tracks`, `unsave_tracks`
- **Search**: `search_track`, `search_track_fuzzy`, `batch_search_tracks`, `get_track_preview_url`
- **Playlist Creation**: `create_playlist`, `add_tracks_to_playlist`, `import_and_create_playlist`, `create_playlist_from_search_results`, `add_reviewed_tracks`
- **Playlist Management**: `get_playlist_info`, `update_playlist`, `get_playlist_tracks`, `export_playlist_to_csv`, `compare_playlists`, `find_duplicate_tracks`, `remove_duplicate_tracks`, `remove_tracks_from_playlist`, `reorder_playlist_tracks`
- **Utilities**: `parse_song_list_csv`, `export_review_csv`

## API Notes

- Migrated for Spotify's February 2026 Web API changes: playlist create uses
  `POST /me/playlists` (`current_user_playlist_create`), playlist reads use
  `playlist_items`. Old per-user endpoints still respond for this grandfathered
  app but are slated for removal — don't reintroduce them.
- Development Mode limits (2026): max 5 allowlisted users per Client ID, owner
  must hold Premium, search `limit` capped at 10 (Spotify's
  [migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide);
  the cap of 10 is from third-party trackers, checked 2026-11-13).
- All 33 tools carry `readOnlyHint`/`destructiveHint` annotations (20 read-only /
  9 additive / 4 destructive) — keep new tools annotated.
- The `export_*` and CSV tools return their content inline and write no files, so
  they work the same hosted. The only disk writes are the `.spotify_cache/` folder.

## Hosted mode

`MCP_TRANSPORT=stdio` (the default) is the local Claude Code registration;
`MCP_TRANSPORT=http` (set in the `Dockerfile`) serves the hosted claude.ai
connector on Cloud Run. Deploys run only from the parent folder's
`../deploy/deploy-spotify.sh`, which builds from a fresh clone of GitHub main,
so merge first.

## Links

- **Repo**: https://github.com/khglynn/spotify-bulk-actions-mcp
- **Support**: https://buymeacoffee.com/kevinhg
