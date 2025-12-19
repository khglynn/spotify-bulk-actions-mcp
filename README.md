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

**Bulk Playlist Creation:**
- Import song lists from CSV files (for podcast playlists, etc.)
- Batch search with confidence scoring (HIGH/MEDIUM/LOW)
- Automatic handling of uncertain matches for human review
- Create playlists from search results

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
python -c "from src.utils.auth import is_authenticated; print('Auth OK!' if is_authenticated() else 'Not authenticated')"
```

### 5. Connect to Claude Code

Add this to your Claude Code settings (`~/.claude/settings.local.json`):

```json
{
  "mcpServers": {
    "spotify": {
      "command": "/path/to/spotify-bulk-actions-mcp/venv/bin/python",
      "args": ["/path/to/spotify-bulk-actions-mcp/src/server.py"]
    }
  }
}
```

Restart Claude Code after adding this.

## Available Tools (18)

### Library Analysis
| Tool | Description |
|------|-------------|
| `check_auth_status` | Verify Spotify auth is working |
| `get_followed_artists` | Get all artists you follow |
| `get_saved_tracks` | Get all your liked songs |
| `get_library_artists` | Artists from saved songs, ranked by count |
| `get_albums_by_song_count` | Albums with N+ saved songs |
| `export_library_summary` | Complete library export |

### Search
| Tool | Description |
|------|-------------|
| `search_track` | Search for a single track |
| `search_track_fuzzy` | Broader search when exact fails |
| `batch_search_tracks` | Search many tracks with confidence scores |
| `get_track_preview_url` | Get 30-second preview URL |

### Playlists
| Tool | Description |
|------|-------------|
| `create_playlist` | Create a new playlist |
| `add_tracks_to_playlist` | Add tracks to existing playlist |
| `import_and_create_playlist` | Full CSV → playlist workflow |
| `create_playlist_from_search_results` | Create from batch search |
| `add_reviewed_tracks` | Add reviewed/corrected tracks |
| `get_playlist_info` | Get playlist details |

### Utilities
| Tool | Description |
|------|-------------|
| `parse_song_list_csv` | Validate a song CSV |
| `export_review_csv` | Export uncertain matches for review |

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
| `src/server.py` | Main MCP server |
| `src/tools/` | Tool implementations |

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
