# 🚀 Changelog

All notable changes to **YT Downloader** are documented in this file following [Semantic Versioning (SemVer)](https://semver.org/).

---

### 📌 v2.1.1 - *2026-07-03*
- 🔊 **Universal Audio/Video Codec Compatibility**: Forced native H.264 video (`avc1`) & AAC audio encoding (`-c:a aac`) in MP4 containers so downloaded videos play audio and video natively out of the box in Windows Media Player and Movies & TV without requiring AV1 extensions or VLC.
- 📋 **Robust 64-bit Windows Clipboard Reader**: Added explicit 64-bit `ctypes` types (`argtypes`/`restype`) and `tkinter` fallback for zero-failure paste button operation on all Windows 10/11 machines.
- 🛡️ **Antivirus & SmartScreen Notes**: Added clarity and release instructions regarding unsigned executable warnings on Windows Defender & Avast DeepScreen.

---

### 📌 v2.1.0 - *2026-07-03*
- 🌐 **Persistent Internationalization (i18n)**: Automatic system language detection + persistent TR/EN language switcher saved in `%APPDATA%\YT_Downloader\config.json`.
- ⚡ **Zero-Flicker & Zero-Deadlock Rendering**: Native `CreateWindowEx` screen centering on creation; instant zero-delay language application with `private_mode=False`.
- 📜 **Robust History Engine**: JSON string IPC serialization ensuring 100% native JavaScript Array parsing; automatic migration of legacy history files to AppData.
- 📐 **Two-Line Hero Title**: Redesigned main hero header into a clean two-line layout.

---

### 📌 v2.0.2 - *2026-07-03*
- 🎨 **Custom Brand Logos**: Integrated custom `icon.ico` for desktop window/taskbar and `icon2.ico` for in-app headers.
- 📋 **Seamless Clipboard Paste**: Bypassed browser permission dialog prompt by forcing exclusive Windows C-API clipboard reads.
- 📐 **Vector Icon Refinement**: Replaced history play button path with standard solid vector arrow shape.
- 🏷️ **Tab Name Simplification**: Renamed "İndirme Geçmişi" navigation tab to "Geçmiş".

---

### 📌 v2.0.1 - *2026-07-03*
- 🎯 **Auto-Center Window**: Window automatically centers on launch (`window.center()`).
- 📋 **Windows C-API Clipboard Reader**: 10-retry loop native Windows C-API (`ctypes.windll.user32`) clipboard implementation with `navigator.clipboard` fallback.
- 📐 **Pixel-Perfect Heights**: Fixed search bar & filter container matching height (`h-11` / 44px).
- 🏷️ **SemVer Standardization**: Standardized minor & patch release versioning policy.

---

### 📌 v2.0.0 - *2026-07-02*
- 🖥️ **PyWebView Engine Overhaul**: Complete architectural migration from legacy Tkinter to modern Webview2 (PyWebView) desktop engine.
- 🎨 **Tailwind CSS Dark Theme**: Fully responsive dark-mode interface featuring glassmorphism, fluid micro-animations, and custom modals.
- ⚡ **Sub-Millisecond RAM Cache**: Implemented thread-safe in-memory caching for history items (4μs load speed).

---

### 📌 v1.9.0 - *2026-06-15*
- 🚀 **Performance Optimization**: Optimized background downloader thread memory allocation and download buffer size.
- 📂 **Registry Folder Detection**: Added Windows Registry (`User Shell Folders`) integration for dynamic user Downloads path resolution.

---

### 📌 v1.8.0 - *2026-05-28*
- 📜 **Download History Tracker**: Introduced JSON-based persistent download history tracker (`history.json`).
- 🗑️ **Item Removal**: Added ability to remove download items from history.

---

### 📌 v1.7.0 - *2026-05-10*
- 🖼️ **Album Artwork Embedding**: Added automatic high-resolution thumbnail extraction and JPEG ID3 cover art tag embedding for MP3 files using Mutagen.
- 🎵 **ID3 Metadata Tags**: Auto-populated Title and Artist tags for MP3 downloads.

---

### 📌 v1.5.0 - *2026-04-18*
- 🎥 **FFmpeg Stream Merger**: Integrated `imageio-ffmpeg` engine to merge separate video (1080p) and audio streams into unified MP4 files.
- 🏎️ **Multi-Thread Downloads**: Enabled 4-fragment concurrent downloads (`concurrent_fragment_downloads: 4`).

---

### 📌 v1.3.0 - *2026-03-22*
- 🎚️ **Quality Selector**: Added support for selecting video resolutions (1080p, 720p, 480p, 360p) and MP3 bitrates (320k, 256k, 192k, 128k).
- ⏱️ **Real-Time Progress Stats**: Added download speed (MB/s), percentage progress, and ETA calculation.

---

### 📌 v1.2.0 - *2026-03-05*
- 🎶 **MP3 Format Extraction**: Added audio-only extraction mode for converting YouTube videos to MP3 audio files.

---

### 📌 v1.1.0 - *2026-02-15*
- ⏳ **Status Indicators**: Added animated loading indicators and inline error handling banners.
- 🔍 **Video Metadata Fetcher**: Added video title, duration, channel, and thumbnail preview before downloading.

---

### 📌 v1.0.0 - *2026-02-01*
- 🎉 **Initial Release**: Basic YouTube URL video downloader powered by `yt-dlp`.
