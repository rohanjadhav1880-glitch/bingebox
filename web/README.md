# 🌐 BingeBox Web / Electron Client

This directory contains the **Web & Electron** client for BingeBox featuring HTML5 video playback, dynamic canvas ambient backlighting, multi-band equalizer, playlist manager, and subtitle synchronization.

---

## 🚀 Running the Web/Electron Client

### Prerequisites
- Node.js 18+
- npm

### Development Setup
1. Navigate to the `web/` directory:
   ```bash
   cd web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start Web Dev Server (Vite):
   ```bash
   npm run dev
   ```

4. Launch Electron Desktop Window:
   ```bash
   npm run electron:dev
   ```

### Production Build
```bash
npm run build
```
The compiled static assets will be output to `web/dist/`.
