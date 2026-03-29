import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
 
export default function LoginPage() {
  const navigate = useNavigate()
  const { setToken } = useAuthStore()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
 
  const apiUrl = import.meta.env.VITE_API_URL || ''
 
  const handleLogin = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()
      if (res.ok && data.access_token) {
        setToken(data.access_token)
        navigate('/app')
      } else {
        setError(data.detail || 'Login failed')
      }
    } catch (e) {
      setError('Connection error')
    }
    setLoading(false)
  }
 
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0c0f',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        background: '#111318',
        border: '1px solid #1e2530',
        borderRadius: '16px',
        padding: '2.5rem',
        width: '360px',
      }}>
        <h1 style={{ color: '#00d4ff', fontSize: '2rem', fontWeight: 700, textAlign: 'center', marginBottom: '0.5rem' }}>
          NEXUS
        </h1>
        <p style={{ color: '#666', textAlign: 'center', marginBottom: '2rem', fontSize: '0.9rem' }}>
          Trading Operating System
        </p>
 
        {error && (
          <div style={{ background: '#2a1515', border: '1px solid #ff4444', borderRadius: '8px', padding: '0.75rem', marginBottom: '1rem', color: '#ff6666', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}
 
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            style={{
              width: '100%',
              background: '#0a0c0f',
              border: '1px solid #1e2530',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: '#fff',
              fontSize: '1rem',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>
 
        <div style={{ marginBottom: '1.5rem' }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleLogin()}
            style={{
              width: '100%',
              background: '#0a0c0f',
              border: '1px solid #1e2530',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: '#fff',
              fontSize: '1rem',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>
 
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: '100%',
            background: loading ? '#0a3a4a' : '#00d4ff',
            color: loading ? '#666' : '#000',
            border: 'none',
            borderRadius: '8px',
            padding: '0.85rem',
            fontSize: '1rem',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </div>
    </div>
  )
}
