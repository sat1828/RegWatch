import { useEffect, useState } from 'react'
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
