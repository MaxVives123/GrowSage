'use client'
import { useState, FormEvent } from 'react'
import { Leaf, Loader2, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface AuthScreenProps {
  onLogin: (email: string, password: string) => Promise<void>
  onRegister: (email: string, password: string) => Promise<void>
}

type Tab = 'login' | 'register'

export function AuthScreen({ onLogin, onRegister }: AuthScreenProps) {
  const [tab, setTab] = useState<Tab>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (tab === 'login') {
        await onLogin(email, password)
      } else {
        await onRegister(email, password)
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-dvh flex items-center justify-center bg-[#f9faf7] px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-[#0a1a0a] flex items-center justify-center mb-3 shadow-lg">
            <Leaf className="w-7 h-7 text-[#4ade80]" />
          </div>
          <h1 className="text-2xl font-bold text-[#0a1a0a]">SproutAI</h1>
          <p className="text-sm text-muted-foreground mt-1">Your AI garden expert</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-border overflow-hidden">

          {/* Tabs */}
          <div className="grid grid-cols-2 border-b border-border">
            {(['login', 'register'] as Tab[]).map(t => (
              <button
                key={t}
                onClick={() => { setTab(t); setError('') }}
                className={`py-3 text-sm font-medium transition-colors ${
                  tab === t
                    ? 'text-[#16a34a] border-b-2 border-[#16a34a] -mb-px'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {t === 'login' ? 'Sign in' : 'Create account'}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                disabled={loading}
                className="rounded-xl"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder={tab === 'register' ? 'Min. 8 characters' : '••••••••'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                disabled={loading}
                className="rounded-xl"
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 text-sm text-red-600 bg-red-50 rounded-xl px-3 py-2">
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#16a34a] hover:bg-[#15803d] text-white"
            >
              {loading
                ? <Loader2 className="w-4 h-4 animate-spin" />
                : tab === 'login' ? 'Sign in' : 'Create account'
              }
            </Button>
          </form>
        </div>

        <p className="text-xs text-center text-muted-foreground mt-6">
          Answers grounded in FAO, INIA & USDA manuals
        </p>
      </div>
    </div>
  )
}
