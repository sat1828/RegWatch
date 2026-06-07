import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FileCheck } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { api } from '@/services/api'
import type { PolicyDraft } from '@/types'

export function Drafts() {
  const [drafts, setDrafts] = useState<PolicyDraft[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    setLoading(true)
    api.listDrafts(statusFilter || undefined).then(setDrafts).catch(console.error).finally(() => setLoading(false))
  }, [statusFilter])

  const handleApprove = async (id: string) => {
    try { await api.reviewDraft(id, { status: 'APPROVED', reviewed_by: 'Admin' }); setDrafts(d => d.map(x => x.id === id ? { ...x, status: 'APPROVED' as const } : x)) } catch (e) { console.error(e) }
  }
  const handleReject = async (id: string) => {
    try { await api.reviewDraft(id, { status: 'REJECTED', reviewed_by: 'Admin' }); setDrafts(d => d.map(x => x.id === id ? { ...x, status: 'REJECTED' as const } : x)) } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold text-[var(--text-primary)]">Policy Drafts</h1><p className="text-gray-500 dark:text-gray-400 mt-1">AI-generated policy amendments</p></div>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="px-4 py-2.5 glass rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30">
          <option value="">All</option><option value="PENDING_REVIEW">Pending Review</option><option value="APPROVED">Approved</option><option value="REJECTED">Rejected</option>
        </select>
      </motion.div>

      {loading ? (
        <div className="flex items-center justify-center h-32"><div className="w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      ) : (
        <div className="space-y-4">
          {drafts.map((d, i) => (
            <motion.div key={d.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <GlassCard>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center"><FileCheck className="w-5 h-5 text-white" /></div>
                    <div>
                      <h3 className="font-semibold text-[var(--text-primary)]">{d.title}</h3>
                      {d.change_summary && <p className="text-sm text-gray-500 dark:text-gray-400">{d.change_summary}</p>}
                    </div>
                  </div>
                  <StatusBadge status={d.status} />
                </div>
                <div className="glass rounded-xl p-4 mb-4 max-h-48 overflow-y-auto scrollbar-thin">
                  <pre className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap font-sans">{d.content.slice(0, 1000)}{d.content.length > 1000 ? '...' : ''}</pre>
                </div>
                {d.status === 'PENDING_REVIEW' && (
                  <div className="flex gap-3 justify-end">
                    <button onClick={() => handleReject(d.id)} className="px-4 py-2 rounded-xl border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 text-sm hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">Reject</button>
                    <button onClick={() => handleApprove(d.id)} className="btn-primary text-sm">Approve</button>
                  </div>
                )}
                {d.reviewed_by && <div className="text-xs text-gray-400 mt-3">Reviewed by {d.reviewed_by}{d.review_notes ? ': ' + d.review_notes : ''}</div>}
              </GlassCard>
            </motion.div>
          ))}
          {drafts.length === 0 && <div className="text-center py-12 text-gray-400">No drafts found</div>}
        </div>
      )}
    </div>
  )
}
