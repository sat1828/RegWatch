import { Menu, Moon, Sun } from 'lucide-react'
import { useTheme } from '@/context/ThemeContext'
import { Sidebar } from './Sidebar'

interface HeaderProps {
  collapsed: boolean
  onToggleSidebar: () => void
}

export function Header({ collapsed, onToggleSidebar }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className={`fixed top-0 right-0 z-30 h-16 glass border-b border-glass-border dark:border-glass-border-dark transition-all duration-300 ${collapsed ? 'left-[72px]' : 'left-[260px]'}`}>
      <div className="flex items-center justify-between h-full px-6">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-xl hover:glass transition-all duration-200 text-gray-500 dark:text-gray-400"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl hover:glass transition-all duration-200 text-gray-500 dark:text-gray-400"
          >
            {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          </button>

          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center text-white text-sm font-semibold shadow-lg shadow-primary-500/20">
            A
          </div>
        </div>
      </div>
    </header>
  )
}
