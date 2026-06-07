import { clsx } from 'clsx'

const statusStyles: Record<string, string> = {
  DETECTED: 'status-detected',
  ANALYZED: 'status-analyzed',
  MAPPED: 'status-mapped',
  SCORED: 'status-scored',
  NOTIFIED: 'status-notified',
  PENDING_REVIEW: 'status-pending',
  APPROVED: 'status-approved',
  REJECTED: 'status-rejected',
  CLOSED: 'status-closed',
  CRITICAL: 'status-rejected',
  HIGH: 'status-scored',
  MEDIUM: 'status-pending',
  LOW: 'status-mapped',
  INFO: 'status-analyzed',
}

export function StatusBadge({ status }: { status: string }) {
  const style = statusStyles[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
  return (
    <span className={clsx('status-badge', style)}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
