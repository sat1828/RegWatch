import { motion } from 'framer-motion'
import {
  Activity,
  FileText,
  Globe,
  GitBranch,
  FileCheck,
  Settings,
  Shield,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

const navItems = [
  { to: '/', icon: Activity, label: 'Dashboard', end: true },
  { to: '/documents', icon: FileText, label: 'Documents' },
  { to: '/sources', icon: Globe, label: 'Sources' },
  { to: '/pipeline', icon: GitBranch, label: 'Pipeline' },
  { to: '/drafts', icon: FileCheck, label: 'Drafts' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar({ collapsed }: SidebarProps) {
  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 260 }}
      className="fixed left-0 top-0 h-screen z-40 glass border-r border-glass-border dark:border-glass-border-dark"
    >
      <div className="flex flex-col h-full">
        <div className="flex items-center gap-3 px-4 h-16 border-b border-glass-border dark:border-glass-border-dark">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center shadow-lg shadow-primary-500/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-lg font-bold gradient-text"
            >
              RegWatch
            </motion.span>
          )}
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group',
                  isActive
                    ? 'glass text-primary-600 dark:text-primary-400 font-medium'
                    : 'text-gray-500 dark:text-gray-400 hover:glass hover:text-gray-700 dark:hover:text-gray-200'
                )
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-sm"
                >
                  {item.label}
                </motion.span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-glass-border dark:border-glass-border-dark">
          {!collapsed && (
            <div className="text-xs text-gray-400 dark:text-gray-500 text-center">
              RegWatch v1.0.0
            </div>
          )}
        </div>
      </div>
    </motion.aside>
  )
}
