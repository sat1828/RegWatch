import os

BASE = "D:\\ALL SOFTWARE PROJECTS\\RegWatch"

FILES: dict[str, str] = {}

FILES["frontend\\src\\vite-env.d.ts"] = """/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
"""

FILES["frontend\\src\\main.tsx"] = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
"""

FILES["frontend\\src\\App.tsx"] = """import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@/context/ThemeContext'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Documents } from '@/pages/Documents'
import { DocumentDetail } from '@/pages/DocumentDetail'
import { Sources } from '@/pages/Sources'
import { Pipeline } from '@/pages/Pipeline'
import { Drafts } from '@/pages/Drafts'
import { Settings } from '@/pages/Settings'

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/documents/:id" element={<DocumentDetail />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/drafts" element={<Drafts />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
"""

FILES["frontend\\src\\components\\dashboard\\RiskGauge.tsx"] = """import { motion } from 'framer-motion'

interface RiskGaugeProps {
  score: number
  label: string
  size?: number
}

export function RiskGauge({ score, label, size = 120 }: RiskGaugeProps) {
  const radius = (size - 20) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference * (1 - Math.min(score, 1))
  const center = size / 2
  const color = score >= 0.8 ? '#ef4444' : score >= 0.6 ? '#f97316' : score >= 0.4 ? '#eab308' : score >= 0.2 ? '#3b82f6' : '#22c55e'

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={center} cy={center} r={radius} fill="none" stroke="currentColor" strokeWidth="8" className="text-gray-200 dark:text-gray-700" />
        <motion.circle cx={center} cy={center} r={radius} fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" strokeDasharray={circumference} initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset }} transition={{ duration: 1.5, ease: 'easeOut' }} />
      </svg>
      <span className="text-2xl font-bold" style={{ color }}>{(score * 100).toFixed(0)}%</span>
      <span className="text-xs text-gray-500 dark:text-gray-400">{label}</span>
    </div>
  )
}
"""

FILES["frontend\\src\\pages\\Dashboard.tsx"] = """import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, FileText, AlertTriangle, Shield, FileCheck, Play, Globe } from 'lucide-react'
import { StatsCard } from '@/components/ui/StatsCard'
import { GlassCard } from '@/components/ui/GlassCard'
import { RiskGauge } from '@/components/dashboard/RiskGauge'
import { api } from '@/services/api'
import type { DashboardStats } from '@/types'

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    api.getDashboardStats().then(s => { setStats(s); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const runPipeline = async () => {
    setRunning(true)
    try { await api.runPipeline('watcher'); const s = await api.getDashboardStats(); setStats(s) } catch (e) { console.error(e) }
    setRunning(false)
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Regulatory compliance overview</p>
        </div>
        <button onClick={runPipeline} disabled={running} className="btn-primary flex items-center gap-2 disabled:opacity-50">
          <Play className="w-4 h-4" />{running ? 'Running...' : 'Run Pipeline'}
        </button>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <StatsCard title="Active Sources" value={stats?.total_sources ?? 0} icon={<Globe className="w-5 h-5 text-white" />} gradient="from-blue-500 to-cyan-500" delay={0} />
        <StatsCard title="Documents" value={stats?.total_documents ?? 0} icon={<FileText className="w-5 h-5 text-white" />} gradient="from-primary-500 to-purple-500" delay={0.1} />
        <StatsCard title="Obligations" value={stats?.total_obligations ?? 0} icon={<Activity className="w-5 h-5 text-white" />} gradient="from-orange-500 to-red-500" subtitle={` + "${stats?.critical_obligations ?? 0}" + ` critical`} delay={0.2} />
        <StatsCard title="High Risk" value={stats?.high_risk_items ?? 0} icon={<AlertTriangle className="w-5 h-5 text-white" />} gradient="from-red-500 to-pink-500" delay={0.3} />
        <StatsCard title="Compliance Gaps" value={stats?.total_gaps ?? 0} icon={<Shield className="w-5 h-5 text-white" />} gradient="from-yellow-500 to-orange-500" delay={0.4} />
        <StatsCard title="Pending Reviews" value={stats?.pending_reviews ?? 0} icon={<FileCheck className="w-5 h-5 text-white" />} gradient="from-green-500 to-emerald-500" delay={0.5} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard>
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-6">Risk Distribution</h2>
          <div className="grid grid-cols-3 gap-6">
            <RiskGauge score={0.85} label="Penalty Risk" size={130} />
            <RiskGauge score={0.62} label="Deadline Risk" size={130} />
            <RiskGauge score={0.43} label="Enforcement Risk" size={130} />
          </div>
        </GlassCard>
        <GlassCard>
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Pipeline Status</h2>
          <div className="space-y-4">
            {[
              { name: 'Watcher', color: 'bg-blue-500' },
              { name: 'Analysis', color: 'bg-purple-500' },
              { name: 'Mapping', color: 'bg-cyan-500' },
              { name: 'Risk Scoring', color: 'bg-orange-500' },
              { name: 'Reporter', color: 'bg-green-500' },
            ].map(a => (
              <div key={a.name} className="flex items-center justify-between py-2">
                <div className="flex items-center gap-3">
                  <div className={'w-2.5 h-2.5 rounded-full ' + a.color + ' animate-glow'} />
                  <span className="text-sm font-medium text-[var(--text-primary)]">{a.name}</span>
                </div>
                <span className="text-xs text-gray-400">Ready</span>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
"""

FILES["frontend\\src\\pages\\Documents.tsx"] = """import { useEffect, useState } from 'react'
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
"""

FILES["frontend\\src\\pages\\DocumentDetail.tsx"] = """import { useEffect, useState } from 'react'
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
"""

FILES["frontend\\src\\pages\\Sources.tsx"] = """import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Trash2, Globe, ExternalLink } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { api } from '@/services/api'
import type { RegulatorySource, SourceCreate } from '@/types'

export function Sources() {
  const [sources, setSources] = useState<RegulatorySource[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<SourceCreate>({ name: '', url: '', source_type: 'html_index', jurisdiction: 'IN', regulator: 'SEBI' })
  const load = () => { setLoading(true); api.listSources().then(setSources).catch(console.error).finally(() => setLoading(false)) }
  useEffect(() => { load() }, [])

  const handleCreate = async () => {
    try { await api.createSource(form); setShowForm(false); setForm({ name: '', url: '', source_type: 'html_index', jurisdiction: 'IN', regulator: 'SEBI' }); load() } catch (e) { console.error(e) }
  }
  const handleDelete = async (id: string) => { try { await api.deleteSource(id); load() } catch (e) { console.error(e) } }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold text-[var(--text-primary)]">Sources</h1><p className="text-gray-500 dark:text-gray-400 mt-1">Regulatory data sources</p></div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Add Source</button>
      </motion.div>

      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
            <GlassCard className="space-y-4">
              <h3 className="font-semibold text-[var(--text-primary)]">New Regulatory Source</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input placeholder="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="px-3 py-2 glass rounded-xl text-sm text-[var(--text-primary)] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
                <input placeholder="URL" value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))}
                  className="px-3 py-2 glass rounded-xl text-sm text-[var(--text-primary)] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
                <select value={form.regulator} onChange={e => setForm(f => ({ ...f, regulator: e.target.value }))}
                  className="px-3 py-2 glass rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30">
                  <option>SEBI</option><option>RBI</option><option>IRDAI</option><option>MCA</option>
                </select>
                <select value={form.source_type} onChange={e => setForm(f => ({ ...f, source_type: e.target.value }))}
                  className="px-3 py-2 glass rounded-xl text-sm text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500/30">
                  <option value="html_index">HTML Index</option><option value="pdf">PDF</option><option value="api">API</option>
                </select>
              </div>
              <div className="flex justify-end gap-3">
                <button onClick={() => setShowForm(false)} className="btn-secondary text-sm">Cancel</button>
                <button onClick={handleCreate} className="btn-primary text-sm">Create</button>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {loading ? (
        <div className="flex items-center justify-center h-32"><div className="w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources.map((s, i) => (
            <motion.div key={s.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
              className="glass rounded-xl p-5 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"><Globe className="w-5 h-5 text-white" /></div>
                  <div><h3 className="font-semibold text-[var(--text-primary)]">{s.name}</h3><p className="text-xs text-gray-400">{s.regulator} &middot; {s.jurisdiction}</p></div>
                </div>
                <button onClick={() => handleDelete(s.id)} className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition-colors"><Trash2 className="w-4 h-4" /></button>
              </div>
              <a href={s.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-primary-500 hover:underline"><ExternalLink className="w-3 h-3" /> {s.url.slice(0, 60)}...</a>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>{s.source_type}</span><span>{s.is_active ? 'Active' : 'Inactive'}</span>
                {s.last_scraped_at && <span>Last: {new Date(s.last_scraped_at).toLocaleDateString()}</span>}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
"""

FILES["frontend\\src\\pages\\Pipeline.tsx"] = """import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, GitBranch, RefreshCw } from 'lucide-react'
import { GlassCard } from '@/components/ui/GlassCard'
import { api } from '@/services/api'

const agents = [
  { name: 'Watcher Agent', desc: 'Scrapes regulatory sources and detects new documents', color: 'from-blue-500 to-cyan-500' },
  { name: 'Analysis Agent', desc: 'Extracts obligations using Claude AI', color: 'from-purple-500 to-pink-500' },
  { name: 'Mapping Agent', desc: 'Maps obligations to internal policies via RAG', color: 'from-cyan-500 to-teal-500' },
  { name: 'Risk Scorer Agent', desc: 'Scores compliance risk across 3 dimensions', color: 'from-orange-500 to-red-500' },
  { name: 'Reporter Agent', desc: 'Generates policy drafts and sends notifications', color: 'from-green-500 to-emerald-500' },
]

export function Pipeline() {
  const [result, setResult] = useState<{ pipeline_id: string; status: string } | null>(null)
  const [loading, setLoading] = useState(false)

  const run = async (mode: 'full' | 'watcher') => {
    setLoading(true)
    try {
      const res = await api.runPipeline(mode)
      setResult(res)
      if (mode === 'full') {
        setTimeout(async () => {
          try { const s = await api.getPipelineStatus(res.pipeline_id); setResult(r => r ? { ...r, status: s.status } : r) } catch {}
        }, 3000)
      }
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">Pipeline</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">5-stage AI compliance pipeline</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => run('watcher')} disabled={loading} className="btn-secondary flex items-center gap-2 disabled:opacity-50"><RefreshCw className="w-4 h-4" /> Watcher</button>
          <button onClick={() => run('full')} disabled={loading} className="btn-primary flex items-center gap-2 disabled:opacity-50"><Play className="w-4 h-4" /> Run Full</button>
        </div>
      </motion.div>

      {result && (
        <GlassCard>
          <div className="flex items-center gap-3">
            <div className={'w-3 h-3 rounded-full ' + (result.status === 'completed' ? 'bg-green-500' : result.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500 animate-glow')} />
            <span className="font-medium text-[var(--text-primary)]">Pipeline {result.pipeline_id.slice(0, 8)}...</span>
            <span className="text-sm text-gray-400 capitalize">Status: {result.status}</span>
          </div>
        </GlassCard>
      )}

      <div className="relative">
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary-500 via-purple-500 to-green-500 opacity-20" />
        <div className="space-y-6">
          {agents.map((a, i) => (
            <motion.div key={a.name} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className="relative pl-16">
              <div className={'absolute left-3 w-6 h-6 rounded-full bg-gradient-to-br ' + a.color + ' flex items-center justify-center shadow-lg'}><GitBranch className="w-3 h-3 text-white" /></div>
              <GlassCard>
                <h3 className="font-semibold text-[var(--text-primary)]">{a.name}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{a.desc}</p>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
"""

FILES["frontend\\src\\pages\\Drafts.tsx"] = """import { useEffect, useState } from 'react'
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
"""

FILES["frontend\\src\\pages\\Settings.tsx"] = """import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { Shield, Bell, Database, Sliders } from 'lucide-react'

const sections = [
  { icon: Database, title: 'Data Sources', desc: 'Configure regulatory sources and scrape intervals', fields: ['Scrape Interval', 'Max Concurrent', 'Timeout'], gradient: 'from-blue-500 to-cyan-500' },
  { icon: Bell, title: 'Notifications', desc: 'Configure email and slack notification channels', fields: ['Email From', 'Slack Webhook', 'Digest Interval'], gradient: 'from-purple-500 to-pink-500' },
  { icon: Shield, title: 'Security', desc: 'API keys and authentication settings', fields: ['API Key', 'JWT Secret', 'Token Expiry'], gradient: 'from-orange-500 to-red-500' },
  { icon: Sliders, title: 'Scoring', desc: 'Risk scoring weights and thresholds', fields: ['Penalty Weight', 'Deadline Weight', 'Enforcement Weight'], gradient: 'from-green-500 to-emerald-500' },
]

export function Settings() {
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Configure RegWatch</p>
      </motion.div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {sections.map((s, i) => (
          <motion.div key={s.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <GlassCard>
              <div className="flex items-center gap-3 mb-6">
                <div className={'w-10 h-10 rounded-xl bg-gradient-to-br ' + s.gradient + ' flex items-center justify-center'}><s.icon className="w-5 h-5 text-white" /></div>
                <div><h2 className="font-semibold text-[var(--text-primary)]">{s.title}</h2><p className="text-sm text-gray-500 dark:text-gray-400">{s.desc}</p></div>
              </div>
              <div className="space-y-4">
                {s.fields.map(f => (
                  <div key={f}>
                    <label className="block text-sm text-gray-500 dark:text-gray-400 mb-1">{f}</label>
                    <div className="glass rounded-xl px-4 py-2.5 text-sm text-[var(--text-primary)] opacity-50">Configured via environment variables</div>
                  </div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
"""

for relpath, content in FILES.items():
    fullpath = os.path.join(BASE, relpath)
    os.makedirs(os.path.dirname(fullpath), exist_ok=True)
    with open(fullpath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"Wrote: {relpath}")
