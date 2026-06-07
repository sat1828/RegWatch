import { useEffect, useState } from 'react'
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
