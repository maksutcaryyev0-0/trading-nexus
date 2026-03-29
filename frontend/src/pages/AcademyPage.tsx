const topics = [
  { title: 'ICT Concepts', desc: 'Order blocks, FVG, liquidity sweeps' },
  { title: 'Wyckoff Method', desc: 'Accumulation, distribution, spring' },
  { title: 'Risk Management', desc: 'Kelly criterion, position sizing' },
  { title: 'Market Structure', desc: 'BOS, CHOCH, MSS patterns' },
  { title: 'Price Action', desc: 'Candlestick patterns, S/R levels' },
  { title: 'VSA', desc: 'Volume spread analysis basics' },
]
 
export default function AcademyPage() {
  return (
    <div style={{ padding: '2rem', color: '#fff' }}>
      <h1 style={{ color: '#00d4ff', fontSize: '1.8rem', marginBottom: '2rem' }}>Academy</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1rem' }}>
        {topics.map(topic => (
          <div key={topic.title} style={{ background: '#111318', border: '1px solid #1e2530', borderRadius: '12px', padding: '1.5rem', cursor: 'pointer' }}
            onMouseOver={e => (e.currentTarget.style.borderColor = '#00d4ff')}
            onMouseOut={e => (e.currentTarget.style.borderColor = '#1e2530')}>
            <p style={{ color: '#00d4ff', fontWeight: 600, marginBottom: '0.5rem' }}>{topic.title}</p>
            <p style={{ color: '#666', fontSize: '0.85rem' }}>{topic.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
