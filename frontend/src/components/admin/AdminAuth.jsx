import { useEffect, useState } from 'react'
import { adminExists, adminLogin, adminRegister } from '../../services/adminApi'

export default function AdminAuth({ onAuthenticated }) {
  const [registered, setRegistered] = useState(null) // null = cargando
  const [mode, setMode] = useState('login')           // 'login' | 'register'
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    adminExists()
      .then((r) => { setRegistered(r); setMode(r ? 'login' : 'register') })
      .catch(() => { setRegistered(true); setMode('login') })
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const token = mode === 'register'
        ? await adminRegister(username.trim(), password)
        : await adminLogin(username.trim(), password)
      onAuthenticated(token)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const isRegister = mode === 'register'

  if (registered === null) {
    return (
      <div className="flex justify-center py-16">
        <div className="w-10 h-10 rounded-full border-4 border-violet-100 border-t-violet-600 animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-sm mx-auto">
      <div className="card p-7">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-violet-600 rounded-xl flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-gray-900">
            {isRegister ? 'Crear administrador' : 'Panel de administrador'}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {isRegister
              ? 'Registro de primer uso. Solo se permite un administrador.'
              : 'Inicia sesión para ver las métricas.'}
          </p>
        </div>

        <form onSubmit={submit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              minLength={isRegister ? 3 : undefined}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
              placeholder="admin"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              required
              minLength={isRegister ? 6 : undefined}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
              placeholder="••••••••"
            />
            {isRegister && (
              <p className="text-xs text-gray-400 mt-1">Mínimo 6 caracteres.</p>
            )}
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full py-2.5 bg-violet-600 hover:bg-violet-700 disabled:bg-violet-300
              text-white font-semibold rounded-lg transition-colors text-sm"
          >
            {busy ? 'Procesando...' : isRegister ? 'Crear cuenta' : 'Iniciar sesión'}
          </button>
        </form>

        <div className="mt-5 text-center text-sm text-gray-500">
          {isRegister ? (
            <button onClick={() => { setMode('login'); setError('') }} className="text-violet-600 hover:text-violet-700 font-medium">
              ¿Ya tienes una cuenta? Inicia sesión
            </button>
          ) : (
            !registered && (
              <button onClick={() => { setMode('register'); setError('') }} className="text-violet-600 hover:text-violet-700 font-medium">
                ¿Primer uso? Crear administrador
              </button>
            )
          )}
        </div>
      </div>
    </div>
  )
}
