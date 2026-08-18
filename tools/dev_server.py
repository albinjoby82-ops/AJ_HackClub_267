#!/usr/bin/env python3
"""Serve the Build Hub and proxy YouTube searches without exposing the API key.

Set YOUTUBE_API_KEY in the environment, then run:

    python tools/dev_server.py --port 8000
"""

import argparse
import html
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
YOUTUBE_API = "https://www.googleapis.com/youtube/v3"
CACHE_TTL_SECONDS = 15 * 60
RATE_WINDOW_SECONDS = 60
RATE_LIMIT = 30

_cache = {}
_cache_lock = threading.Lock()
_requests_by_ip = defaultdict(deque)
_rate_lock = threading.Lock()


def youtube_get(path, params, api_key):
    query = dict(params)
    query["key"] = api_key
    url = f"{YOUTUBE_API}/{path}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Hack-Club-Build-Hub/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.load(response)


def iso_duration(value):
    """Convert the YouTube subset of ISO 8601 durations to H:MM:SS or M:SS."""
    value = value or ""
    if not value.startswith("PT"):
        return ""
    value = value[2:]
    number = ""
    hours = minutes = seconds = 0
    for char in value:
        if char.isdigit():
            number += char
            continue
        amount = int(number or 0)
        number = ""
        if char == "H":
            hours = amount
        elif char == "M":
            minutes = amount
        elif char == "S":
            seconds = amount
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def search_youtube(query, page_token, api_key):
    search_params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": 15,
        "safeSearch": "moderate",
        "relevanceLanguage": "en",
        "regionCode": "IE",
    }
    if page_token:
        search_params["pageToken"] = page_token

    search_data = youtube_get("search", search_params, api_key)
    search_items = search_data.get("items", [])
    video_ids = [
        item.get("id", {}).get("videoId")
        for item in search_items
        if item.get("id", {}).get("videoId")
    ]

    details_by_id = {}
    if video_ids:
        details_data = youtube_get(
            "videos",
            {
                "part": "contentDetails,statistics,status",
                "id": ",".join(video_ids),
            },
            api_key,
        )
        details_by_id = {
            item.get("id"): item for item in details_data.get("items", [])
        }

    results = []
    for item in search_items:
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        details = details_by_id.get(video_id, {})
        status = details.get("status", {})
        if status.get("embeddable") is False:
            continue
        snippet = item.get("snippet", {})
        thumbnails = snippet.get("thumbnails", {})
        thumbnail = (
            thumbnails.get("high")
            or thumbnails.get("medium")
            or thumbnails.get("default")
            or {}
        ).get("url", "")
        statistics = details.get("statistics", {})
        results.append(
            {
                "id": video_id,
                "title": html.unescape(snippet.get("title", video_id)),
                "description": html.unescape(snippet.get("description", "")),
                "channel": html.unescape(snippet.get("channelTitle", "")),
                "publishedAt": snippet.get("publishedAt", ""),
                "thumbnail": thumbnail,
                "duration": iso_duration(
                    details.get("contentDetails", {}).get("duration")
                ),
                "views": statistics.get("viewCount", ""),
            }
        )

    return {
        "items": results,
        "nextPageToken": search_data.get("nextPageToken", ""),
    }


class BuildHubHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/youtube-search":
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def rate_limited(self):
        now = time.monotonic()
        ip = self.client_address[0]
        with _rate_lock:
            events = _requests_by_ip[ip]
            while events and now - events[0] > RATE_WINDOW_SECONDS:
                events.popleft()
            if len(events) >= RATE_LIMIT:
                return True
            events.append(now)
        return False

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/youtube-search":
            return super().do_GET()

        if self.rate_limited():
            return self.send_json(
                429, {"error": "Too many searches. Please wait a minute and try again."}
            )

        api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
        if not api_key:
            return self.send_json(
                503,
                {
                    "error": (
                        "YouTube search is not configured on this server. "
                        "Set YOUTUBE_API_KEY before starting it."
                    )
                },
            )

        params = urllib.parse.parse_qs(parsed.query)
        query = (params.get("q") or [""])[0].strip()
        page_token = (params.get("pageToken") or [""])[0].strip()
        if len(query) < 2:
            return self.send_json(400, {"error": "Enter at least two characters."})
        if len(query) > 200 or len(page_token) > 300:
            return self.send_json(400, {"error": "Search request is too long."})

        cache_key = (query.casefold(), page_token)
        now = time.monotonic()
        with _cache_lock:
            cached = _cache.get(cache_key)
            if cached and now - cached[0] < CACHE_TTL_SECONDS:
                return self.send_json(200, cached[1])

        try:
            result = search_youtube(query, page_token, api_key)
        except urllib.error.HTTPError as error:
            message = "YouTube rejected the search request."
            try:
                detail = json.loads(error.read().decode("utf-8"))
                message = detail.get("error", {}).get("message") or message
            except (ValueError, UnicodeDecodeError):
                pass
            return self.send_json(error.code, {"error": message})
        except (urllib.error.URLError, TimeoutError):
            return self.send_json(
                502, {"error": "YouTube could not be reached. Please try again."}
            )

        with _cache_lock:
            _cache[cache_key] = (now, result)
            if len(_cache) > 250:
                oldest = min(_cache, key=lambda key: _cache[key][0])
                _cache.pop(oldest, None)
        return self.send_json(200, result)


def main():
    parser = argparse.ArgumentParser(description="Serve the Hack Club Build Hub.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--bind", default="127.0.0.1")
    args = parser.parse_args()

    handler = partial(BuildHubHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer((args.bind, args.port), handler)
    configured = "configured" if os.environ.get("YOUTUBE_API_KEY") else "not configured"
    print(
        f"Build Hub: http://{args.bind}:{args.port}/videos.html "
        f"(YouTube API {configured})"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
