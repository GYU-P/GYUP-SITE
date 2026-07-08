"""Regenerate playlist.json from the YouTube playlist via the official
YouTube Data API v3.

Requires the YOUTUBE_API_KEY environment variable, which is stored as a
GitHub Actions secret and never exposed to the browser. Run via the
scheduled GitHub Actions workflow (.github/workflows/update-playlist.yml)
to refresh playlist.json.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PLAYLIST_ID = "PL21xeg-oKROEWOp5GCET7228xD_6iEEQ0"
API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "playlist.json"


def fetch_page(api_key, page_token=None):
    params = {
        "part": "snippet",
        "maxResults": "50",
        "playlistId": PLAYLIST_ID,
        "key": api_key,
    }
    if page_token:
        params["pageToken"] = page_token
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    videos = []
    page_token = None
    while True:
        try:
            data = fetch_page(api_key, page_token)
        except urllib.error.HTTPError as e:
            body = json.loads(e.read().decode("utf-8"))
            message = body.get("error", {}).get("message", str(e))
            print(f"API error ({e.code}): {message}", file=sys.stderr)
            sys.exit(1)

        if "error" in data:
            print(f"API error: {data['error'].get('message')}", file=sys.stderr)
            sys.exit(1)

        for item in data.get("items", []):
            snippet = item["snippet"]
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = thumbnails.get("medium") or thumbnails.get("default")
            video_id = snippet.get("resourceId", {}).get("videoId")
            if not video_id or not thumbnail:
                continue
            videos.append({
                "videoId": video_id,
                "title": snippet.get("title", ""),
                "thumbnail": thumbnail["url"],
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    OUTPUT_PATH.write_text(
        json.dumps(videos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(videos)} videos to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
