# 🎵 Music Bank | YouTube Playlist Downloader

<div align="center">

![Music Bank Logo](assets/Music%20Bank.svg)

**A beautiful, liquid glass-themed Streamlit application for downloading YouTube playlists as MP3 or MP4 files**

[![Made with Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[🚀 **Live Demo**](https://musicbank.streamlit.app/) | [📖 Documentation](#-features) | [🤝 Contributing](CONTRIBUTING.md)

</div>

---

## ✨ Features

### 🎨 Modern UI Design
- **Liquid Glass Theme** - Stunning glassmorphic design with radial gradients and backdrop blur effects
- **Animated Preloader** - 10-second branded loading screen with pulse animations
- **Responsive Navigation** - Bootstrap-inspired menu with smooth hover effects
- **Real-time Progress** - Live download status and progress tracking

### 🚀 Powerful Functionality
- **Batch Downloads** - Download entire YouTube playlists with a single click
- **Dual Format Support** - Choose between MP3 (audio) or MP4 (video) formats
- **Individual Downloads** - Access each completed file instantly with download buttons
- **ZIP Archive** - Download all files in a single compressed archive
- **Background Processing** - Multi-threaded downloads that don't block the UI
- **Auto-branding** - All files automatically tagged with "| Music Bank " suffix
- **Comprehensive Logging** - Detailed progress updates and error tracking

### 🛠️ Technical Excellence
- Built with **Streamlit 1.51.0** for rapid web app development
- Powered by **yt-dlp** for reliable YouTube downloads
- **FFmpeg integration** for seamless audio/video processing
- Session state management for smooth user experience
- Thread-safe download queue with cancellation support

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or newer** installed
- **FFmpeg** - Either:
  - Install system-wide and add to `PATH` (recommended), or
  - Place binaries in `deps/ffmpeg/bin` folder (auto-detected)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Tharinda-Pamindu/youtube-playlist-downloader.git
cd youtube-playlist-downloader
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

**Activate the environment:**
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

### 5. Open in Browser
The app will automatically open at `http://localhost:8501`

---

## 📖 How to Use

1. **Launch the app** and wait for the Music Bank preloader (10 seconds)
2. **Paste a YouTube playlist URL** into the input field
3. **Select format:**
   - 🎵 **MP3** - Audio only (smaller file size)
   - 🎬 **MP4** - Video with audio (full quality)
4. *(Optional)* **Limit downloads** - Enter a number to download only the first N videos
5. **Click "Start Download"** and watch the progress
6. **Download files individually** as they complete, or wait for the ZIP archive

---

## 🎨 UI Features

### Navigation Menu
- **Logo** - Music Bank branding with animated hover effects
- **MP3 Tab** - Quick access to audio downloads
- **MP4 Tab** - Quick access to video downloads

### Liquid Glass Styling
- Radial gradient backgrounds with transparency layers
- Backdrop blur effects for depth
- Smooth hover animations with scale transforms
- Multi-layered box shadows for 3D effect

### Preloader
- Animated Music Bank logo with pulse effect
- Fade-in/out text animation
- Auto-dismisses after 10 seconds
- Shows only once per session

---

## 📁 Project Structure

```
youtube-playlist-downloader/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── assets/                     # Static assets
│   ├── Music Bank.svg         # Logo file
│   └── logo.png               # Alternative logo
├── deps/                      # Optional FFmpeg binaries
│   └── ffmpeg/
│       └── bin/
├── README.md                  # This file
├── CONTRIBUTING.md            # Contribution guidelines
└── LICENSE                    # MIT License
```

---

## 🔧 Configuration

### FFmpeg Setup

**Option 1: System Installation (Recommended)**
- Windows: Download from [ffmpeg.org](https://ffmpeg.org) and add to PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**Option 2: Local Installation**
- Create `deps/ffmpeg/bin/` directory
- Download FFmpeg binaries and place in this folder
- App will auto-detect and use local binaries

---

## 🎯 Features in Detail

### Download Management
- **Queue System** - Downloads process sequentially to avoid rate limits
- **Progress Tracking** - Real-time updates on current file and overall progress
- **Error Handling** - Failed downloads logged with detailed error messages
- **Cancellation** - Stop downloads anytime with the cancel button

### File Naming
All downloaded files are automatically branded:
- Original: `Song Title.mp3`
- Downloaded: `Song Title | Music Bank .mp3`

### Memory Management
- Files stored in memory during download for immediate access
- Temporary files cleaned up automatically
- ZIP archive generated on-demand from memory

---

## ⚠️ Important Notes

- **RAM Usage** - Large playlists require sufficient memory as files are held in RAM
- **Download Speed** - Depends on your internet connection and YouTube's servers
- **Geo-restrictions** - Region-locked videos cannot be downloaded
- **Private Content** - Authentication-required videos not currently supported
- **Fair Use** - Respect copyright laws and YouTube's Terms of Service

---

## 🐛 Troubleshooting

### FFmpeg Not Found
```
Error: FFmpeg not detected
Solution: Install FFmpeg or place binaries in deps/ffmpeg/bin/
```

### Download Failures
- Check internet connection
- Verify playlist URL is public
- Try limiting to first few videos to test

### Slow Performance
- Reduce concurrent downloads
- Clear browser cache
- Restart the application

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Tharinda Pamindu**
- GitHub: [@Tharinda-Pamindu](https://github.com/Tharinda-Pamindu)

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) - Web app framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download engine
- [FFmpeg](https://ffmpeg.org) - Media processing
- Music Bank logo designed with care

---

## ⭐ Show Your Support

If you found this project helpful, please consider giving it a ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ by Music Bank**

[Report Bug](https://github.com/Tharinda-Pamindu/youtube-playlist-downloader/issues) · [Request Feature](https://github.com/Tharinda-Pamindu/youtube-playlist-downloader/issues)

</div>
