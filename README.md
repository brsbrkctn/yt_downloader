<div align="center">

  # 🎬 YT Downloader
  ### High-Performance Standalone YouTube MP4 & MP3 Converter

  [![Version](https://img.shields.io/badge/version-v2.4.0-blue.svg?style=for-the-badge)](https://github.com/brsbrkctn/yt_downloader)
  [![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.10+-yellow.svg?style=for-the-badge)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6.svg?style=for-the-badge)](https://microsoft.com/windows)

  *Ultra-fast desktop YouTube downloader built with Python 3, PyWebView, and Tailwind CSS.*

</div>

---

## ✨ Features

- 🎥 **4K Ultra HD & 1080p Video Downloads**: Merges YouTube video and audio streams seamlessly using FFmpeg with extended quality detection up to 4K (2160p) and 2K (1440p).
- ⏹️ **In-Flight Download Cancellation**: Cancel long or accidental downloads at any moment with automatic cleanup of partial temporary files.
- 🚀 **Multi-Fragment DASH Acceleration**: 5 concurrent fragment downloads with resilient socket retries and adaptive timeouts.
- 🎵 **320 kbps Studio Quality Audio**: Embeds title, artist, and original high-res album cover art (JPEG) into MP3 ID3 metadata tags automatically.
- 📂 **Smart Downloads Directory**: Auto-detects custom Windows Downloads folder locations (e.g. `C:\Downloads`) via Windows Registry (`User Shell Folders`).
- ⚡ **Sub-Millisecond RAM Cache History**: In-memory caching architecture delivers 4-microsecond history list rendering with zero UI freezing.
- 📋 **One-Click Clipboard Paste**: Integrated native Windows C-API (`ctypes.windll.user32`) for instant, leak-proof URL pasting.
- 🎨 **Modern Dark UI & Tactile Micro-Interactions**: Apple HIG and Emil Kowalski inspired polish with tabular monospace digits, custom SVG selects, and fluid transitions.
- 🗑️ **Flexible File Deletion Modal**: Option to delete entries from history only or permanently delete files from disk.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **GUI Framework** | [PyWebView](https://pywebview.flowrl.com/) & [Tailwind CSS](https://tailwindcss.com/) | Modern Webview2-powered desktop interface |
| **Download Engine** | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Powerful, up-to-date YouTube downloader core |
| **Media Transcoder** | [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | High-speed video/audio stream merger |
| **Audio Tagger** | [mutagen](https://mutagen.readthedocs.io/) & [Pillow](https://python-pillow.org/) | MP3 ID3 album cover art & metadata tagger |
| **Clipboard Handler** | Native Windows C-API (`ctypes`) | Zero-latency native clipboard reader |

---

## 🚀 Getting Started

### Option 1: Standalone Portable Executable (No Setup Required)
Download `YT_Downloader.exe` from the `Releases` section or `dist/` directory and double-click to run **without any installation**.

### Option 2: Run from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/brsbrkctn/yt_downloader.git
   cd yt_downloader
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Launch the application:
   ```bash
   python app.py
   ```

---

## 📦 Packaging Standalone Executable (PyInstaller)

To build a single portable `.exe` file:

```powershell
pyinstaller --noconfirm --onedir --windowed --name "YT_Downloader" --add-data "index.html;." --add-data "history.json;." app.py
```

---

## 📄 License

This project is licensed under the **[MIT License](LICENSE)**. Feel free to modify and distribute.
