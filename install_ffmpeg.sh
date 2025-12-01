#!/bin/bash

# Install FFmpeg 8+ on Streamlit Cloud
# This script downloads and installs a newer version of FFmpeg

set -e

echo "Installing FFmpeg 8+ from johnvansickle.com static builds..."

# Create temp directory
mkdir -p /tmp/ffmpeg-install
cd /tmp/ffmpeg-install

# Download FFmpeg 8.x static build (Linux 64-bit)
wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Extract
tar -xf ffmpeg-release-amd64-static.tar.xz

# Find the extracted directory
FFMPEG_DIR=$(find . -maxdepth 1 -type d -name "ffmpeg-*-static" | head -n 1)

# Copy binaries to user local bin
mkdir -p ~/.local/bin
cp "$FFMPEG_DIR/ffmpeg" ~/.local/bin/
cp "$FFMPEG_DIR/ffprobe" ~/.local/bin/
chmod +x ~/.local/bin/ffmpeg
chmod +x ~/.local/bin/ffprobe

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
ffmpeg -version

echo "FFmpeg 8+ installed successfully!"
