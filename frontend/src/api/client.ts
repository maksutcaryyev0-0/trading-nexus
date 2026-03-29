import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 60000,
})

// Auto-attach JWT token
api.interceptors.request.use((config) => {
  const auth = JSON.parse(localStorage.getItem('nexus-auth') || '{}')
  const token = auth?.state?.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('nexus-auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ─────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string, lang: string) =>
    api.post('/auth/login', { username, password, lang }),
  me: () => api.get('/auth/me'),
  timezones: () => api.get('/auth/timezones'),
  languages: () => api.get('/auth/languages'),
}

// ── Analysis ─────────────────────────────────────────────
export const analysisApi = {
  full: (symbol: string, lang: string, timezone: string) =>
    api.post('/analysis/full', { symbol, lang, timezone }),
  quick: (symbol: string, question: string, lang: string) =>
    api.post('/analysis/quick', { symbol, question, lang }),
  price: (symbol: string) => api.get(`/analysis/price/${symbol}`),
  ohlcv: (symbol: string, timeframe = '1h', limit = 200) =>
    api.get(`/analysis/ohlcv/${symbol}`, { params: { timeframe, limit } }),
  sessions: (timezone: string) =>
    api.get('/analysis/sessions', { params: { timezone } }),
  assets: () => api.get('/analysis/assets'),
  timeframes: () => api.get('/analysis/timeframes'),
}

// ── Risk ─────────────────────────────────────────────────
export const riskApi = {
  positionSize: (data: object) => api.post('/risk/position-size', data),
  killSwitch: (action: string, reason?: string) =>
    api.post('/risk/kill-switch', { action, reason }),
  killStatus: () => api.get('/risk/kill-switch/status'),
  psychologyCheck: (data: object) => api.post('/risk/psychology-check', data),
  var: (returns: number[], confidence = 0.95) =>
    api.post('/risk/var', { returns, confidence }),
  kelly: (data: object) => api.post('/risk/kelly', data),
}

// ── AI ───────────────────────────────────────────────────
export const aiApi = {
  chat: (message: string, lang: string, symbol?: string) =>
    api.post('/ai/chat', { message, lang, symbol }),
  morningBrief: (lang: string, timezone: string) =>
    api.post('/ai/morning-brief', { lang, timezone }),
  autopsy: (trade: object, lang: string) =>
    api.post('/ai/autopsy', { trade, lang }),
  psychology: (sessionData: object, lang: string) =>
    api.post('/ai/psychology', { session_data: sessionData, lang }),
  models: () => api.get('/ai/models'),
}

// ── Journal ──────────────────────────────────────────────
export const journalApi = {
  trades: () => api.get('/journal/trades'),
  createTrade: (data: object) => api.post('/journal/trades', data),
}

// ── Calendar ─────────────────────────────────────────────
export const calendarApi = {
  events: () => api.get('/calendar/events'),
}

// ── Watchlist ────────────────────────────────────────────
export const watchlistApi = {
  get: () => api.get('/watchlist/'),
  add: (symbol: string, category?: string) =>
    api.post('/watchlist/add', { symbol, category }),
}

// ── Strategies ───────────────────────────────────────────
export const strategiesApi = {
  list: () => api.get('/strategies/'),
}

// ── Academy ──────────────────────────────────────────────
export const academyApi = {
  modules: () => api.get('/academy/modules'),
}

// ── Settings ─────────────────────────────────────────────
export const settingsApi = {
  apiKeys: () => api.get('/settings/api-keys/list'),
}

// ── Notifications ────────────────────────────────────────
export const notificationsApi = {
  test: (channels: string[]) =>
    api.post('/notifications/test', { channels }),
}

// ── Settings / API Hub ────────────────────────────────────
export const settingsHubApi = {
  services:  ()                          => api.get('/settings/services'),
  categories:()                          => api.get('/settings/categories'),
  status:    ()                          => api.get('/settings/status'),
  save:      (service_id: string, key_value: string, extra_value?: string) =>
    api.post('/settings/save', { service_id, key_value, extra_value }),
  test:      (service_id: string, key_value: string) =>
    api.post('/settings/test', { service_id, key_value }),
  remove:    (service_id: string)        => api.delete(`/settings/remove/${service_id}`),
}
