import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { useState, useEffect, useCallback } from 'react'
import BeneficiaryDiscovery from './pages/BeneficiaryDiscovery'
import GrievancePortal from './pages/GrievancePortal'
import OperatorAssistant from './pages/OperatorAssistant'
import Dashboard from './pages/Dashboard'
import { LanguageProvider, useLanguage } from './contexts/LanguageContext'
import './App.css'

// ── Cache Manifest Types ──────────────────────────────────
interface CacheManifest {
  model_version: string
  checksum: string
  last_sync_timestamp: string
  is_stale: boolean
  connectivity_mode: 'Online' | 'Lite_Mode' | 'Offline'
}

// ── Connectivity Status Bar ───────────────────────────────
function ConnectivityStatusBar() {
  const [manifest, setManifest] = useState<CacheManifest | null>(null)
  const [syncing, setSyncing] = useState(false)
  const [bannerDismissed, setBannerDismissed] = useState(false)

  const fetchManifest = useCallback(async () => {
    try {
      const res = await fetch('/api/cache/manifest')
      if (res.ok) {
        const data: CacheManifest = await res.json()
        setManifest(data)
      }
    } catch {
      // Network error — keep last known state
    }
  }, [])

  useEffect(() => {
    fetchManifest()
    const interval = setInterval(fetchManifest, 60_000)
    return () => clearInterval(interval)
  }, [fetchManifest])

  const handleSyncNow = async () => {
    setSyncing(true)
    try {
      await fetch('/api/cache/sync', { method: 'POST' })
      await fetchManifest()
    } catch {
      // ignore
    } finally {
      setSyncing(false)
    }
  }

  const formatLastSync = (iso: string) => {
    const date = new Date(iso)
    const diffMs = Date.now() - date.getTime()
    const diffMins = Math.floor(diffMs / 60_000)
    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHrs = Math.floor(diffMins / 60)
    if (diffHrs < 24) return `${diffHrs}h ago`
    return date.toLocaleDateString()
  }

  const mode = manifest?.connectivity_mode ?? 'Online'
  const isLimitedMode = mode === 'Lite_Mode' || mode === 'Offline'
  const showBanner = isLimitedMode && !bannerDismissed

  const dotColor = mode === 'Online' ? '#10b981' : mode === 'Lite_Mode' ? '#f59e0b' : '#ef4444'
  const modeLabel = mode === 'Lite_Mode' ? 'Lite Mode' : mode

  return (
    <>
      <div className="connectivity-bar" role="status" aria-live="polite">
        <div className="connectivity-bar-inner">
          <div className="connectivity-left">
            <span className="connectivity-dot" style={{ backgroundColor: dotColor }} aria-hidden="true" />
            <span className="connectivity-mode">{modeLabel}</span>
            {manifest && (
              <span className="connectivity-sync">
                Last sync: {formatLastSync(manifest.last_sync_timestamp)}
              </span>
            )}
            {manifest?.is_stale && (
              <span className="connectivity-stale">
                ⚠ Cache stale — confidence values reduced by 10%
              </span>
            )}
          </div>
          <button
            className="connectivity-sync-btn"
            onClick={handleSyncNow}
            disabled={syncing}
            aria-label="Sync now"
          >
            {syncing ? '↻ Syncing…' : '↻ Sync Now'}
          </button>
        </div>
      </div>

      {showBanner && (
        <div className="lite-mode-banner" role="alert">
          <span>
            {mode === 'Offline'
              ? '⚠ You are offline. Some features are unavailable. Data shown may be outdated.'
              : '⚠ Lite Mode active — real-time charts and analytics are disabled. Showing cached data.'}
          </span>
          <button
            className="lite-mode-banner-dismiss"
            onClick={() => setBannerDismissed(true)}
            aria-label="Dismiss banner"
          >
            ✕
          </button>
        </div>
      )}
    </>
  )
}

function NagarikLogo() {
  return (
    <svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      {/* Dome / pillars */}
      <rect x="6" y="28" width="32" height="4" rx="1" fill="rgba(255,255,255,0.9)" />
      <rect x="8" y="18" width="4" height="10" rx="1" fill="rgba(255,255,255,0.85)" />
      <rect x="16" y="18" width="4" height="10" rx="1" fill="rgba(255,255,255,0.85)" />
      <rect x="24" y="18" width="4" height="10" rx="1" fill="rgba(255,255,255,0.85)" />
      <rect x="32" y="18" width="4" height="10" rx="1" fill="rgba(255,255,255,0.85)" />
      {/* Dome arc */}
      <path d="M6 18 Q22 4 38 18" stroke="rgba(255,255,255,0.95)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      {/* Flag / star at top */}
      <circle cx="22" cy="8" r="2.5" fill="rgba(255,255,255,1)" />
      {/* Base */}
      <rect x="4" y="32" width="36" height="3" rx="1.5" fill="rgba(255,255,255,0.7)" />
    </svg>
  )
}

function AppContent() {
  const { language, setLanguage, t } = useLanguage()

  return (
    <Router>
      <div className="app">
        <header className="header">
          <div className="header-content">
            <div className="header-brand">
              <div className="header-logo">
                <NagarikLogo />
              </div>
              <div className="header-text">
                <h1>{t('header.title')}</h1>
                <p className="tagline">{t('header.tagline')}</p>
              </div>
            </div>
            <button
              className="language-toggle"
              onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
              aria-label="Toggle language"
            >
              {language === 'en' ? 'हिंदी' : 'English'}
            </button>
          </div>
        </header>

        <nav className="nav" role="navigation" aria-label="Main navigation">
          <NavLink to="/" end className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            {t('nav.beneficiary')}
          </NavLink>
          <NavLink to="/grievance" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            {t('nav.grievance')}
          </NavLink>
          <NavLink to="/operator" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            {t('nav.operator')}
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            {t('nav.dashboard')}
          </NavLink>
        </nav>

        <ConnectivityStatusBar />

        <main className="main">
          <Routes>
            <Route path="/" element={<BeneficiaryDiscovery />} />
            <Route path="/grievance" element={<GrievancePortal />} />
            <Route path="/operator" element={<OperatorAssistant />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>{t('footer.text')}</p>
        </footer>
      </div>
    </Router>
  )
}

function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  )
}

export default App
