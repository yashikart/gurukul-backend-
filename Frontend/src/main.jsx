import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { initializeLanguageSupport } from './utils/languageSupport.js'
import { BUILD_VERSION } from './config.js'
import { initSignalCapture } from './utils/signals.js'
import { initStateEngine } from './utils/prana_state_engine.js'
import { initPacketBuilder } from './utils/prana_packet_builder.js'
import { initBucketBridge } from './utils/bucket_bridge.js'

// Initialize language support
initializeLanguageSupport();

// Initialize PRANA system components
try {
  const signalCapture = initSignalCapture();
  const stateEngine = initStateEngine(signalCapture);
  initPacketBuilder(signalCapture, stateEngine);
  initBucketBridge();
  
  console.log('[PRANA-G] System initialized successfully');
} catch (error) {
  console.error('[PRANA-G] Initialization error:', error);
}

// Log build version to prevent tree-shaking
console.log('Gurukul Build Version:', BUILD_VERSION);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
