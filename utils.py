import os
import re
import sys
import webbrowser
import threading
import subprocess
from urllib.parse import urlparse

def get_app_data_dir() -> str:
    """Returns the persistent application data directory (%APPDATA%/YT_Downloader)."""
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(appdata, "YT_Downloader")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def get_user_downloads_dir() -> str:
    """Detects Windows User Downloads directory via Registry or fallback."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        val, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
        winreg.CloseKey(key)
        expanded = os.path.expandvars(val)
        if os.path.exists(expanded):
            return expanded
    except Exception:
        pass

    default_dl = os.path.join(os.path.expanduser("~"), "Downloads")
    if os.path.exists(default_dl):
        return default_dl

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

# Comprehensive YouTube URL validation regex
YOUTUBE_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be"
}

def is_valid_youtube_url(url: str) -> bool:
    """Validates if the provided string is a legitimate YouTube video/music URL."""
    if not url or not isinstance(url, str):
        return False
    url_str = url.strip()
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        url_str = "https://" + url_str

    try:
        parsed = urlparse(url_str)
        domain = (parsed.netloc or "").lower()
        # Remove standard port if present (e.g. youtube.com:443)
        if ":" in domain:
            domain = domain.split(":")[0]

        if domain not in YOUTUBE_DOMAINS:
            return False

        path = parsed.path
        if domain == "youtu.be":
            return len(path.strip("/ ")) > 0
        
        # Check standard YouTube path patterns: /watch, /shorts/, /embed/, /v/, /playlist, /live/
        if path.startswith(("/watch", "/shorts/", "/embed/", "/v/", "/playlist", "/live/")) or "v=" in parsed.query:
            return True
        return len(path.strip("/ ")) > 0
    except Exception:
        return False

def clean_ansi_codes(text: str) -> str:
    """Cleans terminal ANSI escape sequences and formats user-friendly error messages."""
    if not text:
        return "Geçersiz veya ulaşılamayan bağlantı."
    s = str(text)
    
    if "Failed to resolve" in s or "getaddrinfo failed" in s or "Name or service not known" in s:
        return "Geçersiz web adresi veya internet bağlantısı kurulamadı."
    if "Video unavailable" in s:
        return "Bu YouTube videosu bulunamadı, gizli veya kaldırılmış."
    if "Private video" in s:
        return "Bu video gizli veya özel olarak ayarlanmış."
    if "is not a valid URL" in s or "Unsupported URL" in s:
        return "Lütfen geçerli bir YouTube video adresi girin."

    cleaned = re.sub(r'\x1b\[[0-9;]*m', '', s)
    cleaned = re.sub(r'^ERROR:\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(caused by.*\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    if len(cleaned) > 120:
        cleaned = cleaned[:120] + "..."
    return cleaned or "Geçersiz YouTube bağlantısı."

def open_path_or_url(target: str) -> dict:
    """Opens a file, directory, or web URL safely in the appropriate Windows application or default browser."""
    if not target:
        return {"success": False, "error": "Geçersiz hedef."}

    target_str = str(target).strip()

    # Web URL
    if target_str.startswith("http://") or target_str.startswith("https://"):
        try:
            threading.Thread(target=lambda: webbrowser.open(target_str), daemon=True).start()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Tarayıcı açılamadı: {e}"}

    # Local File or Directory
    norm_path = os.path.normpath(target_str)
    if os.path.exists(norm_path):
        try:
            threading.Thread(target=lambda: os.startfile(norm_path), daemon=True).start()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Dosya açılamadı: {e}"}

    return {"success": False, "error": "Dosya veya bağlantı bulunamadı."}
