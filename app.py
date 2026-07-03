import os
import sys
import time
import json
import ctypes
import threading
import webview
from downloader import YTDownloaderEngine
from history_manager import HistoryManager

def get_app_data_dir():
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    target_dir = os.path.join(appdata, "YT_Downloader")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

CONFIG_FILE = os.path.join(get_app_data_dir(), "config.json")

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
        try:
            cfg = load_config()
            if "lang" in cfg and cfg["lang"] in ["tr", "en"]:
                return cfg["lang"]
        except Exception:
            pass
        return self.get_system_language()

    def save_language(self, lang):
        if lang in ["tr", "en"]:
            try:
                cfg = load_config()
                cfg["lang"] = lang
                save_config(cfg)
                return True
            except Exception:
                pass
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
                try:
                    progress_json = json.dumps(progress_data)
                    js_code = f"if (window.updateProgress) window.updateProgress({progress_json});"
                    self.window.evaluate_js(js_code)
                except Exception:
                    pass

        def worker():
            try:
                result_item = self.engine.download(url, format_type, quality, progress_callback=progress_callback)
                if self.window:
                    try:
                        js_code = f"if (window.onDownloadComplete) window.onDownloadComplete({json.dumps(result_item)});"
                        self.window.evaluate_js(js_code)
                    except Exception:
                        pass
            except Exception as e:
                error_msg = str(e)
                if self.window:
                    try:
                        err_payload = {"status": "error", "percent": 0, "text": f"Hata: {error_msg}"}
                        self.window.evaluate_js(f"if (window.updateProgress) window.updateProgress({json.dumps(err_payload)});" )
                    except Exception:
                        pass

        threading.Thread(target=worker, daemon=True).start()
        return {"success": True}

    def get_history(self):
        try:
            return HistoryManager.get_history()
        except Exception as e:
            print(f"API get_history error: {e}")
            return []

    def delete_history_item(self, item_id, delete_file=False):
        try:
            return HistoryManager.delete_item(item_id, delete_file)
        except Exception as e:
            print(f"API delete_history_item error: {e}")
            return []

    def open_file(self, path):
        try:
            return HistoryManager.open_file(path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_folder(self, path):
        try:
            return HistoryManager.open_folder(path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_clipboard(self):
        try:
            return get_clipboard_text()
        except Exception:
            return ""

def main():
    try:
        HistoryManager.load_history(force_refresh=True)
    except Exception as e:
        print(f"Startup history load error: {e}")
    
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
        "title": "YT Downloader v2.1.0",
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
