import os
import sys
import json
import subprocess
import threading
from datetime import datetime

def get_app_dir():
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(appdata, "YT_Downloader")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

HISTORY_FILE = os.path.join(get_app_dir(), "history.json")

def get_user_downloads_dir():
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

def sanitize_item(item):
    """
    Guarantees returning pure primitive Python types (str, bool)
    to prevent PyWebView CLR/SyncRoot serialization recursion.
    """
    path = str(item.get("path", ""))
    return {
        "id": str(item.get("id", "")),
        "title": str(item.get("title", "")),
        "url": str(item.get("url", "")),
        "format": str(item.get("format", "")),
        "quality": str(item.get("quality", "")),
        "date": str(item.get("date", "")),
        "thumbnail": str(item.get("thumbnail", "")),
        "path": path,
        "duration": str(item.get("duration", "")),
        "exists": bool(os.path.exists(path)) if path else False
    }

class HistoryManager:
    _cached_history = None
    _lock = threading.Lock()

    @staticmethod
    def load_history(force_refresh=False):
        with HistoryManager._lock:
            if HistoryManager._cached_history is not None and not force_refresh:
                return [dict(x) for x in HistoryManager._cached_history]

            if not os.path.exists(HISTORY_FILE):
                HistoryManager._cached_history = []
                return []

            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    raw_history = json.load(f)
                    
                if not raw_history:
                    HistoryManager._cached_history = []
                    return []

                dirty = False
                cleaned_list = []
                for idx, raw in enumerate(raw_history):
                    if "id" not in raw or not raw["id"]:
                        raw["id"] = f"legacy_{idx}_{int(datetime.now().timestamp())}"
                        dirty = True
                    cleaned_list.append(sanitize_item(raw))

                if dirty:
                    try:
                        with open(HISTORY_FILE, "w", encoding="utf-8") as wf:
                            json.dump(cleaned_list, wf, ensure_ascii=False, indent=4)
                    except Exception:
                        pass

                HistoryManager._cached_history = cleaned_list
                return [dict(x) for x in cleaned_list]
            except Exception as e:
                print(f"Error loading history: {e}")
                HistoryManager._cached_history = []
                return []

    @staticmethod
    def add_to_history(item):
        history = HistoryManager.load_history(force_refresh=True)
        
        # Deduplicate by URL & Format
        history = [h for h in history if not (h.get("url") == item.get("url") and h.get("format") == item.get("format"))]
        
        if "id" not in item:
            item["id"] = f"{int(datetime.now().timestamp()*1000)}"
            
        sanitized = sanitize_item(item)
        history.insert(0, sanitized)
        
        try:
            temp_file = HISTORY_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
            os.replace(temp_file, HISTORY_FILE)
        except Exception as e:
            print(f"Error saving history: {e}")

        with HistoryManager._lock:
            HistoryManager._cached_history = history
        return [dict(x) for x in history]

    @staticmethod
    def delete_item(item_id, delete_file=False):
        history = HistoryManager.load_history(force_refresh=True)
        target_item = None
        new_history = []
        
        for item in history:
            if str(item.get("id")) == str(item_id):
                target_item = item
            else:
                new_history.append(item)
                
        if target_item and delete_file:
            path = target_item.get("path")
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error deleting file {path}: {e}")
                    
        try:
            temp_file = HISTORY_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(new_history, f, ensure_ascii=False, indent=4)
            os.replace(temp_file, HISTORY_FILE)
        except Exception as e:
            print(f"Error updating history after deletion: {e}")

        with HistoryManager._lock:
            HistoryManager._cached_history = new_history
        return [dict(x) for x in new_history]

    @staticmethod
    def open_file(path):
        if path and os.path.exists(path):
            norm_path = os.path.normpath(path)
            threading.Thread(target=lambda: os.startfile(norm_path), daemon=True).start()
            return {"success": True}
        return {"success": False, "error": "Dosya bulunamadı."}

    @staticmethod
    def open_folder(path):
        if path:
            norm_path = os.path.normpath(path)
            if os.path.exists(norm_path):
                threading.Thread(target=lambda: subprocess.Popen(['explorer', '/select,', norm_path]), daemon=True).start()
                return {"success": True}
            else:
                downloads_dir = os.path.dirname(norm_path)
                if not os.path.exists(downloads_dir):
                    downloads_dir = get_user_downloads_dir()
                if os.path.exists(downloads_dir):
                    threading.Thread(target=lambda: os.startfile(downloads_dir), daemon=True).start()
                    return {"success": True}
        return {"success": False, "error": "Klasör bulunamadı."}
