import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'

// Pages
import LoginPage     from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import TerminalPage  from './pages/TerminalPage'
import AnalysisPage  from './pages/AnalysisPage'
import JournalPage   from './pages/JournalPage'
import RiskPage      from './pages/RiskPage'
import CalendarPage  from './pages/CalendarPage'
import WatchlistPage from './pages/WatchlistPage'
import AcademyPage   from './pages/AcademyPage'
import SettingsPage  from './pages/SettingsPage'
import AIChatPage    from './pages/AIChatPage'
import LangSelectPage from './pages/LangSelectPage'
import Layout        from './components/Layout'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  const { lang } = useAuthStore()

  // RTL for Arabic
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'
  document.documentElement.lang = lang

  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/"      element={<Navigate to="/lang" replace />} />
        <Route path="/lang"  element={<LangSelectPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index            element={<DashboardPage />} />
          <Route path="terminal"  element={<TerminalPage />} />
          <Route path="analysis"  element={<AnalysisPage />} />
          <Route path="journal"   element={<JournalPage />} />
          <Route path="risk"      element={<RiskPage />} />
          <Route path="calendar"  element={<CalendarPage />} />
          <Route path="watchlist" element={<WatchlistPage />} />
          <Route path="academy"   element={<AcademyPage />} />
          <Route path="settings"  element={<SettingsPage />} />
          <Route path="ai"        element={<AIChatPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
