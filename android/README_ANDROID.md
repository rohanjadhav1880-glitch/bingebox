# 📱 BingeBox for Android (Native Port)

BingeBox Android is built with **Kotlin**, **Jetpack Compose**, and native **libmpv (`libmpv.so`)** via Android NDK for high-performance hardware-accelerated video playback.

---

## 🛠️ Project Structure
* `android/app/src/main/java/com/bingebox/mediaplayer/`
  * `MainActivity.kt`: App lifecycle, SAF file picker, Picture-in-Picture (PiP) mode.
  * `mpv/MPVLib.kt`: JNI native interface bindings to `libmpv.so`.
  * `mpv/MPVView.kt`: Android `SurfaceView` wrapper for libmpv video rendering.
  * `ui/components/`:
    * `PlayerControls.kt`: Glassmorphic auto-hiding controls (Play/Pause, Seekbar, A-B loop, PiP).
    * `GestureOverlay.kt`: Touch gesture engine (Double-tap 10s seek, brightness & volume drag).
    * `EqualizerSheet.kt`: Audio Equalizer presets, dialogue booster, pre-amp boost, audio sync.
    * `MediaLibraryScreen.kt`: Local file scanner and storage access.
  * `ui/theme/Theme.kt`: Jetpack Compose color themes (Midnight Obsidian, Cyberpunk Neon, Frost).

---

## 🚀 How to Build & Run

### 1. Requirements
* **Android Studio**: Jellyfish / Koala or newer (AGP 8.3+, Gradle 8.4+).
* **JDK**: Version 17.
* **Android NDK**: Version 26.x or newer.
* **Target Android SDK**: API 34 (Android 14).
* **Minimum Android SDK**: API 24 (Android 7.0).

### 2. Download Pre-built `libmpv.so` Binaries
Place pre-built Android `libmpv.so` binaries in `app/src/main/jniLibs/`:
```text
app/src/main/jniLibs/
├── arm64-v8a/
│   ├── libmpv.so
│   └── libplayer.so
├── armeabi-v7a/
│   ├── libmpv.so
│   └── libplayer.so
└── x86_64/
    ├── libmpv.so
    └── libplayer.so
```
*(Pre-compiled `libmpv.so` binaries can be downloaded from the official `mpv-android` releases repository).*

### 3. Build APK via Command Line
Open a terminal in the `android/` directory and run:
```bash
# Debug APK
./gradlew assembleDebug

# Release APK
./gradlew assembleRelease
```
The generated APK will be available in:
`android/app/build/outputs/apk/debug/app-debug.apk`

---

## 📱 Features Included
- ⚡ **Hardware Acceleration** (`hwdec="auto-safe"`, `vo="gpu"`, 150MB Demuxer Cache)
- 🔁 **A-B Repeat Looping**
- 🎛️ **Audio Equalizer & Dialogue Booster (Night Mode)**
- 📺 **Picture-in-Picture (PiP) Mode**
- 👆 **Double-tap Seek (±10s) & Touch Gestures**
- 📁 **Storage Access Framework (SAF) File Picker**
