import { motion } from 'framer-motion'
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
