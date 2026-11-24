"""The album and playlist lookups (search_albums, get_album_tracks, find_playlists) against a stand-in Spotify client.

Run: uv run python -m unittest discover -s tests
"""

import unittest
from unittest import mock

from spotify_bulk_actions_mcp.tools import search


class FakeSpotipy:
    """Just enough of spotipy.Spotify for the lookups; records each search's limit."""

    def __init__(self, albums=(), own=(), found=(), tracks=()):
        self.albums, self.own, self.found, self.tracks = list(albums), list(own), list(found), list(tracks)
        self.search_limits = []

    def search(self, q, type, limit):
        if limit > search.SEARCH_MAX:
            raise AssertionError("Spotify refuses a search limit over 10")
        self.search_limits.append(limit)
        key = "albums" if type == "album" else "playlists"
        return {key: {"items": (self.albums if type == "album" else self.found)[:limit]}}

    def current_user_playlists(self, limit, offset):
        return {"items": self.own[offset:offset + limit], "total": len(self.own)}

    def album_tracks(self, album_id, limit, offset):
        return {"items": self.tracks[offset:offset + limit], "total": len(self.tracks)}


class FakeClient:
    def __init__(self, fake):
        self.client = fake

    def _handle_rate_limit(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def get_current_user(self):
        return {"id": "kevin"}


def playlist(pid, name, owner="kevin", summary_key="tracks", total=12):
    return {"id": pid, "name": name, "uri": "spotify:playlist:" + pid,
            "owner": {"id": owner, "display_name": owner}, summary_key: {"total": total}}


class Lookups(unittest.TestCase):
    def use(self, fake):
        patcher = mock.patch.object(search, "spotify_client", FakeClient(fake))
        patcher.start()
        self.addCleanup(patcher.stop)
        return fake

    def test_a_large_limit_never_reaches_spotify_search(self):
        fake = self.use(FakeSpotipy(albums=[{"id": "a", "name": "Rumours", "uri": "u", "artists": [{"name": "Fleetwood Mac"}]}]))
        out = search.search_albums("Rumours", "Fleetwood Mac", limit=20)
        self.assertEqual(out["best_match"]["id"], "a")
        search.find_playlists("Rumours", limit=15)
        self.assertEqual(fake.search_limits, [10, 10])

    def test_followed_playlists_are_in_the_library_but_not_yours(self):
        self.use(FakeSpotipy(own=[playlist("p1", "Kitchen", owner="kevin"), playlist("p2", "Kitchen Jazz", owner="spotify")]))
        out = search.find_playlists("Kitchen")
        by_id = {p["id"]: p for p in out["all_matches"]}
        self.assertEqual((by_id["p1"]["yours"], by_id["p1"]["in_library"]), (True, True))
        self.assertEqual((by_id["p2"]["yours"], by_id["p2"]["in_library"]), (False, True))

    def test_a_short_name_inside_the_asked_one_does_not_outrank_it(self):
        self.use(FakeSpotipy(own=[playlist("short", "Mix"), playlist("exact", "Morning Mix")]))
        out = search.find_playlists("Morning Mix")
        self.assertEqual(out["best_match"]["id"], "exact")
        self.assertNotIn("_tie", out["best_match"])

    def test_the_track_count_reads_the_2026_items_name_too(self):
        self.use(FakeSpotipy(own=[playlist("p", "Kitchen", summary_key="items", total=7)]))
        self.assertEqual(search.find_playlists("Kitchen")["best_match"]["tracks"], 7)

    def test_album_tracks_page_past_fifty_in_order(self):
        tracks = [{"name": "t%d" % i, "uri": "spotify:track:%d" % i, "track_number": i + 1, "artists": []} for i in range(120)]
        self.use(FakeSpotipy(tracks=tracks))
        with mock.patch.object(search.time, "sleep"):
            out = search.get_album_tracks("a")
        self.assertEqual(out["count"], 120)
        self.assertEqual(out["track_uris"][:2], ["spotify:track:0", "spotify:track:1"])


if __name__ == "__main__":
    unittest.main()
