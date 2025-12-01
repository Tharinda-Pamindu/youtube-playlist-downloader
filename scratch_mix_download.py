import tempfile
from pathlib import Path

import yt_dlp

URL = "https://www.youtube.com/watch?v=BSwzZj7xvYE&list=RDBSwzZj7xvYE&start_radio=1"

with tempfile.TemporaryDirectory() as temp_dir:
    target = Path(temp_dir)
    opts = {
        "outtmpl": str(target / "%(title)s.%(ext)s"),
        "format": "bestaudio/best",
        "ignoreerrors": True,
        "quiet": False,
        "no_warnings": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "playlist_items": "1",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([URL])
    files = list(target.glob("*") )
    print("files", files)
