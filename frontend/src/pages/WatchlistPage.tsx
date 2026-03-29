import { useTranslation } from 'react-i18next'
export default function WatchlistPage() {
  const { t } = useTranslation()
  return (
    <div style={{ padding: '1.5rem' }}>
      <h2 style={{ fontSize: '1.1rem', fontWeight: 500, marginBottom: '1rem' }}>Watchlist</h2>
      <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>Module loaded.</p>
    </div>
  )
}
