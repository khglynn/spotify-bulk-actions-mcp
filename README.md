<p align="center">
  <img src="logo.png" alt="Spotify Bulk Actions MCP" width="200">
</p>

# Spotify Bulk Actions MCP

<!-- mcp-name: io.github.khglynn/spotify-bulk-actions-mcp -->

A Model Context Protocol (MCP) server for bulk Spotify operations - **batch playlist creation, library exports, and large-scale library management.**

**What makes this different from other Spotify MCPs?**
- **Confidence scoring** - Batch searches return HIGH/MEDIUM/LOW confidence for each match
- **Human-in-the-loop** - Uncertain matches are exported for review, then re-imported
- **Bulk operations** - Handle 500+ songs efficiently with rate limiting built-in
- **Library exports** - Export your complete library data
- **Podcast playlist focused** - Built specifically for importing song lists from podcast show notes

---

## Support This Project

Made cause I can't not have headphones on, support my 80k+ pocast subscriptions. [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/kevinhg)

---

## Listed On

| Directory | Link |
|-----------|------|
| PyPI | [pypi.org/project/spotify-bulk-actions-mcp](https://pypi.org/project/spotify-bulk-actions-mcp/) |
| mcp.so | [mcp.so/server/spotify-bulk-actions-mcp](https://mcp.so/server/spotify-bulk-actions-mcp/khglynn) |
| awesome-mcp-servers | [PR #1541](https://github.com/punkpeye/awesome-mcp-servers/pull/1541) *(pending)* |

---

## Projects I've Built With This

| Project | Description | Links |
|---------|-------------|-------|
| **recordOS** | Which albums do you love most? A visual album collection app | [Live](https://record-os.khglynn.com) · [Repo](https://github.com/khglynn/recordOS) |
| **Festival Navigator** | Navigate multi-day festivals with friends | [Repo](https://github.com/khglynn/festival-navigator) |

### Playlists Maintained With This MCP
*Coming soon: Switched On Pop, This American Life, and more podcast playlists*

---

## What This Does

**Library Analysis:**
- Get all your followed artists
- Get all saved/liked songs (handles libraries up to 10k songs)
- Find unique artists from your library ranked by song count
- Find albums where you have 6+ saved songs (great for vinyl shopping!)
- Export your complete library summary

**Listening Insights:**
- Your top artists and tracks (short/medium/long term)
- Recently played history

**Bulk Playlist Creation:**
- Import song lists from CSV files (for podcast playlists, etc.)
- Batch search with confidence scoring (HIGH/MEDIUM/LOW)
- Automatic handling of uncertain matches for human review
- Create playlists from search results

**Playlist Maintenance:**
- Find and remove duplicate tracks
- Compare two playlists (shared vs unique tracks)
- Bulk remove and reorder tracks, update playlist details
- Export any playlist to CSV

**Bulk Library Actions:**
- Follow/unfollow artists in bulk
- Save/unsave tracks in bulk

## Quick Start

### 1. Prerequisites

- Python 3.10+
- A Spotify account
- Spotify Developer credentials ([get them here](https://developer.spotify.com/dashboard))

### 2. Clone & Setup

```bash
# Clone the repo
git clone https://github.com/khglynn/spotify-bulk-actions-mcp.git
cd spotify-bulk-actions-mcp

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Copy env example and add your credentials
cp .env.example .env
# Edit .env with your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
```

> **Also on PyPI:** `pip install spotify-bulk-actions-mcp` - but you'll still need local `.env` and auth setup.

### 3. Authenticate with Spotify (One-Time)

This opens a browser for you to log in:

```bash
python setup_auth.py
```

After login, your token is saved locally in `.spotify_cache/`.

### 4. Test It Works

```bash
source venv/bin/activate
python -c "from spotify_bulk_actions_mcp.utils.auth import is_authenticated; print('Auth OK!' if is_authenticated() else 'Not authenticated')"
```

### Option B: Hosted (claude.ai custom connector)

This server also runs as a remote MCP over streamable HTTP (`MCP_TRANSPORT=http`),
fronted by OAuth 2.1 (WorkOS AuthKit) with a fail-closed user allowlist. That's how
the author runs it: Cloud Run + Secret Manager for the Spotify refresh token, added
to claude.ai as a custom connector. Tools carry `readOnlyHint`/`destructiveHint`
annotations so clients can group read vs write actions. See `Dockerfile` and the
deploy notes in the parent collection repo.

### 5. Connect to Claude Code

Add this to your Claude Code settings (`~/.claude/settings.local.json`):

```json
{
  "mcpServers": {
    "spotify": {
      "command": "/path/to/spotify-bulk-actions-mcp/venv/bin/spotify-bulk-actions-mcp"
    }
  }
}
```

Restart Claude Code after adding this.

## Available Tools (33)

### Library Analysis
| Tool | Description |
|------|-------------|
| `check_auth_status` | Verify Spotify auth is working |
| `get_followed_artists` | Get all artists you follow |
| `get_saved_tracks` | Get all your liked songs |
| `get_library_artists` | Artists from saved songs, ranked by count |
| `get_albums_by_song_count` | Albums with N+ saved songs |
| `export_library_summary` | Complete library export |

### Listening Insights
| Tool | Description |
|------|-------------|
| `get_top_artists` | Your top artists (short/medium/long term) |
| `get_top_tracks` | Your top tracks (short/medium/long term) |
| `get_recently_played` | Recently played tracks |

### Bulk Library Actions
| Tool | Description |
|------|-------------|
| `follow_artists` | Follow artists in bulk |
| `unfollow_artists` | Unfollow artists in bulk |
| `save_tracks` | Like/save tracks in bulk |
| `unsave_tracks` | Un-like tracks in bulk |

### Search
| Tool | Description |
|------|-------------|
| `search_track` | Search for a single track |
| `search_track_fuzzy` | Broader search when exact fails |
| `batch_search_tracks` | Search many tracks with confidence scores |
| `get_track_preview_url` | Get 30-second preview URL |

### Playlist Creation
| Tool | Description |
|------|-------------|
| `create_playlist` | Create a new playlist |
| `add_tracks_to_playlist` | Add tracks to existing playlist |
| `import_and_create_playlist` | Full CSV → playlist workflow |
| `create_playlist_from_search_results` | Create from batch search |
| `add_reviewed_tracks` | Add reviewed/corrected tracks |

### Playlist Management
| Tool | Description |
|------|-------------|
| `get_playlist_info` | Get playlist details |
| `update_playlist` | Update name, description, public status |
| `get_playlist_tracks` | Get all tracks in a playlist |
| `export_playlist_to_csv` | Export a playlist to CSV |
| `compare_playlists` | Shared vs unique tracks between two playlists |
| `find_duplicate_tracks` | Find duplicates in a playlist |
| `remove_duplicate_tracks` | Remove duplicates, keeping first occurrence |
| `remove_tracks_from_playlist` | Bulk remove specific tracks |
| `reorder_playlist_tracks` | Move tracks within a playlist |

### Utilities
| Tool | Description |
|------|-------------|
| `parse_song_list_csv` | Validate a song CSV |
| `export_review_csv` | Export uncertain matches for review |

## How This Differs From the Official Spotify Connector

Claude has an official Spotify connector (built by Spotify, April 2026). It's excellent
at what it does — but its tool surface is small, and this MCP exists for everything it
doesn't cover. As of August 2026 the official connector exposes 8 tools: Search Spotify,
Create Playlist, Get Currently Playing, Add to Library, Remove from Library, Fetch
Playlist Tracks, and two auth utilities.

| Capability | Official connector | This MCP |
|---|---|---|
| Search, playback context, mood playlists | ✅ | Search only |
| Create a playlist | ✅ | ✅ (plus CSV import w/ confidence scoring) |
| Add/remove Liked Songs | ✅ (one at a time) | ✅ bulk |
| Read your full library (saved tracks, followed artists) | ❌ | ✅ |
| Listening insights (top artists/tracks, recently played) | ❌ | ✅ |
| Edit existing playlists (bulk remove, reorder, update details) | ❌ | ✅ |
| Dedupe / compare / export playlists to CSV | ❌ | ✅ |
| Bulk follow/unfollow artists | ❌ | ✅ |

One more difference: the official connector runs on Spotify's partner-gated MCP gateway
(no dynamic client registration; tokens from ordinary developer apps are rejected), so
it's only usable inside partnered AI surfaces. This MCP runs under your own Spotify
developer app — Development Mode limits apply (5 allowlisted users per Client ID as of
February 2026), but you control it end to end.

## Example Workflows

### Get Your Library Stats

Ask Claude:
> "What artists do I have the most saved songs from?"

Claude will use `get_library_artists` and show you.

### Find Albums for Vinyl

Ask Claude:
> "Find albums where I have 6 or more saved songs"

Claude will use `get_albums_by_song_count` with `min_songs=6`.

### Create Playlist from Song List

1. Create a CSV file:
```csv
title,artist
Bohemian Rhapsody,Queen
Hotel California,Eagles
Billie Jean,Michael Jackson
```

2. Ask Claude:
> "Create a playlist called 'My Mix' from this CSV: [paste CSV]"

Claude will:
1. Parse the CSV
2. Search each song with confidence scoring
3. Create the playlist with high-confidence matches
4. Show you uncertain matches to review

### Bulk Podcast Playlist

For large lists (500+ songs):
1. Ask Claude to use `batch_search_tracks` with your song list
2. Review the results (HIGH goes in automatically)
3. Use `export_review_csv` to get uncertain matches
4. Review/correct in a spreadsheet
5. Use `add_reviewed_tracks` to add your corrections

## Rate Limits

The server handles Spotify's rate limits automatically:
- Small delays between API calls
- Automatic retry on 429 errors
- Caching to reduce repeat calls

For 10k songs, expect the initial library fetch to take 2-3 minutes.

## Files & Data

| Location | Purpose |
|----------|---------|
| `.env` | Your Spotify credentials (gitignored) |
| `.spotify_cache/` | Auth tokens and cached data (gitignored) |
| `spotify_bulk_actions_mcp/server.py` | Main MCP server |
| `spotify_bulk_actions_mcp/tools/` | Tool implementations |

## Troubleshooting

**"Not authenticated" error:**
```bash
python setup_auth.py
```

**Rate limit errors:**
Wait a few minutes and try again. The server will auto-retry.

**Token expired:**
The server auto-refreshes tokens. If issues persist, re-run `setup_auth.py`.

## Security Notes

- Your credentials are in `.env` (gitignored, never committed)
- Auth tokens are stored locally in `.spotify_cache/`
- Never share your `.env` or token files
- If credentials are exposed, rotate them in Spotify Dashboard

## License

MIT

---

Made cause I can't not have headphones on. If this helps you, [buy me a coffee](https://buymeacoffee.com/kevinhg)!
