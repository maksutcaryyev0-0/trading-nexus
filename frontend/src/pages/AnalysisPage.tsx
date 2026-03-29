import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
 
export default function AnalysisPage() {
  const { token } = useAuthStore()
  const [symbol, setSymbol] = useState('XAUUSD')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const apiUrl = import.meta.env.VITE_API_URL || ''
 
  const analyze = async () => {
    setLoading(true)
    setResult('')
    try {
      const res = await fetch(`${apiUrl}/api/v1/analysis/full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ symbol, timeframe: 'H1' }),
      })
      const data = await res.json()
      setResult(JSON.stringify(data, null, 2))
    } catch (e) {
      setResult('Error connecting to backend')
    }
    setLoading(false)
  }
 
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Analysis</h1>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <input value={symbol} onChange={e => setSymbol(e.target.value)}
          style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '8px', padding: '0.75rem 1rem', color: '#fff', fontSize: '1rem', width: '200px' }}
        />
        <button onClick={analyze} disabled={loading}
          style={{ background: '#00d4ff', color: '#000', border: 'none', borderRadius: '8px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
      {result && (
        <pre style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem', overflow: 'auto', fontSize: '0.85rem', color: '#ccc' }}>
          {result}
        </pre>
      )}
    </div>
  )
}
