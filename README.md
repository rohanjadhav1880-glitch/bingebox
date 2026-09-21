# 🎬 BingeBox — Universal Standalone Media Player

![Version](https://img.shields.io/badge/version-1.1.0-violet.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011%20%7C%20Android%207.0%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Privacy](https://img.shields.io/badge/privacy-100%25%20Offline%20%26%20Private-black.svg)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-orange.svg)](https://buymeacoffee.com/nemo7299)

**BingeBox** is a high-performance, 100% standalone, 100% offline multi-platform media player available for **Windows** (Python/PySide6) and **Android** (Kotlin/Jetpack Compose), powered by **libmpv** and **FFmpeg**.

Designed from the ground up to require zero external dependencies (no VLC installation needed), BingeBox delivers hardware-accelerated GPU video playback with an ultra-sleek, modern Obsidian dark UI.

---

## ✨ Features

- **🚀 100% Standalone & Offline**: Ships with embedded `libmpv` and `FFmpeg` engines. No VLC or third-party codecs required. Zero telemetry, zero analytics tracking, and no background network calls (100% private).
- **🎞️ Universal Format Support**: Plays virtually every video container and audio codec (`.mp4`, `.mkv`, `.webm`, `.avi`, `.mov`, `.flv`, `.ts`, `.m2ts`, `.vob`, `.ogv`, `.3gp`, `.rmvb`, `.divx`, `.mp3`, `.flac`, `.wav`, etc.).
- **⚡ Hardware-Accelerated Decoding**: High-efficiency GPU decoding (`hwdec=auto-safe`, Direct3D 11 on Windows, MediaCodec on Android) powered by `libmpv`.
- **🎨 Obsidian Modern UI**: Custom glassmorphic dark interface with responsive controls, thumbnail previews, dynamic volume / seeking sliders, and auto-hiding controls.
- **🎛️ Audio Enhancer & Equalizer**: Multi-preset equalizer, volume booster, audio delay synchronization, dynamic volume normalizer, and Movie Night Mode (dialogue booster).
- **💬 Subtitle Engine**: Automatic embedded and external subtitle detection (`.srt`, `.ass`, `.vtt`) with hardware-accelerated text rendering via libass and real-time sync delay offsets.
- **🔁 A-B Looper & Playback Speed**: Precise native `libmpv` segment looping (`ab-loop-a` / `ab-loop-b`) and smooth playback speed scaling (`0.25x` to `4.0x`).
- **📱 Native Android Support**: Touch gestures (double-tap ±10s seek), Picture-in-Picture (PiP), screen orientation adaptivity, screen lock, and device video scanning via Android MediaStore.
- **📦 One-Click Windows Installer**: Built with Inno Setup for Start Menu, Desktop shortcuts, and right-click *"Play with BingeBox"* Windows Explorer integration.

---

## 💖 Support Development

If you love using BingeBox and want to support ongoing development, new feature additions, and updates, consider buying the developer a coffee:

☕ **[Buy Me a Coffee — nemo7299](https://buymeacoffee.com/nemo7299)**

---

## 📥 Downloads

Download the latest pre-compiled packages directly from our [GitHub Releases](https://github.com/rohanjadhav1880-glitch/bingebox/releases/tag/v1.1.0) page:

| Package | Platform | Format | Description |
| :--- | :--- | :--- | :--- |
| 📦 **[BingeBox_Setup.exe](https://github.com/rohanjadhav1880-glitch/bingebox/releases/download/v1.1.0/BingeBox_Setup.exe)** | Windows 10 / 11 | Single-file Installer | Installs desktop shortcuts & file associations |
| 🚀 **[BingeBox.exe](https://github.com/rohanjadhav1880-glitch/bingebox/releases/download/v1.1.0/BingeBox.exe)** | Windows 10 / 11 | Portable Executable | Standalone portable build (no install required) |
| 📱 **[BingeBox.apk](https://github.com/rohanjadhav1880-glitch/bingebox/releases/download/v1.1.0/BingeBox.apk)** | Android 7.0+ | APK Package (`arm64-v8a`) | Native Android mobile application |

---

## 📂 Repository Structure

- `main.py`: Core desktop player application (Python 3.10 & PySide6 / Qt6).
- `setup_engine.py`: Engine helper utility to check and guide `libmpv` & FFmpeg installation.
- `main.spec` & `setup_installer.iss`: PyInstaller executable spec and Inno Setup Windows installer script.
- `android/`: Native Android application (Kotlin, Jetpack Compose, Android NDK `libmpv`).
- `web/`: Web and Electron client (HTML5, Vite, Canvas dynamic lighting).

---

## 🛠️ Building from Source

### 💻 Windows Desktop (Python / PySide6)

#### Prerequisites
- Python 3.10+
- Windows 10 / 11 (64-bit)

#### 1. Clone the Repository
```bash
git clone https://github.com/rohanjadhav1880-glitch/bingebox.git
cd bingebox
```

#### 2. Install Python Dependencies
```bash
pip install PySide6 python-mpv
```

#### 3. Setup libmpv & Engine Binaries
`python-mpv` requires the 64-bit `libmpv` shared library on Windows:
1. Download 64-bit `libmpv` (`libmpv-2.dll` or `mpv-1.dll`) from [SourceForge mpv-player-windows](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/) or [shinchiro/mpv-winbuild-cmake Releases](https://github.com/shinchiro/mpv-winbuild-cmake/releases).
2. Extract `libmpv-2.dll` (or `mpv-1.dll`) into the `engine/` folder in the project root:
   ```text
   bingebox/
   ├── engine/
   │   ├── libmpv-2.dll
   │   ├── ffmpeg.exe (optional, for thumbnail extraction)
   │   └── ffprobe.exe (optional)
   ├── main.py
   ```
3. Run the engine verification script:
   ```bash
   python setup_engine.py
   ```

#### 4. Run Application
```bash
python main.py
```

#### 5. Build Standalone Executable & Installer
```bash
# Build portable standalone .exe
python -m PyInstaller main.spec --noconfirm

# Build Inno Setup single-file installer (requires Inno Setup 6)
iscc setup_installer.iss
```

---

### 📱 Android Application (Kotlin / Compose)

See the [Android Documentation](android/README_ANDROID.md) for full setup instructions.

```bash
cd android
./gradlew.bat assembleDebug
```
The output APK will be generated at `android/app/build/outputs/apk/debug/app-debug.apk`.

---

### 🌐 Web / Electron Client (Optional)

See the [Web Documentation](web/README.md) for setup and development:
```bash
cd web
npm install
npm run dev
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

Developed with ❤️ by **CAPTAIN NEMO**.
