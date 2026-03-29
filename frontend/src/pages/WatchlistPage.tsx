import { useState } from 'react'
 
const defaultSymbols = ['XAUUSD', 'BTCUSDT', 'EURUSD', 'GBPUSD', 'USDJPY', 'ETHUSD']
 
export default function WatchlistPage() {
  const [symbols] = useState(defaultSymbols)
 
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Watchlist</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1rem' }}>
        {symbols.map(symbol => (
          <div key={symbol} style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem' }}>
            <p style={{ color: '#00d4ff', fontWeight: 700, fontSize: '1.1rem' }}>{symbol}</p>
            <p style={{ color: '#666', fontSize: '0.85rem', marginTop: '0.5rem' }}>Loading...</p>
          </div>
        ))}
      </div>
    </div>
  )
}
