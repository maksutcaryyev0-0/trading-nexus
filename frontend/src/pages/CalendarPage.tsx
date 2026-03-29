export default function CalendarPage() {
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Economic Calendar</h1>
      <div style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '3rem', textAlign: 'center' }}>
        <p style={{ color: '#666' }}>Economic calendar coming soon.</p>
        <p style={{ color: '#444', fontSize: '0.9rem', marginTop: '0.5rem' }}>Add FRED_API_KEY in Settings to enable macro data.</p>
      </div>
    </div>
  )
}
