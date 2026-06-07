import { motion } from 'framer-motion'

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
