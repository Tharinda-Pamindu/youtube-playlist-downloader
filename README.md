# YouTube Playlist Downloader (Streamlit)

This project provides a Streamlit web application that downloads every video in a YouTube playlist as either MP4 (video) or MP3 (audio-only), exposing each completed item for immediate download while still offering an optional ZIP bundle when the run finishes.

## Features

- Streamlit UI with playlist URL input and output format selection.
- Uses `yt-dlp` to download video or audio tracks reliably.
- Converts audio tracks to MP3 using FFmpeg.
- Surfaces each finished track/video instantly with individual download buttons—no need to wait for the entire playlist.
- Generates a compressed ZIP file containing all downloaded media for a single-click download once the playlist finishes.
- Background worker keeps processing the playlist even while you interact with downloads or dismiss browser prompts.
- Displays detailed progress, success counts, and per-item failures.

## Prerequisites

- Python 3.9 or newer.
- FFmpeg must be available. Either install it on the system `PATH` (recommended) or drop the binaries in `deps/ffmpeg/bin` and the app will load them automatically.

## Getting Started

1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
4. Open the provided local URL in a browser, supply a playlist URL, pick the desired output format, and click **Start Download**.

## Notes

- Large playlists can take considerable time and disk space. The app holds completed files in memory to enable immediate downloads and also streams the final ZIP from memory; ensure you have sufficient RAM for very large downloads.
- Items blocked in your region or requiring authentication cannot be downloaded without providing additional credentials; the current UI targets public playlists only.
