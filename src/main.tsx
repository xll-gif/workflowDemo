import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

// 仅在开发环境启用 Mock
if (import.meta.env.DEV) {
  const { setupWorker } = await import('msw/browser')
  const { handlers } = await import('./mockHandlers')
  const worker = setupWorker(...handlers)
  await worker.start({
    onUnhandledRequest: 'bypass'
  })
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
