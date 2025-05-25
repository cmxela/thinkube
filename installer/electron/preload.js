const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getBackendURL: () => ipcRenderer.invoke('get-backend-url'),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  loadConfig: () => ipcRenderer.invoke('load-config'),
  
  // Platform information
  platform: process.platform,
  arch: process.arch,
  version: process.versions.electron
});