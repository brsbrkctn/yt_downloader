# 🚀 Changelog

All notable changes to this project are documented in this file following [Semantic Versioning (SemVer)](https://semver.org/).

---

### 📌 v2.0.1 - *2026-07-03*
- 🎯 **Auto-Center Window**: Window automatically centers on screen launch (`window.center()`).
- 📋 **Clipboard Paste Fix**: Added 10-retry loop Windows C-API clipboard reader with `navigator.clipboard` fallback.
- 🏷️ **SemVer Policy**: Standardized minor and patch version numbering.

---

### 📌 v2.0.0 - *2026-07-02*
- 🖥️ **PyWebView & Tailwind CSS**: Rewrote interface using PyWebView desktop window & Tailwind CSS dark theme.
- 🎥 **1080p Full HD & MP3 320kbps**: Added FFmpeg video/audio stream merger & Mutagen ID3 album artwork tagger.
- ⚡ **RAM Cache History**: Sub-millisecond history loading speed (4μs) with zero UI freezing.
- 📂 **Dynamic Downloads Folder**: Auto-detected user Downloads path via Windows Registry `User Shell Folders`.
