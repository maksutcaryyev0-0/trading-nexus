import { useState } from 'react'
 
export default function RiskPage() {
  const [balance, setBalance] = useState('10000')
  const [risk, setRisk] = useState('1')
  const [sl, setSl] = useState('50')
  const result = balance && risk && sl
    ? ((parseFloat(balance) * parseFloat(risk) / 100) / parseFloat(sl)).toFixed(2)
    : '0'
 
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Risk Calculator</h1>
      <div style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '2rem', maxWidth: '400px' }}>
        {[
          { label: 'Account Balance ($)', value: balance, set: setBalance },
          { label: 'Risk %', value: risk, set: setRisk },
          { label: 'Stop Loss (pips)', value: sl, set: setSl },
        ].map(field => (
          <div key={field.label} style={{ marginBottom: '1rem' }}>
            <p style={{ color: '#666', fontSize: '0.85rem', marginBottom: '0.4rem' }}>{field.label}</p>
            <input value={field.value} onChange={e => field.set(e.target.value)}
              style={{ width: '100%', background: '#0a0c0f', border: '1px solid #1e2530', borderRadius: '8px', padding: '0.75rem', color: '#fff', boxSizing: 'border-box' }}
            />
          </div>
        ))}
        <div style={{ background: '#0a1a2a', border: '1px solid #00d4ff', borderRadius: '8px', padding: '1rem', marginTop: '1rem', textAlign: 'center' }}>
          <p style={{ color: '#666', fontSize: '0.85rem' }}>Position Size</p>
          <p style={{ color: '#00d4ff', fontSize: '2rem', fontWeight: 700 }}>{result} lots</p>
        </div>
      </div>
    </div>
  )
}
