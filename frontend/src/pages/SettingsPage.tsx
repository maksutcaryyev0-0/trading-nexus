import { useState, useEffect } from 'react'
import { api } from '../api/client'

const CAT_ICONS: Record<string,string> = {
  all:'⊞', ai:'◆', market:'◈', crypto:'₿',
  broker:'⊡', macro:'◎', news:'◉', notify:'◷', voice:'◑',
}
const CAT_NAMES: Record<string,string> = {
  all:'All', ai:'AI Models', market:'Market Data', crypto:'Crypto',
  broker:'Brokers', macro:'Macro', news:'News', notify:'Notifications', voice:'Voice',
}

interface Svc {
  id:string; name:string; cat:string; url:string
  free:boolean; price:string; desc:string; required:boolean
  configured:boolean; preview:string|null; test_ok:boolean|null
}

export default function SettingsPage() {
  const [svcs, setSvcs] = useState<Svc[]>([])
  const [cat, setCat] = useState('all')
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState<any>(null)
  const [modal, setModal] = useState<Svc|null>(null)
  const [keyVal, setKeyVal] = useState('')
  const [extraVal, setExtraVal] = useState('')
  const [show, setShow] = useState(false)
  const [saving, setSaving] = useState('')
  const [result, setResult] = useState<any>(null)

  useEffect(() => { load() }, [])

  async function load() {
    try {
      const [a,b] = await Promise.all([api.get('/settings/services'), api.get('/settings/status')])
      setSvcs(a.data.services); setStatus(b.data)
    } finally { setLoading(false) }
  }

  const cats = ['all', ...Array.from(new Set(svcs.map(s => s.cat)))]
  const list = svcs.filter(s =>
    (cat==='all'||s.cat===cat) &&
    (!q || s.name.toLowerCase().includes(q.toLowerCase()) || s.desc.toLowerCase().includes(q.toLowerCase()))
  )

  function open(s:Svc){ setModal(s); setKeyVal(''); setExtraVal(''); setResult(null); setShow(false) }

  async function doTest() {
    if (!modal||!keyVal.trim()) return
    setSaving('test')
    try { const r = await api.post('/settings/test',{service_id:modal.id,key_value:keyVal}); setResult(r.data) }
    catch { setResult({ok:false,error:'Request failed'}) }
    finally { setSaving('') }
  }

  async function doSave() {
    if (!modal||!keyVal.trim()) return
    setSaving('save')
    try {
      const r = await api.post('/settings/save',{service_id:modal.id,key_value:keyVal,extra_value:extraVal||null})
      setResult(r.data)
      if (r.data.saved) { await load(); setTimeout(()=>setModal(null),1200) }
    } catch(e:any) { setResult({ok:false,error:e.response?.data?.detail||'Failed'}) }
    finally { setSaving('') }
  }

  async function doRemove(s:Svc) {
    if (!confirm(`Remove ${s.name}?`)) return
    try { await api.delete(`/settings/remove/${s.id}`); await load() } catch{}
  }

  const needsExtra = (id:string) => ['binance','bybit','twilio'].includes(id)
  const extraLbl = (id:string) => id==='twilio'?'Auth Token':'API Secret'

  return (
    <div style={{padding:'1.5rem',maxWidth:920,margin:'0 auto'}}>

      {status && (
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:10,marginBottom:20}}>
          {[
            {l:'APIs configured', v:`${status.configured} / ${status.total}`, ok:status.configured>0},
            {l:'AI (Claude)',      v:status.ai_ready?'✓ Active':'✗ Add key',  ok:status.ai_ready},
            {l:'Telegram bot',    v:status.notify_ready?'✓ Active':'✗ Add key',ok:status.notify_ready},
          ].map(s=>(
            <div key={s.l} style={{
              background:'var(--color-background-secondary)',borderRadius:8,padding:'10px 14px',
              borderLeft:`3px solid ${s.ok?'#1D9E75':'#E24B4A'}`,
            }}>
              <div style={{fontSize:11,color:'var(--color-text-tertiary)',marginBottom:2}}>{s.l}</div>
              <div style={{fontSize:15,fontWeight:500,color:s.ok?'#1D9E75':'#E24B4A'}}>{s.v}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{display:'flex',gap:10,marginBottom:14,flexWrap:'wrap',alignItems:'center'}}>
        <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search..."
          style={{flex:1,minWidth:160,padding:'7px 12px',fontSize:13,
            border:'0.5px solid var(--color-border-secondary)',borderRadius:8,
            background:'var(--color-background-primary)',color:'var(--color-text-primary)',outline:'none'}}/>
        <div style={{display:'flex',gap:5,flexWrap:'wrap'}}>
          {cats.map(c=>(
            <button key={c} onClick={()=>setCat(c)}
              style={{padding:'5px 10px',fontSize:11,cursor:'pointer',borderRadius:20,
                border:'0.5px solid var(--color-border-secondary)',
                background:cat===c?'var(--color-text-primary)':'transparent',
                color:cat===c?'var(--color-background-primary)':'var(--color-text-secondary)'}}>
              {CAT_ICONS[c]||'·'} {CAT_NAMES[c]||c}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <p style={{color:'var(--color-text-secondary)',fontSize:13}}>Loading services...</p>
      ) : (
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(255px,1fr))',gap:10}}>
          {list.map(s=>(
            <div key={s.id} style={{
              background:'var(--color-background-primary)',borderRadius:10,padding:'12px 14px',
              border:`0.5px solid ${s.configured?(s.test_ok?'#1D9E75':'#E24B4A'):'var(--color-border-tertiary)'}`,
              display:'flex',flexDirection:'column',gap:8,
            }}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontSize:13,fontWeight:500,display:'flex',alignItems:'center',gap:4}}>
                    <span style={{overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{s.name}</span>
                    {s.required && <span style={{fontSize:9,color:'#E24B4A',flexShrink:0}}>req</span>}
                  </div>
                  <div style={{fontSize:11,color:'var(--color-text-tertiary)',marginTop:1}}>{s.desc}</div>
                </div>
                <div style={{display:'flex',flexDirection:'column',alignItems:'flex-end',gap:3,flexShrink:0,marginLeft:8}}>
                  <span style={{fontSize:10,padding:'2px 6px',borderRadius:10,fontWeight:500,
                    background:s.free?'#E1F5EE':'#FAEEDA',color:s.free?'#085041':'#633806'}}>
                    {s.price}
                  </span>
                  {s.configured && (
                    <span style={{fontSize:10,padding:'2px 6px',borderRadius:10,
                      background:s.test_ok?'#E1F5EE':'#FCEBEB',color:s.test_ok?'#085041':'#791F1F'}}>
                      {s.test_ok?'✓':'✗'}
                    </span>
                  )}
                </div>
              </div>

              {s.preview && (
                <div style={{fontSize:11,color:'var(--color-text-tertiary)',fontFamily:'monospace'}}>
                  ···{s.preview}
                </div>
              )}

              <div style={{display:'flex',gap:6}}>
                <button onClick={()=>open(s)}
                  style={{flex:1,padding:'6px 0',fontSize:12,cursor:'pointer',borderRadius:6,
                    border:'0.5px solid var(--color-border-secondary)',
                    background:s.configured?'var(--color-background-secondary)':'var(--color-text-primary)',
                    color:s.configured?'var(--color-text-secondary)':'var(--color-background-primary)'}}>
                  {s.configured?'Update':'+ Add Key'}
                </button>
                {s.configured && (
                  <button onClick={()=>doRemove(s)}
                    style={{padding:'6px 8px',fontSize:12,cursor:'pointer',borderRadius:6,
                      border:'0.5px solid #E24B4A',background:'transparent',color:'#A32D2D'}}>✕</button>
                )}
                <a href={s.url} target="_blank" rel="noreferrer"
                  style={{padding:'6px 8px',fontSize:12,borderRadius:6,textDecoration:'none',
                    border:'0.5px solid var(--color-border-secondary)',color:'var(--color-text-secondary)'}}>↗</a>
              </div>
            </div>
          ))}
        </div>
      )}

      {modal && (
        <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.55)',
          display:'flex',alignItems:'center',justifyContent:'center',zIndex:1000,padding:'1rem'}}>
          <div style={{background:'var(--color-background-primary)',
            border:'0.5px solid var(--color-border-secondary)',
            borderRadius:14,padding:'1.5rem',width:'100%',maxWidth:420}}>

            <div style={{display:'flex',justifyContent:'space-between',marginBottom:14}}>
              <div>
                <div style={{fontSize:15,fontWeight:500}}>{modal.name}</div>
                <div style={{fontSize:12,color:'var(--color-text-secondary)',marginTop:2}}>{modal.desc}</div>
              </div>
              <button onClick={()=>setModal(null)}
                style={{background:'none',border:'none',fontSize:18,cursor:'pointer',
                  color:'var(--color-text-secondary)',alignSelf:'flex-start'}}>✕</button>
            </div>

            <div style={{marginBottom:12,padding:'8px 12px',
              background:'var(--color-background-secondary)',borderRadius:8,fontSize:12}}>
              Get your key at:{' '}
              <a href={modal.url} target="_blank" rel="noreferrer"
                style={{color:'#378ADD'}}>{modal.url}</a>
            </div>

            <div style={{marginBottom:10}}>
              <div style={{fontSize:12,color:'var(--color-text-secondary)',marginBottom:5}}>
                {modal.id==='telegram'?'Bot Token':modal.id==='twilio'?'Account SID':'API Key'}
              </div>
              <div style={{position:'relative'}}>
                <input value={keyVal} onChange={e=>setKeyVal(e.target.value)}
                  type={show?'text':'password'} placeholder="Paste your key here..."
                  style={{width:'100%',padding:'9px 36px 9px 12px',fontSize:13,
                    border:'0.5px solid var(--color-border-secondary)',borderRadius:8,
                    background:'var(--color-background-primary)',color:'var(--color-text-primary)',
                    outline:'none',boxSizing:'border-box'}}/>
                <button onClick={()=>setShow(!show)}
                  style={{position:'absolute',right:10,top:'50%',transform:'translateY(-50%)',
                    background:'none',border:'none',cursor:'pointer',
                    color:'var(--color-text-tertiary)',fontSize:13}}>
                  {show?'◎':'◉'}
                </button>
              </div>
            </div>

            {needsExtra(modal.id) && (
              <div style={{marginBottom:10}}>
                <div style={{fontSize:12,color:'var(--color-text-secondary)',marginBottom:5}}>
                  {extraLbl(modal.id)}
                </div>
                <input value={extraVal} onChange={e=>setExtraVal(e.target.value)}
                  type={show?'text':'password'} placeholder={`Paste ${extraLbl(modal.id)}...`}
                  style={{width:'100%',padding:'9px 12px',fontSize:13,
                    border:'0.5px solid var(--color-border-secondary)',borderRadius:8,
                    background:'var(--color-background-primary)',color:'var(--color-text-primary)',
                    outline:'none',boxSizing:'border-box'}}/>
              </div>
            )}

            {result && (
              <div style={{padding:'9px 12px',borderRadius:8,marginBottom:12,fontSize:12,
                background:result.ok?'#E1F5EE':'#FCEBEB',
                color:result.ok?'#085041':'#791F1F'}}>
                {result.ok
                  ? `✅ ${result.message||'Key works!'}`
                  : `❌ ${result.message||result.error||'Test failed'}`}
                {result.detail?.bot && ` — @${result.detail.bot}`}
              </div>
            )}

            <div style={{display:'flex',gap:8}}>
              <button onClick={doTest} disabled={!keyVal||saving==='test'}
                style={{flex:1,padding:'9px 0',fontSize:13,cursor:'pointer',
                  border:'0.5px solid var(--color-border-secondary)',borderRadius:8,
                  background:'var(--color-background-secondary)',color:'var(--color-text-secondary)',
                  opacity:!keyVal||saving==='test'?0.5:1}}>
                {saving==='test'?'Testing...':'Test'}
              </button>
              <button onClick={doSave} disabled={!keyVal||saving==='save'}
                style={{flex:2,padding:'9px 0',fontSize:13,cursor:'pointer',
                  border:'none',borderRadius:8,
                  background:'var(--color-text-primary)',color:'var(--color-background-primary)',
                  opacity:!keyVal||saving==='save'?0.5:1}}>
                {saving==='save'?'Saving...':'Save Key'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
