import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'

export default function LoginPage() {
  const [username, setUsername] = useState('dev1')
  const [password, setPassword] = useState('changeme')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/auth/login', { username, password })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role)
      localStorage.setItem('username', username)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form className="bg-white shadow-md rounded p-8 w-full max-w-md" onSubmit={submit}>
        <h1 className="text-xl font-bold mb-4">PAM Portal Login</h1>
        <input className="w-full border p-2 mb-3" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" />
        <input type="password" className="w-full border p-2 mb-3" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        {error && <p className="text-red-600 mb-3">{error}</p>}
        <button className="w-full bg-blue-600 text-white py-2 rounded">Sign In</button>
      </form>
    </div>
  )
}
