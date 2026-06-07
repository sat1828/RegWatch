import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import type { ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  glow?: boolean
  delay?: number
}

export function GlassCard({ children, className, hover = false, glow = false, delay = 0 }: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: 'easeOut' }}
      className={clsx(
        'glass rounded-2xl p-6',
        hover && 'glass-card-hover',
        glow && 'shadow-glow dark:shadow-glow-dark',
        className
      )}
    >
      {children}
    </motion.div>
  )
}
