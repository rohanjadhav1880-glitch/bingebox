# 🎬 BingeBox — Universal Standalone Media Player

![Version](https://img.shields.io/badge/version-1.0.0-violet.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Privacy](https://img.shields.io/badge/privacy-100%25%20Offline%20%26%20Private-black.svg)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-orange.svg)](https://buymeacoffee.com/nemo7299)

**BingeBox** is a high-performance, 100% standalone, 100% offline desktop video player built with **Python 3.10**, **PySide6 (Qt6)**, **libmpv**, and **FFmpeg**.

Designed from the ground up to require zero external dependencies (no VLC installation needed), BingeBox delivers hardware-accelerated 4K/8K GPU video playback with an ultra-sleek, modern dark UI.

---

## ✨ Features

- **🚀 100% Standalone & Offline**: Ships with embedded `libmpv` and `FFmpeg` engine. No VLC or third-party software required. Zero telemetry, zero external network calls.
- **🎞️ Universal Format Support**: Plays virtually every video container and audio codec on Earth (`.mp4`, `.mkv`, `.webm`, `.avi`, `.mov`, `.flv`, `.ts`, `.m2ts`, `.vob`, `.ogv`, `.3gp`, `.rmvb`, `.divx`, `.mp3`, `.flac`, `.wav`, etc.).
- **⚡ Direct3D 11 GPU Acceleration**: High-efficiency hardware decoding (`hwdec=auto-safe`) powered by `libmpv`.
- **🎨 Obsidian Frameless UI**: Custom modern dark mode interface with responsive controls, thumbnail previews, and dynamic volume / seeking sliders.
- **🎛️ Audio Enhancer & Equalizer**: Native 5-band equalizer, volume booster (up to 150%), audio delay synchronization, volume normalizer, and night mode compression.
- **💬 Subtitle Engine**: Automatic embedded subtitle detection (`.srt`, `.ass`, `.vtt`) with custom delay adjustment offsets.
- **🔁 A-B Looper & Playback Speed**: Precise segment looping and smooth playback speed scaling (`0.25x` to `4.0x`).
- **📦 One-Click Windows Installer**: Built with Inno Setup for Start Menu, Desktop shortcuts, and right-click *"Play with BingeBox"* file Explorer integration.

---

## 💖 Support Development

If you love using BingeBox and want to support ongoing development, new feature additions, and updates, consider buying the developer a coffee:

☕ **[Buy Me a Coffee — nemo7299](https://buymeacoffee.com/nemo7299)**

---

## 📥 Download

Download the latest pre-compiled installer from our [GitHub Releases](https://github.com/rohanjadhav1880-glitch/bingebox/releases) page:

- 📦 **[BingeBox_Setup.exe](https://github.com/rohanjadhav1880-glitch/bingebox/releases)** (Single-file Windows Installer)

---

## 🛠️ Building from Source

### Prerequisites
- Python 3.10+
- Windows 10 / 11

### Installation & Build Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rohanjadhav1880-glitch/bingebox.git
   cd bingebox
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install PySide6 python-mpv
   ```

3. **Run Application**:
   ```bash
   python main.py
   ```

4. **Build Standalone Executable (`BingeBox.exe`)**:
   ```bash
   python -m PyInstaller main.spec --noconfirm
   ```

5. **Build Windows Installer (`BingeBox_Setup.exe`)**:
   *(Requires Inno Setup 6)*
   ```bash
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_installer.iss
   ```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

Developed with ❤️ by **CAPTAIN NEMO**.
