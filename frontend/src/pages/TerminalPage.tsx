import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
 
export default function TerminalPage() {
  const { token } = useAuthStore()
  const [input, setInput] = useState('')
  const [output, setOutput] = useState<string[]>(['NEXUS Terminal v1.0.0', 'Type a command...'])
  const apiUrl = import.meta.env.VITE_API_URL || ''
 
  const run = async () => {
    if (!input.trim()) return
    setOutput(prev => [...prev, `> ${input}`])
    setInput('')
    setOutput(prev => [...prev, 'Command sent...'])
  }
 
  return (
    <div style={{ padding: '2rem', color: '#fff', height: 'calc(100vh - 4rem)', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '1rem' }}>Terminal</h1>
      <div style={{ flex: 1, background: '#050708', border: '1px solid #1e2530', borderRadius: '12px', padding: '1rem', fontFamily: 'monospace', fontSize: '0.9rem', overflow: 'auto', marginBottom: '1rem' }}>
        {output.map((line, i) => (
          <div key={i} style={{ color: line.startsWith('>') ? '#00d4ff' : '#ccc', marginBottom: '0.25rem' }}>{line}</div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && run()}
          placeholder="Enter command..."
          style={{ flex: 1, background: '#111318', border: '1px solid #1e2530', borderRadius: '8px', padding: '0.75rem', color: '#fff', fontFamily: 'monospace' }}
        />
        <button onClick={run} style={{ background: '#00d4ff', color: '#000', border: 'none', borderRadius: '8px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>Run</button>
      </div>
    </div>
  )
}
