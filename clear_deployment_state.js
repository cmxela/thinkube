// Clear deployment state from browser localStorage
console.log("Clearing deployment state...");
localStorage.removeItem('thinkube-deployment-state');
console.log("Deployment state cleared\!");
console.log("You can now restart the deployment process.");
EOF < /dev/null
