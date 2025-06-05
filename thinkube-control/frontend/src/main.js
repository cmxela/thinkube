// src/main.js
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/styles.css';

// Create app
const app = createApp(App);

// Use plugins
app.use(createPinia());
app.use(router);

// Mount the app
app.mount('#app');