# Bundled FFmpeg

Place FFmpeg binaries in this folder if you want the application to run without a system-wide FFmpeg installation.

Expected layout:

```
deps/
  ffmpeg/
    bin/
      ffmpeg.exe      # Windows
      ffprobe.exe
      ffplay.exe      # optional
```

For Linux/macOS use the appropriate executable names (without the `.exe` suffix). During startup the app prepends `deps/ffmpeg/bin` to `PATH`, so yt-dlp can invoke the bundled FFmpeg automatically. Update the files whenever you upgrade FFmpeg.
