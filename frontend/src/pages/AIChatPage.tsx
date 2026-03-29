import { useState } from 'react'
import { useAuthStore } from '../store/authStore'
 
export default function AIChatPage() {
  const { token } = useAuthStore()
  const [messages, setMessages] = useState<{role: string, text: string}[]>([
    { role: 'assistant', text: 'Hello! I am NEXUS AI. Ask me anything about trading.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const apiUrl = import.meta.env.VITE_API_URL || ''
 
  const send = async () => {
    if (!input.trim()) return
    const userMsg = input
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)
    try {
      const res = await fetch(`${apiUrl}/api/v1/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: userMsg }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', text: data.response || JSON.stringify(data) }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Connection error' }])
    }
    setLoading(false)
  }
 
  return (
    <div style={{ padding: '2rem', height: 'calc(100vh - 4rem)', display: 'flex', flexDirection: 'column' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '1rem' }}>AI Chat</h1>
      <div style={{ flex: 1, background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1rem', overflow: 'auto', marginBottom: '1rem' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '1rem', display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{ background: msg.role === 'user' ? '#00d4ff20' : '#1e2530', border: `1px solid ${msg.role === 'user' ? '#00d4ff' : '#2a3540'}`, borderRadius: '12px', padding: '0.75rem 1rem', maxWidth: '70%', color: '#fff', fontSize: '0.9rem' }}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && <div style={{ color: '#666', fontSize: '0.9rem' }}>Thinking...</div>}
      </div>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask anything about trading..."
          style={{ flex: 1, background: '#111318', border: '1px solid #1e2530', borderRadius: '8px', padding: '0.75rem', color: '#fff' }}
        />
        <button onClick={send} disabled={loading} style={{ background: '#00d4ff', color: '#000', border: 'none', borderRadius: '8px', padding: '0.75rem 1.5rem', fontWeight: 600, cursor: 'pointer' }}>Send</button>
      </div>
    </div>
  )
}
