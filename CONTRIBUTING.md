# Contributing to Music Bank YouTube Playlist Downloader

First off, thank you for considering contributing to Music Bank! 🎉 Your help makes this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Issue Guidelines](#issue-guidelines)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our commitment to fostering an open and welcoming environment. We pledge to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🤝 How Can I Contribute?

### Reporting Bugs 🐛

Before creating a bug report, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title** - Brief description of the issue
- **Steps to reproduce** - Detailed steps to recreate the bug
- **Expected behavior** - What you expected to happen
- **Actual behavior** - What actually happened
- **Screenshots** - If applicable
- **Environment details:**
  - OS (Windows, macOS, Linux)
  - Python version
  - Streamlit version
  - FFmpeg version

**Example Bug Report:**
```markdown
## Bug: Downloads fail for private playlists

**Steps to Reproduce:**
1. Enter a private YouTube playlist URL
2. Click "Start Download"
3. Error appears in console

**Expected:** Clear error message about private playlist
**Actual:** Generic error with stack trace

**Environment:**
- OS: Windows 11
- Python: 3.11.5
- Streamlit: 1.51.0
```

### Suggesting Enhancements 💡

Enhancement suggestions are welcome! Please include:

- **Clear use case** - Why is this enhancement needed?
- **Detailed description** - What should it do?
- **Mockups/examples** - Visual aids if applicable
- **Alternative solutions** - Other approaches considered

**Example Enhancement Request:**
```markdown
## Enhancement: Add playlist reordering option

**Use Case:** Users want to download specific videos first

**Description:** Add option to reorder playlist before downloading

**Mockup:** [Drag-and-drop interface sketch]

**Alternatives:** Number-based priority system
```

### Code Contributions 💻

We love code contributions! Here are areas where you can help:

- **Bug fixes** - Resolve reported issues
- **New features** - Implement requested enhancements
- **UI improvements** - Enhance the liquid glass theme
- **Performance** - Optimize download speed or memory usage
- **Documentation** - Improve README, comments, or guides
- **Tests** - Add unit tests or integration tests

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.9 or newer
- Git
- FFmpeg (installed or in `deps/ffmpeg/bin`)

### Initial Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
```bash
git clone https://github.com/YOUR_USERNAME/youtube-playlist-downloader.git
cd youtube-playlist-downloader
```

3. **Add upstream remote:**
```bash
git remote add upstream https://github.com/Tharinda-Pamindu/youtube-playlist-downloader.git
```

4. **Create virtual environment:**
```bash
python -m venv .venv
```

5. **Activate environment:**
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

6. **Install dependencies:**
```bash
pip install -r requirements.txt
```

7. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

### Running the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Testing Your Changes

1. **Manual testing:**
   - Test with various playlist URLs
   - Try both MP3 and MP4 formats
   - Test error scenarios (invalid URLs, network issues)
   - Check UI responsiveness

2. **Code validation:**
```bash
# Check for syntax errors
python -m py_compile app.py

# Run any unit tests (if available)
# pytest tests/
```

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Comments added for complex logic
- [ ] Self-review completed
- [ ] Manual testing performed
- [ ] Documentation updated (if needed)
- [ ] No console errors or warnings

### Submitting the PR

1. **Update your fork:**
```bash
git fetch upstream
git rebase upstream/main
```

2. **Push your changes:**
```bash
git push origin feature/your-feature-name
```

3. **Create Pull Request** on GitHub with:
   - **Clear title** - Brief description of changes
   - **Description** - Detailed explanation of what and why
   - **Issue reference** - Link related issues (e.g., "Fixes #123")
   - **Screenshots** - Before/after images for UI changes
   - **Testing notes** - How you tested the changes

**Example PR Description:**
```markdown
## Add playlist thumbnail preview

Closes #45

### Changes
- Added thumbnail fetching from yt-dlp
- Displays playlist thumbnail in hero section
- Cached thumbnails to improve performance

### Screenshots
[Before] [After comparison images]

### Testing
- Tested with 10 different playlists
- Verified thumbnail caching works
- Checked memory usage remains acceptable
```

### Review Process

1. A maintainer will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. You'll be credited in the contributors list! 🎉

---

## 🎨 Style Guidelines

### Python Code Style

Follow PEP 8 with these specific guidelines:

**Formatting:**
- 4 spaces for indentation (no tabs)
- Max line length: 100 characters
- Use double quotes for strings
- Blank line between functions

**Naming Conventions:**
```python
# Functions and variables: snake_case
def download_playlist():
    video_url = "..."

# Classes: PascalCase
class PlaylistDownloader:
    pass

# Constants: UPPER_CASE
MAX_DOWNLOADS = 10
DEFAULT_FORMAT = "mp3"
```

**Import Order:**
```python
# 1. Standard library
import io
import os
from pathlib import Path

# 2. Third-party packages
import streamlit as st
import yt_dlp

# 3. Local modules
from utils import helper_function
```

**Comments:**
```python
# Good: Explains why, not what
# Cache results to avoid repeated API calls
cache = {}

# Bad: States the obvious
# Set x to 5
x = 5
```

### CSS/HTML Style

**CSS:**
- Use meaningful class names
- Keep selectors specific but not overly nested
- Comment complex animations

**HTML:**
- Proper indentation
- Close all tags
- Use semantic markup

### Streamlit Conventions

```python
# Use session state for persistence
if "downloads" not in st.session_state:
    st.session_state["downloads"] = []

# Use columns for layout
col1, col2 = st.columns(2)

# Use callbacks for button actions
st.button("Download", on_click=start_download)
```

---

## 📝 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(ui): add playlist thumbnail preview

Added thumbnail fetching from playlist metadata and display
in the hero section with liquid glass styling.

Closes #45

---

fix(download): handle network timeout errors

Added try-catch block around network requests with proper
error messages shown to users.

Fixes #67

---

docs(readme): update installation instructions

Clarified FFmpeg setup steps for Windows users.
```

### Commit Best Practices

- Write clear, descriptive commit messages
- Keep commits focused on single changes
- Commit working code (don't commit broken code)
- Reference issues when applicable

---

## 🐛 Issue Guidelines

### Creating Issues

**Use Templates:**
- Bug reports should include reproduction steps
- Feature requests should explain the use case
- Questions should provide context

**Good Issue Titles:**
- ✅ "Download fails for playlists with age-restricted videos"
- ✅ "Add support for playlist thumbnail display"
- ❌ "It doesn't work"
- ❌ "New feature"

**Label Usage:**
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

---

## 🧪 Testing Guidelines

### Manual Testing Checklist

- [ ] Fresh install in clean environment
- [ ] Test with various playlist sizes (small, medium, large)
- [ ] Test both MP3 and MP4 formats
- [ ] Verify UI responsiveness on different screen sizes
- [ ] Check error handling with invalid inputs
- [ ] Test cancellation functionality
- [ ] Verify ZIP download works correctly
- [ ] Check file naming with special characters

### Edge Cases to Consider

- Empty playlists
- Single-video playlists
- Very long video titles
- Special characters in titles
- Network interruptions
- Insufficient disk space
- Invalid FFmpeg installation

---

## 🏆 Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Thanked in commit messages and PR descriptions

---

## 💬 Questions?

- Open a GitHub issue with the `question` label
- Check existing issues and discussions
- Review the README for common solutions

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [Python PEP 8 Style Guide](https://pep8.org)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)

---

**Thank you for contributing to Music Bank! Your efforts help make this project better for everyone.** 🎵✨
