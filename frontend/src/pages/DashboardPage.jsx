import { useEffect, useState } from 'react'
import api from '../lib/api'

export default function DashboardPage() {
  const [requests, setRequests] = useState([])

  useEffect(() => {
    api.get('/requests').then((r) => setRequests(r.data.requests))
  }, [])

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Requests</h2>
      <div className="bg-white rounded shadow overflow-auto">
        <table className="w-full">
          <thead className="bg-slate-200">
            <tr><th className="p-2 text-left">User</th><th className="p-2 text-left">Resource</th><th className="p-2">Role</th><th className="p-2">Status</th><th className="p-2">Approvals</th></tr>
          </thead>
          <tbody>
            {requests.map((r) => (
              <tr key={r.id} className="border-t"><td className="p-2">{r.username}</td><td className="p-2">{r.resource}</td><td className="p-2 text-center">{r.role_requested}</td><td className="p-2 text-center">{r.status}</td><td className="p-2 text-center">{r.approvals_count}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
