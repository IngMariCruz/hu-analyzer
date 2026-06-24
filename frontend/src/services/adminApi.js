// Cliente del panel de administrador. El JWT vive en localStorage (sesión del
// navegador) y se envía como Authorization: Bearer en las rutas protegidas.

const API_BASE = '/api/v1/admin'
const TOKEN_KEY = 'hu_admin_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

async function parseError(response, fallback) {
  try {
    const data = await response.json()
    return data.detail || fallback
  } catch {
    return fallback
  }
}

/** ¿Ya hay un administrador registrado? (decide Registro vs Login) */
export async function adminExists() {
  const res = await fetch(`${API_BASE}/exists`)
  if (!res.ok) throw new Error('No se pudo consultar el estado del administrador.')
  return (await res.json()).registered
}

/** Registro de primer uso → guarda el token y lo devuelve. */
export async function adminRegister(username, password) {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error(await parseError(res, 'No se pudo registrar el administrador.'))
  const { access_token } = await res.json()
  setToken(access_token)
  return access_token
}

/** Login → guarda el token y lo devuelve. */
export async function adminLogin(username, password) {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) throw new Error(await parseError(res, 'Credenciales inválidas.'))
  const { access_token } = await res.json()
  setToken(access_token)
  return access_token
}

// Fetch autenticado: agrega Bearer y lanza un error especial 'UNAUTHORIZED' si el token caducó.
async function authFetch(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
  if (res.status === 401) {
    clearToken()
    throw new Error('UNAUTHORIZED')
  }
  if (!res.ok) throw new Error(await parseError(res, 'Error al consultar el panel.'))
  return res.json()
}

export const getMetrics = () => authFetch('/metrics')
export const getBands = () => authFetch('/metrics/bands')
export const getAnalyses = () => authFetch('/analyses')
