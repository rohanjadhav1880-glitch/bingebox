const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),

  // Dialogs
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  selectDirectoryDialog: () => ipcRenderer.invoke('select-directory-dialog'),
  scanDirectoryPath: (dirPath) => ipcRenderer.invoke('scan-directory-path', dirPath),

  // Event listeners
  onGlobalPlayPause: (callback) => {
    const subscription = (_event, ...args) => callback(...args);
    ipcRenderer.on('global-play-pause', subscription);
    return () => ipcRenderer.removeListener('global-play-pause', subscription);
  },
  onGlobalNextTrack: (callback) => {
    const subscription = (_event, ...args) => callback(...args);
    ipcRenderer.on('global-next-track', subscription);
    return () => ipcRenderer.removeListener('global-next-track', subscription);
  },
  onGlobalPrevTrack: (callback) => {
    const subscription = (_event, ...args) => callback(...args);
    ipcRenderer.on('global-prev-track', subscription);
    return () => ipcRenderer.removeListener('global-prev-track', subscription);
  }
});
