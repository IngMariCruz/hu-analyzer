import { useState } from 'react'
import { Link } from 'react-router-dom'
import AdminAuth from '../components/admin/AdminAuth'
import AdminDashboard from '../components/admin/AdminDashboard'
import { clearToken, getToken } from '../services/adminApi'

export default function AdminPage() {
  const [token, setTokenState] = useState(getToken())

  const handleAuthenticated = (newToken) => setTokenState(newToken)

  const handleLogout = () => {
    clearToken()
    setTokenState(null)
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9]">
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="font-bold text-gray-900 text-lg tracking-tight">
              HU Analyzer <span className="text-gray-300 font-normal">/ Admin</span>
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link to="/" className="text-sm text-gray-500 hover:text-violet-600 font-medium">
              ← Volver
            </Link>
            {token && (
              <button onClick={handleLogout} className="text-sm text-violet-600 hover:text-violet-700 font-medium">
                Cerrar sesión
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        {token ? (
          <AdminDashboard onUnauthorized={handleLogout} />
        ) : (
          <AdminAuth onAuthenticated={handleAuthenticated} />
        )}
      </main>
    </div>
  )
}
