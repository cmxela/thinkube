const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const log = require('electron-log');
const Store = require('electron-store');

// Handle sandbox issues on Linux
if (process.platform === 'linux') {
  console.log('Running on Linux, disabling sandbox...');
  app.commandLine.appendSwitch('no-sandbox');
  app.commandLine.appendSwitch('disable-setuid-sandbox');
}

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Store for saving configuration
const store = new Store();

let mainWindow;
let backendProcess;

// FastAPI backend configuration
const BACKEND_PORT = process.env.BACKEND_PORT || 8000;
const BACKEND_HOST = 'localhost';
const isDev = process.argv.includes('--dev');

// Start FastAPI backend
function startBackend() {
  // In dev mode, assume backend is already running
  if (isDev) {
    log.info('Dev mode: Using external backend on port', BACKEND_PORT);
    return;
  }

  const backendPath = path.join(process.resourcesPath, 'backend', 'main.py');

  log.info('Starting FastAPI backend...');
  
  backendProcess = spawn('python3', [backendPath], {
    env: { ...process.env, PORT: BACKEND_PORT }
  });

  backendProcess.stdout.on('data', (data) => {
    log.info(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    log.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    log.info(`Backend process exited with code ${code}`);
  });
}

// Create the browser window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, '..', 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#006680'
  });

  // Remove menu bar on Linux
  Menu.setApplicationMenu(null);

  // Load Vue frontend
  const frontendURL = isDev
    ? 'http://localhost:5173' // Vite dev server
    : `file://${path.join(__dirname, '..', 'frontend', 'dist', 'index.html')}`;

  // Add error handling for loading
  mainWindow.loadURL(frontendURL).catch(err => {
    log.error('Failed to load frontend:', err);
    // Show error in window
    mainWindow.loadURL(`data:text/html,
      <h1>Failed to load frontend</h1>
      <p>Make sure the frontend dev server is running on port 5173</p>
      <p>Error: ${err.message}</p>
    `);
  });

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  // Wait for the frontend to be ready
  mainWindow.webContents.on('did-finish-load', () => {
    log.info('Frontend loaded successfully');
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    log.error(`Frontend failed to load: ${errorCode} - ${errorDescription}`);
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// IPC Handlers
ipcMain.handle('get-backend-url', () => {
  return `http://${BACKEND_HOST}:${BACKEND_PORT}`;
});

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

ipcMain.handle('save-config', async (event, config) => {
  store.set('config', config);
  return true;
});

ipcMain.handle('load-config', async () => {
  return store.get('config', {});
});

// App event handlers
app.whenReady().then(() => {
  startBackend();
  
  // In dev mode, create window immediately
  if (isDev) {
    createWindow();
  } else {
    // Wait a bit for backend to start in production
    setTimeout(() => {
      createWindow();
    }, 2000);
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    log.info('Stopping backend process...');
    backendProcess.kill();
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  log.error('Uncaught Exception:', error);
  dialog.showErrorBox('Unexpected Error', error.message);
});

// 🤖 AI-generated