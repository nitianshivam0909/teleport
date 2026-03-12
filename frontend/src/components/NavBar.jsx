import { Link, useNavigate } from 'react-router-dom'

export default function NavBar() {
  const role = localStorage.getItem('role')
  const navigate = useNavigate()

  const logout = () => {
    localStorage.clear()
    navigate('/login')
  }

  return (
    <nav className="bg-slate-800 text-white p-4 flex gap-4 items-center">
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/request">Create Request</Link>
      {(role === 'admin' || role === 'security') && <Link to="/audit">Audit Logs</Link>}
      {role === 'admin' && <Link to="/admin">Approvals</Link>}
      <button className="ml-auto bg-red-500 px-3 py-1 rounded" onClick={logout}>Logout</button>
    </nav>
  )
}
