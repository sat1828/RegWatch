import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, ExternalLink, Clock } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { RiskBadge } from '@/components/ui/RiskBadge'
import { api } from '@/services/api'
import type { DocumentDetail as DocDetail } from '@/types'

export function DocumentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [doc, setDoc] = useState<DocDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    api.getDocument(id).then(setDoc).catch(console.error).finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
  if (!doc) return <div className="text-center py-12 text-gray-400">Document not found</div>

  return (
    <div className="space-y-6 max-w-4xl">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-4">
        <button onClick={() => navigate('/documents')} className="p-2 rounded-xl hover:glass transition-all"><ArrowLeft className="w-5 h-5 text-gray-500" /></button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">{doc.title}</h1>
            <StatusBadge status={doc.status} />
          </div>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{doc.source_name} &middot; {doc.document_type}</p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <GlassCard>
            <h2 className="font-semibold text-[var(--text-primary)] mb-3">Document Text</h2>
            <div className="max-h-96 overflow-y-auto scrollbar-thin glass rounded-xl p-4">
              <pre className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap font-sans">{doc.raw_text || 'No text extracted'}</pre>
            </div>
          </GlassCard>

          {doc.obligations.length > 0 && (
            <GlassCard>
              <h2 className="font-semibold text-[var(--text-primary)] mb-4">Obligations ({doc.obligations.length})</h2>
              <div className="space-y-3">
                {doc.obligations.map(o => (
                  <div key={o.id} className="glass rounded-xl p-4">
                    <div className="flex items-start justify-between mb-2">
                      <p className="text-sm font-medium text-[var(--text-primary)]">{o.obligation_text}</p>
                      <StatusBadge status={o.severity} />
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>{o.obligation_category}</span>
                      {o.regulation_reference && <span>{o.regulation_reference}</span>}
                      {o.deadline && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(o.deadline).toLocaleDateString()}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {doc.gaps.length > 0 && (
            <GlassCard>
              <h2 className="font-semibold text-[var(--text-primary)] mb-4">Compliance Gaps ({doc.gaps.length})</h2>
              <div className="space-y-3">
                {doc.gaps.map(g => (
                  <div key={g.id} className="glass rounded-xl p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className="text-xs font-medium text-gray-400 uppercase">{g.gap_type}</span>
                        <p className="text-sm text-[var(--text-primary)] mt-1">{g.gap_description}</p>
                      </div>
                      <StatusBadge status={g.severity} />
                    </div>
                    {g.recommendation && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Recommendation: {g.recommendation}</p>}
                    <div className="mt-2 text-xs text-gray-400">Confidence: {(g.confidence_score * 100).toFixed(0)}%</div>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}
        </div>

        <div className="space-y-6">
          <GlassCard>
            <h2 className="font-semibold text-[var(--text-primary)] mb-4">Risk Scores</h2>
            {doc.risk_scores.length > 0 ? doc.risk_scores.map(rs => (
              <div key={rs.id} className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Overall</span>
                  <RiskBadge score={rs.overall_score} category={rs.risk_category} />
                </div>
                <div className="h-2 glass rounded-full overflow-hidden">
                  <motion.div initial={{ width: 0 }} animate={{ width: (rs.overall_score * 100) + '%' }}
                    className="h-full rounded-full bg-gradient-to-r from-primary-500 to-purple-500" />
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between"><span>Penalty</span><span>{(rs.penalty_score * 100).toFixed(0)}%</span></div>
                  <div className="flex justify-between"><span>Deadline</span><span>{(rs.deadline_score * 100).toFixed(0)}%</span></div>
                  <div className="flex justify-between"><span>Enforcement</span><span>{(rs.enforcement_score * 100).toFixed(0)}%</span></div>
                </div>
                {rs.reasoning && <p className="text-xs text-gray-400 mt-2">{rs.reasoning}</p>}
              </div>
            )) : <p className="text-sm text-gray-400">Not scored yet</p>}
          </GlassCard>

          <GlassCard>
            <h2 className="font-semibold text-[var(--text-primary)] mb-3">Details</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-400">Type</span><span>{doc.document_type}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Amendment</span><span>{doc.is_amendment ? 'Yes' : 'No'}</span></div>
              {doc.published_date && <div className="flex justify-between"><span className="text-gray-400">Published</span><span>{new Date(doc.published_date).toLocaleDateString()}</span></div>}
            </div>
            <a href={doc.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-primary-500 hover:underline mt-4">
              <ExternalLink className="w-3 h-3" /> View Original
            </a>
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
