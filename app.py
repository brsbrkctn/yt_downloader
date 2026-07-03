import os
import sys
import time
import json
import ctypes
import threading
import webview
from downloader import YTDownloaderEngine
from history_manager import HistoryManager

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(get_app_dir(), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_clipboard_text():
    try:
        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        opened = False
        for _ in range(10):
            if user32.OpenClipboard(None):
                opened = True
                break
            time.sleep(0.01)
            
        if not opened:
            return ""

        try:
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return ""
            pointer = kernel32.GlobalLock(handle)
            if not pointer:
                return ""
            text = ctypes.c_wchar_p(pointer).value
            kernel32.GlobalUnlock(handle)
            return text or ""
        finally:
            user32.CloseClipboard()
    except Exception:
        return ""

class YTDownloaderAPI:
    def __init__(self, window_holder):
        self.window_holder = window_holder
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = YTDownloaderEngine()
        return self._engine

    @property
    def window(self):
        return self.window_holder.get('window')

    def get_system_language(self):
        try:
            import locale
            lang_code = locale.getdefaultlocale()[0]
            if not lang_code:
                lang_code = locale.getlocale()[0]
            if lang_code and lang_code.lower().startswith("tr"):
                return "tr"
        except Exception:
            pass
        try:
            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            if (lang_id & 0xFF) == 0x1F:  # Primary language ID for Turkish is 0x1F
                return "tr"
        except Exception:
            pass
        return "en"

    def get_language(self):
        cfg = load_config()
        if "lang" in cfg and cfg["lang"] in ["tr", "en"]:
            return cfg["lang"]
        return self.get_system_language()

    def save_language(self, lang):
        if lang in ["tr", "en"]:
            cfg = load_config()
            cfg["lang"] = lang
            save_config(cfg)
            return True
        return False

    def fetch_info(self, url):
        try:
            info = self.engine.fetch_info(url)
            return {"success": True, "data": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_download(self, url, format_type, quality):
        def progress_callback(progress_data):
            if self.window:
                progress_json = json.dumps(progress_data)
                js_code = f"if (window.updateProgress) window.updateProgress({progress_json});"
                self.window.evaluate_js(js_code)

        def worker():
            try:
                result_item = self.engine.download(url, format_type, quality, progress_callback=progress_callback)
                if self.window:
                    js_code = f"if (window.onDownloadComplete) window.onDownloadComplete({json.dumps(result_item)});"
                    self.window.evaluate_js(js_code)
            except Exception as e:
                error_msg = str(e)
                if self.window:
                    err_payload = {"status": "error", "percent": 0, "text": f"Hata: {error_msg}"}
                    self.window.evaluate_js(f"if (window.updateProgress) window.updateProgress({json.dumps(err_payload)});" )

        threading.Thread(target=worker, daemon=True).start()
        return {"success": True}

    def get_history(self):
        return HistoryManager.load_history()

    def delete_history_item(self, item_id, delete_file=False):
        return HistoryManager.delete_item(item_id, delete_file)

    def open_file(self, path):
        return HistoryManager.open_file(path)

    def open_folder(self, path):
        return HistoryManager.open_folder(path)

    def read_clipboard(self):
        return get_clipboard_text()

def main():
    HistoryManager.load_history(force_refresh=True)
    
    html_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
    file_url = f"file:///{html_file.replace('\\', '/')}"
    
    window_holder = {}
    api = YTDownloaderAPI(window_holder)

    # Calculate centered position natively without using events.shown to avoid Win32 deadlock
    try:
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        win_w, win_h = 1040, 780
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
    except Exception:
        pos_x, pos_y = None, None

    create_args = {
        "title": "YT Downloader",
        "url": file_url,
        "js_api": api,
        "width": 1040,
        "height": 780,
        "min_size": (850, 650),
        "background_color": "#101622"
    }
    if pos_x is not None and pos_y is not None:
        create_args["x"] = pos_x
        create_args["y"] = pos_y

    window = webview.create_window(**create_args)
    window_holder['window'] = window

    webview.start(debug=False)

if __name__ == "__main__":
    main()
