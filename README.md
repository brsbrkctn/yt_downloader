<div align="center">

  # 🎬 YT Downloader
  ### Yüksek Hızlı, Modern ve Kurulumsuz YouTube MP4 & MP3 Dönüştürücü

  [![Version](https://img.shields.io/badge/version-v2.0.1-blue.svg?style=for-the-badge)](https://github.com/brsbrkctn/yt_downloader)
  [![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.10+-yellow.svg?style=for-the-badge)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6.svg?style=for-the-badge)](https://microsoft.com/windows)

  *Python 3, PyWebView ve Tailwind CSS kullanılarak geliştirilmiş ultra hızlı masaüstü YouTube indiricisi.*

</div>

---

## ✨ Öne Çıkan Özellikler

- 🎥 **1080p Full HD Video İndirme**: YouTube video ve ses akışlarını FFmpeg ile kayıpsız 1080p, 720p, 480p formatlarında birleştirir.
- 🎵 **320 kbps Stüdyo Kalitesinde MP3**: Şarkı adı, sanatçı bilgisi ve orijinal albüm kapağını (JPEG) otomatik olarak MP3 ID3 etiketlerine gömer.
- 📂 **Akıllı Klasör Tespiti**: Windows Registry (`User Shell Folders`) entegrasyonu sayesinde kullanıcının özel İndirilenler konumunu (örn: `D:\Berke\İndirilenler`) otomatik tespit eder.
- ⚡ **Ultra Hızlı Önbellekli Geçmiş**: RAM içi önbellekleme mimarisi ile indirme geçmişi 4 mikrosaniyede (0.000004s) anında kilitlenmeden açılır.
- 📋 **Tek Tıkla Panodan Yapıştırma**: Yerel Windows C-API (`ctypes.windll.user32`) entegrasyonu ile kopyaladığınız linkleri tek tıkla yapıştırır.
- 🎨 **Modern Koyu Tema Arayüz**: PyWebView ve Tailwind CSS ile tasarlanmış, buzlu cam ve dinamik animasyonlu şık arayüz.
- 🗑️ **Esnek Silme Modalı**: İndirme geçmişinden öge silerken isteğe bağlı olarak bilgisayarınızdaki fiziksel dosyayı da silme seçeneği sunar.

---

## 🛠️ Kullanılan Teknolojiler & Kütüphaneler

| Bileşen | Teknoloji / Paket | Açıklama |
| :--- | :--- | :--- |
| **Arayüz (GUI)** | [PyWebView](https://pywebview.flowrl.com/) & [Tailwind CSS](https://tailwindcss.com/) | Modern Webview2 tabanlı masaüstü arayüzü |
| **İndirme Motoru** | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | En güncel ve hızlı YouTube indirme kütüphanesi |
| **Medya Dönüştürücü** | [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | Video ve ses акışlarını 1080p kayıpsız birleştirici |
| **Ses Etiketleyici** | [mutagen](https://mutagen.readthedocs.io/) & [Pillow](https://python-pillow.org/) | MP3 ID3 kapak resmi ve şarkı bilgisi gömücü |
| **Pano Bağlantısı** | Native Windows C-API (`ctypes`) | 0ms kilitlenmesiz yerel pano okuyucu |

---

## 🚀 Kurulum ve Çalıştırma

### Yöntem 1: Standart Exe (Kurulumsuz Portatif)
`Releases` bölümünden veya `dist/YT_Downloader.exe` dosyasını indirerek **hiçbir kurulum yapmadan** doğrudan çift tıklayıp çalıştırabilirsiniz.

### Yöntem 2: Kaynak Koddan Çalıştırma

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/brsbrkctn/yt_downloader.git
   cd yt_downloader
   ```

2. Sanal ortam (venv) oluşturun ve aktif edin:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

---

## 📦 Exe Olarak Paketleme (PyInstaller)

Uygulamayı tek bir taşınabilir `.exe` dosyası haline getirmek için:

```powershell
pyinstaller --noconfirm --onedir --windowed --name "YT_Downloader" --add-data "index.html;." --add-data "history.json;." app.py
```

---

## 👤 Geliştirici

- **Geliştirici:** Barış Berke Çetin
- **GitHub:** [@brsbrkctn](https://github.com/brsbrkctn)

---

## 📄 Lisans

Bu proje **[MIT Lisansı](LICENSE)** ile lisanslanmıştır. Dilediğiniz gibi kullanabilir, değiştirebilir ve dağıtabilirsiniz.
