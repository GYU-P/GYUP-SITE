"""Regenerate playlist.json from the YouTube playlist using yt-dlp.

No YouTube API key is required: yt-dlp reads the public playlist page
directly. Run this locally or via the scheduled GitHub Actions workflow
(.github/workflows/update-playlist.yml) to refresh playlist.json.
"""
import json
import subprocess
from pathlib import Path

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL21xeg-oKROEWOp5GCET7228xD_6iEEQ0"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "playlist.json"


def main():
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "-J", PLAYLIST_URL],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)

    videos = []
    for entry in data.get("entries", []):
        video_id = entry.get("id")
        title = entry.get("title")
        if not video_id or not title:
            continue
        videos.append({
            "videoId": video_id,
            "title": title,
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
        })

    OUTPUT_PATH.write_text(
        json.dumps(videos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(videos)} videos to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
