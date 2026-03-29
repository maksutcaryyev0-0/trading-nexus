import { useState } from 'react'
 
export default function JournalPage() {
  const [entries] = useState([])
 
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Trade Journal</h1>
      <div style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '3rem', textAlign: 'center' }}>
        <p style={{ color: '#666', fontSize: '1.1rem' }}>No trades recorded yet.</p>
        <p style={{ color: '#444', fontSize: '0.9rem', marginTop: '0.5rem' }}>Your trades will appear here after you log them.</p>
      </div>
    </div>
  )
}
