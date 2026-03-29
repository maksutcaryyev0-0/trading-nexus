import { Outlet, NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'

const NAV = [
  { to: '/app',           key: 'nav_dash',     icon: '⊞' },
  { to: '/app/terminal',  key: 'nav_terminal', icon: '▣' },
  { to: '/app/analysis',  key: 'nav_analysis', icon: '◈' },
  { to: '/app/journal',   key: 'nav_journal',  icon: '◉' },
  { to: '/app/risk',      key: 'nav_risk',     icon: '⚠' },
  { to: '/app/calendar',  key: 'nav_calendar', icon: '◷' },
  { to: '/app/watchlist', key: 'nav_watchlist',icon: '◎' },
  { to: '/app/academy',   key: 'nav_academy',  icon: '◑' },
  { to: '/app/ai',        key: 'nav_ai',       icon: '◆' },
  { to: '/app/settings',  key: 'nav_settings', icon: '◐' },
]

export default function Layout() {
  const { t } = useTranslation()
  const { logout, username, lang } = useAuthStore()

  return (
    <div style={{
      display: 'flex', minHeight: '100vh',
      direction: lang === 'ar' ? 'rtl' : 'ltr'
    }}>
      <nav style={{
        width: 200, flexShrink: 0,
        borderRight: lang === 'ar' ? 'none' : '0.5px solid var(--color-border-tertiary)',
        borderLeft: lang === 'ar' ? '0.5px solid var(--color-border-tertiary)' : 'none',
        padding: '1rem 0', display: 'flex', flexDirection: 'column',
        background: 'var(--color-background-secondary)',
      }}>
        <div style={{
          padding: '0 1rem 1rem',
          borderBottom: '0.5px solid var(--color-border-tertiary)',
          marginBottom: 8,
        }}>
          <div style={{ fontSize: 14, fontWeight: 500, letterSpacing: 2 }}>NEXUS</div>
          <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)' }}>{username}</div>
        </div>

        {NAV.map(n => (
          <NavLink
            key={n.to} to={n.to} end={n.to === '/app'}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '8px 1rem', fontSize: 13,
              color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
              background: isActive ? 'var(--color-background-primary)' : 'transparent',
              textDecoration: 'none', borderRadius: 6, margin: '1px 8px',
              transition: 'all .15s',
            })}
          >
            <span style={{ fontSize: 14 }}>{n.icon}</span>
            {t(n.key)}
          </NavLink>
        ))}

        <div style={{ marginTop: 'auto', padding: '0 8px' }}>
          <button
            onClick={logout}
            style={{
              width: '100%', padding: 8, fontSize: 13,
              color: 'var(--color-text-secondary)',
              background: 'transparent',
              border: '0.5px solid var(--color-border-tertiary)',
              borderRadius: 6, cursor: 'pointer',
            }}
          >
            {t('logout')}
          </button>
        </div>
      </nav>

      <main style={{ flex: 1, overflow: 'auto' }}>
        <Outlet />
      </main>
    </div>
  )
}
