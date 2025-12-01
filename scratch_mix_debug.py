import yt_dlp

URL = "https://www.youtube.com/watch?v=BSwzZj7xvYE&list=RDBSwzZj7xvYE&start_radio=1"

with yt_dlp.YoutubeDL({
    "quiet": False,
    "skip_download": True,
    "extract_flat": "in_playlist",
}) as ydl:
    info = ydl.extract_info(URL, download=False)

entries = [entry for entry in (info.get("entries") or []) if entry]
print("Title:", info.get("title"))
print("Count:", len(entries))
print("First 5 titles:")
for entry in entries[:5]:
    print(" -", entry.get("title"))
