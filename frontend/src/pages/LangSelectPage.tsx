import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
 
const languages = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
  { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
]
 
export default function LangSelectPage() {
  const navigate = useNavigate()
  const { setLang } = useAuthStore()
 
  const handleSelect = (code: string) => {
    setLang(code)
    navigate('/login')
  }
 
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0c0f',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: '2rem'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ color: '#00d4ff', fontSize: '2.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          NEXUS
        </h1>
        <p style={{ color: '#666', fontSize: '1rem' }}>Trading Operating System</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '280px' }}>
        {languages.map(lang => (
          <button
            key={lang.code}
            onClick={() => handleSelect(lang.code)}
            style={{
              background: '#111318',
              border: '1px solid #1e2530',
              borderRadius: '12px',
              padding: '1rem 1.5rem',
              color: '#fff',
              fontSize: '1.1rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              transition: 'all 0.2s',
            }}
            onMouseOver={e => (e.currentTarget.style.borderColor = '#00d4ff')}
            onMouseOut={e => (e.currentTarget.style.borderColor = '#1e2530')}
          >
            <span style={{ fontSize: '1.5rem' }}>{lang.flag}</span>
            <span>{lang.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
