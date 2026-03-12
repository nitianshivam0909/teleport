import { useState } from 'react'
import api from '../lib/api'

export default function CreateRequestPage() {
  const [form, setForm] = useState({ resource: '', role_requested: 'jit-ssh', reason: '', ticket_id: '' })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setMsg('')
    try {
      const { data } = await api.post('/requests/create', form)
      setMsg(`Request created with Teleport ID: ${data.teleport_request_id}`)
      setForm({ resource: '', role_requested: 'jit-ssh', reason: '', ticket_id: '' })
    } catch (err) {
      setError(err.response?.data?.detail || 'Request failed')
    }
  }

  return (
    <div className="p-6 max-w-xl">
      <h2 className="text-2xl font-semibold mb-4">Create Access Request</h2>
      <form className="bg-white p-4 rounded shadow" onSubmit={submit}>
        <input className="w-full border p-2 mb-3" placeholder="Server/resource" value={form.resource} onChange={(e) => setForm({ ...form, resource: e.target.value })} required />
        <input className="w-full border p-2 mb-3" placeholder="Role" value={form.role_requested} onChange={(e) => setForm({ ...form, role_requested: e.target.value })} required />
        <textarea className="w-full border p-2 mb-3" placeholder="Reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} required />
        <input className="w-full border p-2 mb-3" placeholder="Ticket ID (required)" value={form.ticket_id} onChange={(e) => setForm({ ...form, ticket_id: e.target.value })} required />
        {msg && <p className="text-green-700 mb-2">{msg}</p>}
        {error && <p className="text-red-700 mb-2">{error}</p>}
        <button className="bg-blue-600 text-white px-4 py-2 rounded">Submit</button>
      </form>
    </div>
  )
}
