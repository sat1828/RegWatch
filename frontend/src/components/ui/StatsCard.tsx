import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

interface StatsCardProps {
  title: string
  value: number | string
  icon: ReactNode
  gradient?: string
  subtitle?: string
  delay?: number
}

export function StatsCard({ title, value, icon, gradient = 'from-primary-500 to-purple-500', subtitle, delay = 0 }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: 'easeOut' }}
      className="glass rounded-2xl p-6 hover:shadow-glow dark:hover:shadow-glow-dark transition-all duration-300 hover:-translate-y-1"
    >
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="text-3xl font-bold text-[var(--text-primary)]">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-400 dark:text-gray-500">{subtitle}</p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
          {icon}
        </div>
      </div>
    </motion.div>
  )
}
