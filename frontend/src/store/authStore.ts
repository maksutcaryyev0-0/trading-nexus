import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  token:    string | null
  role:     string
  lang:     string
  timezone: string
  username: string
  setAuth:  (data: { token: string; role: string; lang: string; timezone: string; username: string }) => void
  setLang:  (lang: string) => void
  setTimezone: (tz: string) => void
  logout:   () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token:    null,
      role:     'viewer',
      lang:     'en',
      timezone: 'Europe/Moscow',
      username: '',

      setAuth: (data) => set({
        token:    data.token,
        role:     data.role,
        lang:     data.lang,
        timezone: data.timezone,
        username: data.username,
      }),

      setLang: (lang) => set({ lang }),

      setTimezone: (timezone) => set({ timezone }),

      logout: () => set({
        token:    null,
        role:     'viewer',
        username: '',
      }),
    }),
    { name: 'nexus-auth' }
  )
)
