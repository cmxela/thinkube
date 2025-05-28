# Clear Deployment State

To clear the saved deployment state and start fresh:

## Option 1: In the Browser Console (Recommended)

1. Open the installer in your browser/Electron app
2. Open Developer Tools (F12 or Ctrl+Shift+I)
3. Go to the Console tab
4. Run this command:
   ```javascript
   localStorage.removeItem('thinkube-deployment-state');
   ```
5. Refresh the page

## Option 2: Clear All Browser Data

1. In the browser, clear all site data for localhost:5173
2. Or in Electron, you can quit the app completely and restart

## Option 3: Add a Clear State Button (Future Enhancement)

We should add a "Reset Deployment" button in the error state for easier recovery.

After clearing the state, the deployment will start from the beginning and run all playbooks in the correct order.