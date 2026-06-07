import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@/context/ThemeContext'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { Documents } from '@/pages/Documents'
import { DocumentDetail } from '@/pages/DocumentDetail'
import { Sources } from '@/pages/Sources'
import { Pipeline } from '@/pages/Pipeline'
import { Drafts } from '@/pages/Drafts'
import { Settings } from '@/pages/Settings'

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/documents/:id" element={<DocumentDetail />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/drafts" element={<Drafts />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
