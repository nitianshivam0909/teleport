import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CreateRequestPage from './pages/CreateRequestPage'
import AdminApprovalPage from './pages/AdminApprovalPage'
import AuditLogsPage from './pages/AuditLogsPage'

function Protected({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      {window.location.pathname !== '/login' && <NavBar />}
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Protected><DashboardPage /></Protected>} />
        <Route path="/request" element={<Protected><CreateRequestPage /></Protected>} />
        <Route path="/admin" element={<Protected><AdminApprovalPage /></Protected>} />
        <Route path="/audit" element={<Protected><AuditLogsPage /></Protected>} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  )
}
