import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { loadConfig } from './api/config'

// Load configuration before rendering app
loadConfig()
  .then(() => {
    createRoot(document.getElementById('root')).render(
      <StrictMode>
        <App />
      </StrictMode>,
    )
  })
  .catch((error) => {
    console.error('Failed to initialize app:', error)
    document.getElementById('root').innerHTML = `
      <div style="padding: 20px; text-align: center;">
        <h1>Configuration Error</h1>
        <p>Failed to load configuration. Please check the console for details.</p>
      </div>
    `
  })
