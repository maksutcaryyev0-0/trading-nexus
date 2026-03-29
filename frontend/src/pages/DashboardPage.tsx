import { useAuthStore } from '../store/authStore'
 
export default function DashboardPage() {
  const { username } = useAuthStore()
  const apiUrl = import.meta.env.VITE_API_URL || ''
 
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '0.5rem' }}>Dashboard</h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>Welcome back, {username}</p>
 
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {[
          { label: 'Total Trades', value: '0', color: '#00d4ff' },
          { label: 'Win Rate', value: '0%', color: '#00ff88' },
          { label: 'P&L Today', value: '$0', color: '#ffaa00' },
          { label: 'Active Positions', value: '0', color: '#ff6688' },
        ].map(stat => (
          <div key={stat.label} style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem' }}>
            <p style={{ color: '#666', fontSize: '0.85rem', marginBottom: '0.5rem' }}>{stat.label}</p>
            <p style={{ color: stat.color, fontSize: '2rem', fontWeight: 700 }}>{stat.value}</p>
          </div>
        ))}
      </div>
 
      <div style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem' }}>
        <h2 style={{ color: '#fff', marginBottom: '1rem' }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {['Analyze XAUUSD', 'Analyze BTCUSDT', 'Analyze EURUSD', 'Open Journal'].map(action => (
            <button key={action} style={{
              background: '#0a0c0f', border: '1px solid #1e2530', borderRadius: '8px',
              padding: '0.75rem 1.25rem', color: '#fff', cursor: 'pointer', fontSize: '0.9rem'
            }}>
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
