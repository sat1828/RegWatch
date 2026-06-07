import { clsx } from 'clsx'

export function RiskBadge({ score, category }: { score?: number | null; category?: string }) {
  if (score === null || score === undefined) {
    return <span className="text-xs text-gray-400">N/A</span>
  }

  let colorClass: string
  let label: string

  if (category) {
    label = category
    colorClass = ({
      CRITICAL: 'risk-critical',
      HIGH: 'risk-high',
      MEDIUM: 'risk-medium',
      LOW: 'risk-low',
      NEGLIGIBLE: 'risk-negligible',
    } as Record<string, string>)[category] || 'text-gray-500'
  } else if (score >= 0.8) {
    colorClass = 'risk-critical'
    label = 'Critical'
  } else if (score >= 0.6) {
    colorClass = 'risk-high'
    label = 'High'
  } else if (score >= 0.4) {
    colorClass = 'risk-medium'
    label = 'Medium'
  } else if (score >= 0.2) {
    colorClass = 'risk-low'
    label = 'Low'
  } else {
    colorClass = 'risk-negligible'
    label = 'Negligible'
  }

  return (
    <span className={clsx('text-xs font-semibold', colorClass)}>
      {label} ({score.toFixed(2)})
    </span>
  )
}
