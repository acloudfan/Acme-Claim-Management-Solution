/**
 * Application entry point
 * Loads configuration before rendering React app
 */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { loadConfig } from './api/config';

// Load configuration before rendering app
loadConfig()
  .then(() => {
    console.log('Configuration loaded, starting app...');
    createRoot(document.getElementById('root')).render(
      <StrictMode>
        <App />
      </StrictMode>
    );
  })
  .catch((error) => {
    console.error('Failed to load configuration:', error);
    // Render error message
    document.getElementById('root').innerHTML = `
      <div style="display: flex; align-items: center; justify-center; min-height: 100vh; background: #f3f4f6; font-family: system-ui;">
        <div style="text-align: center; padding: 2rem; background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); max-width: 500px;">
          <h1 style="color: #ef4444; margin-bottom: 1rem;">Configuration Error</h1>
          <p style="color: #6b7280; margin-bottom: 1rem;">Failed to load application configuration.</p>
          <p style="color: #9ca3af; font-size: 0.875rem;">${error.message}</p>
          <button
            onclick="window.location.reload()"
            style="margin-top: 1rem; padding: 0.75rem 1.5rem; background: #2563eb; color: white; border: none; border-radius: 0.5rem; cursor: pointer; font-weight: 600;"
          >
            Retry
          </button>
        </div>
      </div>
    `;
  });
