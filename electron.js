const { app, BrowserWindow, ipcMain, dialog, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: false, // Frameless design for a premium custom titlebar
    backgroundColor: '#060913',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, // Allows window.require('electron') in Vite
      webSecurity: false,      // Allows playing local video files via file:// scheme
    },
    title: 'BingeBox'
  });

  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // Open DevTools in development
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// OS Window control IPC handlers
ipcMain.on('window-minimize', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow) mainWindow.close();
});

// Native PC File picker handler
ipcMain.handle('open-file-dialog', async () => {
  if (!mainWindow) return [];
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Select Video File(s)',
    properties: ['openFile', 'multiSelections'],
    filters: [
      { 
        name: 'Video Files', 
        extensions: ['mp4', 'mkv', 'webm', 'ogg', 'avi', 'mov', 'flv'] 
      },
      {
        name: 'Audio Files',
        extensions: ['mp3', 'wav', 'ogg', 'aac', 'flac']
      },
      { 
        name: 'All Files', 
        extensions: ['*'] 
      }
    ]
  });
  return result.filePaths;
});

// Scan directory helper for media files
function scanDirectory(dirPath) {
  try {
    const files = fs.readdirSync(dirPath);
    const videoExtensions = ['.mp4', '.mkv', '.webm', '.ogg', '.avi', '.mov', '.flv', '.mp3', '.wav'];
    const results = [];
    
    files.forEach(file => {
      const fullPath = path.join(dirPath, file);
      try {
        const stats = fs.statSync(fullPath);
        if (stats.isFile()) {
          const ext = path.extname(file).toLowerCase();
          if (videoExtensions.includes(ext)) {
            results.push({
              name: file,
              path: fullPath,
              size: stats.size,
              modified: stats.mtime
            });
          }
        }
      } catch (e) {
        // Skip un-statable files
      }
    });
    
    return results.sort((a, b) => a.name.localeCompare(b.name));
  } catch (err) {
    console.error('Failed to read directory', err);
    return [];
  }
}

// Select Local Directory dialog IPC handler
ipcMain.handle('select-directory-dialog', async () => {
  if (!mainWindow) return null;
  const result = await dialog.showOpenDialog(mainWindow, {
    title: 'Select Media Folder to Scan',
    properties: ['openDirectory']
  });
  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  const dirPath = result.filePaths[0];
  const files = scanDirectory(dirPath);
  return { dirPath, files };
});

// Direct scan path IPC handler (on boot auto-reload)
ipcMain.handle('scan-directory-path', async (event, dirPath) => {
  if (!dirPath) return null;
  const files = scanDirectory(dirPath);
  return { dirPath, files };
});

// App lifecycle
app.whenReady().then(() => {
  createWindow();

  // Register global OS media hotkeys (work even when app is minimized)
  try {
    globalShortcut.register('MediaPlayPause', () => {
      if (mainWindow) mainWindow.webContents.send('global-play-pause');
    });
    globalShortcut.register('MediaNextTrack', () => {
      if (mainWindow) mainWindow.webContents.send('global-next-track');
    });
    globalShortcut.register('MediaPreviousTrack', () => {
      if (mainWindow) mainWindow.webContents.send('global-prev-track');
    });
  } catch (err) {
    console.error('Failed to register global OS shortcuts', err);
  }
});

app.on('will-quit', () => {
  // Clean up global key bindings on exit
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
