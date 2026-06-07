import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Search } from 'lucide-react'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { RiskBadge } from '@/components/ui/RiskBadge'
import { api } from '@/services/api'
import type { DocumentListItem } from '@/types'

export function Documents() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(0)

  useEffect(() => {
    setLoading(true)
    api.listDocuments({ skip: page * 20, limit: 20, status: statusFilter || undefined })
      .then(d => { setDocuments(d.items); setTotal(d.total) })
      .catch(console.error).finally(() => setLoading(false))
  }, [page, statusFilter])

  const filtered = search ? documents.filter(d => d.title.toLowerCase().includes(search.toLowerCase())) : documents

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Documents</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">{total} regulatory documents tracked</p>
      </motion.div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input type="text" placeholder="Search documents..." value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 glass rounded-xl text-sm text-[var(--text-primary)] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
        </div>
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(0) }}
          className="px-4 py-2.5 glass rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30">
          <option value="">All Status</option>
          {['DETECTED', 'ANALYZED', 'MAPPED', 'SCORED', 'NOTIFIED', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'CLOSED'].map(s => (
            <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32"><div className="w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      ) : (
        <div className="space-y-3">
          {filtered.map((doc, i) => (
            <motion.div key={doc.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}
              className="glass rounded-xl p-4 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
              onClick={() => window.location.href = '/documents/' + doc.id}>
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-[var(--text-primary)] truncate">{doc.title}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{doc.source_name} &middot; {doc.document_type}</p>
                </div>
                <div className="flex items-center gap-3 ml-4">
                  <span className="text-xs text-gray-400">{doc.obligation_count} obligations</span>
                  <RiskBadge score={doc.risk_score} />
                  <StatusBadge status={doc.status} />
                </div>
              </div>
            </motion.div>
          ))}
          {filtered.length === 0 && <div className="text-center py-12 text-gray-400">No documents found</div>}
          <div className="flex items-center justify-between pt-4">
            <span className="text-sm text-gray-400">Showing {page * 20 + 1}-{Math.min((page + 1) * 20, total)} of {total}</span>
            <div className="flex gap-2">
              <button disabled={page === 0} onClick={() => setPage(p => p - 1)} className="px-4 py-2 glass rounded-xl text-sm disabled:opacity-50">Previous</button>
              <button disabled={(page + 1) * 20 >= total} onClick={() => setPage(p => p + 1)} className="px-4 py-2 glass rounded-xl text-sm disabled:opacity-50">Next</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
