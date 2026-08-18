import os
import sys
import json
import shutil
import subprocess
import threading
from datetime import datetime
from utils import get_app_data_dir, get_user_downloads_dir, open_path_or_url

HISTORY_FILE = os.path.join(get_app_data_dir(), "history.json")

def migrate_legacy_history():
    """
    Automatically migrates history.json from old executable/script paths
    to %APPDATA%/YT_Downloader/history.json so user history is never lost.
    """
    candidate_paths = []
    if getattr(sys, 'frozen', False):
        candidate_paths.append(os.path.join(os.path.dirname(sys.executable), "history.json"))
    candidate_paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json"))
    candidate_paths.append(os.path.join(os.getcwd(), "history.json"))

    current_data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                current_data = json.load(f)
                if not isinstance(current_data, list):
                    current_data = []
        except Exception:
            current_data = []

    if len(current_data) > 0:
        return  # APPDATA history already populated with items

    for old_path in candidate_paths:
        if os.path.exists(old_path) and old_path != HISTORY_FILE:
            try:
                with open(old_path, "r", encoding="utf-8") as of:
                    old_items = json.load(of)
                    if isinstance(old_items, list) and len(old_items) > 0:
                        with open(HISTORY_FILE, "w", encoding="utf-8") as wf:
                            json.dump(old_items, wf, ensure_ascii=False, indent=2)
                        break
            except Exception:
                pass

def sanitize_item(item):
    """
    Guarantees returning pure primitive Python types (str, bool)
    to prevent PyWebView CLR/SyncRoot serialization recursion.
    Fast path check without blocking network drives.
    """
    path = str(item.get("path", ""))
    # Fast non-blocking exists check:
    file_exists = bool(item.get("exists", True))
    if path:
        try:
            file_exists = os.path.isfile(path)
        except Exception:
            file_exists = False

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
        "exists": file_exists
    }

class HistoryManager:
    _cached_history = None
    _lock = threading.Lock()

    @staticmethod
    def load_history(force_refresh=False):
        with HistoryManager._lock:
            if HistoryManager._cached_history is not None and not force_refresh:
                return [dict(x) for x in HistoryManager._cached_history]

            # Attempt migration if needed
            migrate_legacy_history()

            if not os.path.exists(HISTORY_FILE):
                HistoryManager._cached_history = []
                return []

            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    raw_history = json.load(f)
                    
                if not raw_history or not isinstance(raw_history, list):
                    HistoryManager._cached_history = []
                    return []

                cleaned_list = []
                dirty = False
                for idx, raw in enumerate(raw_history):
                    if not isinstance(raw, dict):
                        continue
                    if "id" not in raw or not raw["id"]:
                        raw["id"] = f"item_{idx}_{int(datetime.now().timestamp())}"
                        dirty = True
                    cleaned_list.append(sanitize_item(raw))

                if dirty:
                    try:
                        with open(HISTORY_FILE, "w", encoding="utf-8") as wf:
                            json.dump(cleaned_list, wf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                HistoryManager._cached_history = cleaned_list
                return [dict(x) for x in cleaned_list]
            except Exception as e:
                HistoryManager._cached_history = []
                return []

    @staticmethod
    def get_history():
        """
        Ultra-fast non-blocking history accessor for PyWebView IPC.
        """
        with HistoryManager._lock:
            if HistoryManager._cached_history is None:
                return HistoryManager.load_history(force_refresh=True)
            return [dict(x) for x in HistoryManager._cached_history]

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
                json.dump(history, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, HISTORY_FILE)
        except Exception:
            pass

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
                except Exception:
                    pass
                    
        try:
            temp_file = HISTORY_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(new_history, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, HISTORY_FILE)
        except Exception:
            pass

        with HistoryManager._lock:
            HistoryManager._cached_history = new_history
        return [dict(x) for x in new_history]

    @staticmethod
    def open_file(path):
        return open_path_or_url(path)

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
