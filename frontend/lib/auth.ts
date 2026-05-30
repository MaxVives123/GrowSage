const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'growsage_token'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function authHeaders(): Record<string, string> {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// ── API calls ────────────────────────────────────────────────────────────────

export async function apiRegister(email: string, password: string) {
  const res = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Error ${res.status}`)
  }
  return res.json()
}

export async function apiLogin(email: string, password: string): Promise<string> {
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error('Invalid email or password')
  const data = await res.json()
  return data.access_token
}

export async function apiChat(question: string): Promise<{ answer: string; sources: { name: string; page: string }[] }> {
  const res = await fetch(`${API}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ question }),
  })
  if (res.status === 401 || res.status === 403) {
    clearToken()
    throw new Error('SESSION_EXPIRED')
  }
  if (res.status === 429) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? 'Daily message limit reached. Try again tomorrow.')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `API error ${res.status}`)
  }
  return res.json()
}
