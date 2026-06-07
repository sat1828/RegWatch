import { useState } from 'react'
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
