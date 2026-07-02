import os
import re
import time
import requests
import imageio_ffmpeg
import yt_dlp
from datetime import datetime
from PIL import Image
from io import BytesIO

from history_manager import HistoryManager

try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, error as ID3Error
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

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

def is_valid_youtube_url(url):
    if not url or not isinstance(url, str):
        return False
    url_lower = url.strip().lower()
    patterns = ["youtube.com/", "youtu.be/", "music.youtube.com/"]
    return any(p in url_lower for p in patterns)

def clean_ansi_codes(text):
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

class YTDownloaderEngine:
    def __init__(self, download_dir=None):
        if not download_dir:
            self.download_dir = get_user_downloads_dir()
        else:
            self.download_dir = download_dir
            
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
            
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    def clean_url(self, url):
        if not url:
            return ""
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return url

    def fetch_info(self, url):
        """
        Extracts video metadata without downloading.
        """
        clean_url_str = self.clean_url(url)
        
        if not is_valid_youtube_url(clean_url_str):
            raise Exception("Geçersiz YouTube bağlantısı! Lütfen 'https://www.youtube.com/...' formatında doğru bir link girin.")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'ffmpeg_location': self.ffmpeg_path,
            'nocheckcertificate': True,
            'noplaylist': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url_str, download=False)
        except Exception as e:
            raise Exception(clean_ansi_codes(str(e)))

        if not info:
            raise Exception("Video bilgileri alınamadı. Linki kontrol edin.")

        title = info.get('title', 'Bilinmeyen Başlık')
        thumbnail = info.get('thumbnail')
        duration = info.get('duration')
        duration_str = info.get('duration_string')
        if not duration_str and duration:
            m, s = divmod(int(duration), 60)
            h, m = divmod(m, 60)
            duration_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        channel = info.get('uploader') or info.get('channel') or 'YouTube'

        # Extract available heights/qualities
        qualities = []
        formats = info.get('formats', [])
        for f in formats:
            h = f.get('height')
            if h and f.get('vcodec') != 'none':
                q_str = f"{h}p"
                if q_str not in qualities and h in [1080, 720, 480, 360, 240, 144]:
                    qualities.append(q_str)
                    
        qualities.sort(key=lambda x: int(x.replace('p', '')), reverse=True)
        if not qualities:
            qualities = ["1080p", "720p", "480p", "360p"]

        return {
            "url": clean_url_str,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration_str or "??:??",
            "channel": channel,
            "qualities": qualities
        }

    def download(self, url, format_type="MP4", quality="720p", progress_callback=None):
        """
        Downloads video/audio with given format & quality.
        """
        clean_url_str = self.clean_url(url)
        
        if not is_valid_youtube_url(clean_url_str):
            raise Exception("Geçersiz YouTube bağlantısı! Lütfen doğru bir video adresi girin.")

        def hook(d):
            if not progress_callback:
                return
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0) or 0
                eta = d.get('eta', 0) or 0
                
                percent = (downloaded / total * 100) if total > 0 else 0
                
                if speed > 1024 * 1024:
                    speed_str = f"{speed / (1024 * 1024):.1f} MB/s"
                elif speed > 1024:
                    speed_str = f"{speed / 1024:.0f} KB/s"
                else:
                    speed_str = f"{speed:.0f} B/s"

                if eta:
                    eta_m, eta_s = divmod(int(eta), 60)
                    eta_str = f"{eta_m:02d}:{eta_s:02d}"
                else:
                    eta_str = "--:--"

                progress_callback({
                    "status": "downloading",
                    "percent": round(percent, 1),
                    "speed": speed_str,
                    "eta": eta_str,
                    "text": f"İndiriliyor... %{percent:.1f} ({speed_str} - Kalan: {eta_str})"
                })
            elif d['status'] == 'finished':
                progress_callback({
                    "status": "processing",
                    "percent": 99,
                    "speed": "",
                    "eta": "",
                    "text": "İşleniyor & Dönüştürülüyor..."
                })

        out_tmpl = os.path.join(self.download_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'outtmpl': out_tmpl,
            'progress_hooks': [hook],
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': self.ffmpeg_path,
            'nocheckcertificate': True,
            'noplaylist': True,
            'concurrent_fragment_downloads': 4,
        }

        bitrate = "192"
        if format_type == "MP3":
            if quality and quality.endswith("k"):
                bitrate = quality.replace("k", "")
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
            })
        elif format_type == "M4A":
            ydl_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
            })
        else: # MP4
            height_val = "720"
            if quality and 'p' in quality:
                height_val = quality.replace('p', '')
            ydl_opts.update({
                'format': f'bestvideo[height<={height_val}]+bestaudio/best[height<={height_val}]/best',
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url_str, download=True)
                
                filename = ydl.prepare_filename(info)
                
                if format_type == "MP3":
                    final_path = os.path.splitext(filename)[0] + ".mp3"
                elif format_type == "MP4":
                    final_path = os.path.splitext(filename)[0] + ".mp4"
                else:
                    final_path = filename

                if not os.path.exists(final_path):
                    base_name = os.path.splitext(os.path.basename(filename))[0]
                    expected_ext = ".mp3" if format_type == "MP3" else ".mp4"
                    alt_path = os.path.join(self.download_dir, base_name + expected_ext)
                    if os.path.exists(alt_path):
                        final_path = alt_path
        except Exception as e:
            clean_err = clean_ansi_codes(str(e))
            raise Exception(clean_err)

        # Embed metadata for MP3 if mutagen available
        if format_type == "MP3" and HAS_MUTAGEN and os.path.exists(final_path):
            try:
                self._embed_mp3_tags(final_path, info)
            except Exception as e:
                print(f"Metadata embedding error: {e}")

        if progress_callback:
            progress_callback({
                "status": "completed",
                "percent": 100,
                "speed": "",
                "eta": "",
                "text": "İndirme Tamamlandı!"
            })

        # Register to History
        history_item = {
            "id": f"{int(time.time()*1000)}",
            "title": info.get('title', 'Bilinmeyen Video'),
            "url": clean_url_str,
            "format": format_type,
            "quality": quality,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "thumbnail": info.get('thumbnail'),
            "path": final_path,
            "duration": info.get('duration_string') or "??"
        }
        HistoryManager.add_to_history(history_item)

        return history_item

    def _embed_mp3_tags(self, mp3_file, info):
        audio = MP3(mp3_file, ID3=ID3)
        try:
            audio.add_tags()
        except ID3Error:
            pass

        title = info.get('title', '')
        artist = info.get('uploader') or info.get('channel') or ''
        thumb_url = info.get('thumbnail')

        if title:
            audio.tags.add(TIT2(encoding=3, text=title))
        if artist:
            audio.tags.add(TPE1(encoding=3, text=artist))

        if thumb_url:
            try:
                resp = requests.get(thumb_url, timeout=5)
                if resp.status_code == 200:
                    img = Image.open(BytesIO(resp.content))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    buf = BytesIO()
                    img.save(buf, format='JPEG', quality=90)
                    jpeg_bytes = buf.getvalue()

                    audio.tags.add(APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3, # Front Cover
                        desc='Cover',
                        data=jpeg_bytes
                    ))
            except Exception as e:
                print(f"Failed to fetch thumbnail for audio tag: {e}")

        audio.save()
