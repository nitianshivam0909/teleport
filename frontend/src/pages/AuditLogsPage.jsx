import { useEffect, useState } from 'react'
import api from '../lib/api'

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([])

  useEffect(() => {
    api.get('/audit/logs').then((r) => setLogs(r.data))
  }, [])

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Audit Logs</h2>
      <div className="bg-white rounded shadow overflow-auto">
        <table className="w-full">
          <thead className="bg-slate-200"><tr><th className="p-2">Time</th><th className="p-2">Actor</th><th className="p-2">Action</th><th className="p-2">Details</th></tr></thead>
          <tbody>
            {logs.map((l, i) => (
              <tr key={i} className="border-t"><td className="p-2">{new Date(l.created_at).toLocaleString()}</td><td className="p-2">{l.actor}</td><td className="p-2">{l.action}</td><td className="p-2">{l.details}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
