import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { phoneFirstEntry } from './device'
import './styles.css'
import './innate.css'
import './demo-skin.css'

phoneFirstEntry()

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
