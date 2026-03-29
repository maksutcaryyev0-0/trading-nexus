import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
 
const apis = [
  { key: 'ANTHROPIC_API_KEY', label: 'Anthropic Claude', desc: 'AI analysis engine', required: true },
  { key: 'GEMINI_API_KEY', label: 'Google Gemini', desc: 'Free AI model' },
  { key: 'GROQ_API_KEY', label: 'Groq', desc: 'Fast free AI' },
  { key: 'TWELVE_DATA_KEY', label: 'TwelveData', desc: 'Market data' },
  { key: 'ALPHA_VANTAGE_KEY', label: 'Alpha Vantage', desc: 'Stock data' },
  { key: 'NEWS_API_KEY', label: 'NewsAPI', desc: 'News feed' },
  { key: 'TELEGRAM_BOT_TOKEN', label: 'Telegram Bot', desc: 'Notifications' },
]
 
export default function SettingsPage() {
  const { username, logout } = useAuthStore()
  const [keys, setKeys] = useState<Record<string, string>>({})
 
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Settings</h1>
 
      <div style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem', marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Account</h2>
        <p style={{ color: '#666' }}>Username: <span style={{ color: '#fff' }}>{username}</span></p>
        <button onClick={logout} style={{ marginTop: '1rem', background: '#2a1515', border: '1px solid #ff4444', borderRadius: '8px', padding: '0.5rem 1rem', color: '#ff6666', cursor: 'pointer' }}>
          Sign Out
        </button>
      </div>
 
      <div style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem' }}>
        <h2 style={{ marginBottom: '0.5rem', fontSize: '1.1rem' }}>API Keys</h2>
        <p style={{ color: '#666', fontSize: '0.85rem', marginBottom: '1.5rem' }}>Add your API keys to enable features. Keys are stored in Railway Variables.</p>
        {apis.map(api => (
          <div key={api.key} style={{ marginBottom: '1rem' }}>
            <p style={{ color: '#fff', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
              {api.label} {api.required && <span style={{ color: '#ff6666' }}>*</span>}
            </p>
            <p style={{ color: '#444', fontSize: '0.8rem', marginBottom: '0.4rem' }}>{api.desc}</p>
            <input
              type="password"
              placeholder={`Enter ${api.key}`}
              value={keys[api.key] || ''}
              onChange={e => setKeys(prev => ({ ...prev, [api.key]: e.target.value }))}
              style={{ width: '100%', background: '#0a0c0f', border: '1px solid #1e2530', borderRadius: '8px', padding: '0.6rem', color: '#fff', boxSizing: 'border-box', fontSize: '0.9rem' }}
            />
          </div>
        ))}
        <p style={{ color: '#444', fontSize: '0.8rem', marginTop: '1rem' }}>* Add these keys directly in Railway → Variables for them to take effect.</p>
      </div>
    </div>
  )
}
