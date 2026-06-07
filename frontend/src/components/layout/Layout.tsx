import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

export function Layout() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="min-h-screen">
      <div className="fixed inset-0 bg-grid opacity-[0.03] dark:opacity-[0.05] pointer-events-none" />
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <Header collapsed={collapsed} onToggleSidebar={() => setCollapsed(!collapsed)} />
      <main
        className={`pt-16 min-h-screen transition-all duration-300 bg-[var(--bg-primary)] ${
          collapsed ? 'pl-[72px]' : 'pl-[260px]'
        }`}
      >
        <div className="p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
