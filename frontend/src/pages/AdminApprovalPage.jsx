import { useEffect, useState } from 'react'
import api from '../lib/api'

export default function AdminApprovalPage() {
  const [requests, setRequests] = useState([])
  const [error, setError] = useState('')

  const load = async () => {
    const { data } = await api.get('/requests')
    setRequests(data.requests.filter((r) => r.status === 'pending'))
  }

  useEffect(() => {
    load().catch(() => setError('Failed to load requests'))
  }, [])

  const approve = async (id) => {
    await api.post(`/requests/${id}/approve`)
    load()
  }

  const deny = async (id) => {
    await api.post(`/requests/${id}/deny`)
    load()
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Pending Approvals</h2>
      {error && <p className="text-red-600">{error}</p>}
      <div className="space-y-3">
        {requests.map((r) => (
          <div key={r.id} className="bg-white p-4 shadow rounded flex items-center gap-4">
            <div className="flex-1">
              <div className="font-semibold">{r.username} → {r.role_requested} on {r.resource}</div>
              <div className="text-sm text-slate-600">Reason: {r.reason} | Ticket: {r.ticket_id}</div>
            </div>
            <button onClick={() => approve(r.id)} className="bg-green-600 text-white px-3 py-1 rounded">Approve</button>
            <button onClick={() => deny(r.id)} className="bg-red-600 text-white px-3 py-1 rounded">Deny</button>
          </div>
        ))}
      </div>
    </div>
  )
}
