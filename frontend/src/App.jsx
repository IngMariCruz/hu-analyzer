import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AnalyzerPage from './pages/AnalyzerPage'
import AdminPage from './pages/AdminPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AnalyzerPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </BrowserRouter>
  )
}
