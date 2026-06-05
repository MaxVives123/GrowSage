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

// ── Auth ─────────────────────────────────────────────────────────────────────

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
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? 'Invalid email or password')
  }
  return (await res.json()).access_token
}

// ── Streaming chat ────────────────────────────────────────────────────────────

export type StreamEvent =
  | { type: 'sources'; sources: { name: string; page: string }[]; conversation_id: string }
  | { type: 'token'; content: string }
  | { type: 'done'; message_id: string }
  | { type: 'error'; detail: string }

export async function* apiChatStream(
  question: string,
  history: { role: 'user' | 'assistant'; content: string }[],
  conversationId?: string | null,
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${API}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({
      question,
      history,
      conversation_id: conversationId ?? null,
    }),
  })

  if (res.status === 401 || res.status === 403) {
    const err = await res.json().catch(() => ({}))
    if (err.detail === 'UNVERIFIED_EMAIL') throw new Error('UNVERIFIED_EMAIL')
    clearToken()
    throw new Error('SESSION_EXPIRED')
  }
  if (res.status === 429) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? 'Daily message limit reached. Try again tomorrow.')
  }
  if (!res.ok || !res.body) {
    throw new Error(`API error ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed.startsWith('data: ')) {
        try {
          yield JSON.parse(trimmed.slice(6)) as StreamEvent
        } catch { /* skip malformed lines */ }
      }
    }
  }
}

// ── Conversations ─────────────────────────────────────────────────────────────

export interface ConversationSummary {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  sources: { name: string; page: string }[]
  created_at: string
}

export async function apiGetConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${API}/conversations`, { headers: authHeaders() })
  if (!res.ok) return []
  return res.json()
}

export async function apiGetConversationMessages(convId: string): Promise<ConversationMessage[]> {
  const res = await fetch(`${API}/conversations/${convId}/messages`, { headers: authHeaders() })
  if (!res.ok) return []
  return res.json()
}

export async function apiDeleteConversation(convId: string): Promise<void> {
  await fetch(`${API}/conversations/${convId}`, { method: 'DELETE', headers: authHeaders() })
}

export async function apiResendVerification(): Promise<void> {
  await fetch(`${API}/auth/resend-verification`, {
    method: 'POST',
    headers: authHeaders(),
  })
}

export function getEmailVerifiedFromToken(): boolean {
  const token = getToken()
  if (!token) return true
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.email_verified ?? true
  } catch {
    return true
  }
}

export async function apiFeedback(messageId: string, rating: 1 | -1): Promise<void> {
  await fetch(`${API}/conversations/messages/${messageId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ rating }),
  })
}
