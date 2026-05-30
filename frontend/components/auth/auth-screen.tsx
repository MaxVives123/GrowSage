'use client'
import { useState, FormEvent } from 'react'
import { Leaf, Loader2, AlertCircle, Eye, EyeOff, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface AuthScreenProps {
  onLogin: (email: string, password: string) => Promise<void>
  onRegister: (email: string, password: string) => Promise<void>
}

type Tab = 'login' | 'register'

function PasswordInput({
  id,
  value,
  onChange,
  placeholder,
  disabled,
  autoComplete,
}: {
  id: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
  disabled: boolean
  autoComplete?: string
}) {
  const [show, setShow] = useState(false)
  return (
    <div className="relative">
      <Input
        id={id}
        type={show ? 'text' : 'password'}
        placeholder={placeholder ?? '••••••••'}
        value={value}
        onChange={e => onChange(e.target.value)}
        required
        disabled={disabled}
        autoComplete={autoComplete}
        className="rounded-xl pr-10"
      />
      <button
        type="button"
        tabIndex={-1}
        onClick={() => setShow(s => !s)}
        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
        aria-label={show ? 'Hide password' : 'Show password'}
      >
        {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
      </button>
    </div>
  )
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function AuthScreen({ onLogin, onRegister }: AuthScreenProps) {
  const [tab, setTab] = useState<Tab>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const switchTab = (t: Tab) => {
    setTab(t)
    setError('')
    setSuccess(false)
    setConfirmPassword('')
  }

  const validate = (): string | null => {
    if (!EMAIL_RE.test(email.trim())) return 'Enter a valid email address'
    if (password.length < 8) return 'Password must be at least 8 characters'
    if (tab === 'register' && password !== confirmPassword) return 'Passwords do not match'
    return null
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    const err = validate()
    if (err) { setError(err); return }

    setLoading(true)
    try {
      if (tab === 'login') {
        await onLogin(email.trim(), password)
      } else {
        setSuccess(true)
        await onRegister(email.trim(), password)
      }
    } catch (err: unknown) {
      setSuccess(false)
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const passwordOk = password.length >= 8
  const passwordsMatch = password === confirmPassword

  return (
    <div className="min-h-dvh flex items-center justify-center bg-[#f9faf7] px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-[#0a1a0a] flex items-center justify-center mb-3 shadow-lg">
            <Leaf className="w-7 h-7 text-[#4ade80]" />
          </div>
          <h1 className="text-2xl font-bold text-[#0a1a0a]">GrowSage</h1>
          <p className="text-sm text-muted-foreground mt-1">Your AI garden expert</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-border overflow-hidden">

          {/* Tabs */}
          <div className="grid grid-cols-2 border-b border-border">
            {(['login', 'register'] as Tab[]).map(t => (
              <button
                key={t}
                type="button"
                onClick={() => switchTab(t)}
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

            {/* Success banner */}
            {success && (
              <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 rounded-xl px-3 py-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Account created! Signing you in…</span>
              </div>
            )}

            {/* Email */}
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
                autoComplete="email"
                className="rounded-xl"
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <PasswordInput
                id="password"
                value={password}
                onChange={setPassword}
                placeholder={tab === 'register' ? 'Min. 8 characters' : '••••••••'}
                disabled={loading}
                autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
              />
              {tab === 'register' && password.length > 0 && (
                <p className={`text-xs ${passwordOk ? 'text-green-600' : 'text-amber-600'}`}>
                  {passwordOk
                    ? '✓ Looks good'
                    : `${8 - password.length} more character${8 - password.length === 1 ? '' : 's'} needed`}
                </p>
              )}
            </div>

            {/* Confirm password — register only */}
            {tab === 'register' && (
              <div className="space-y-1.5">
                <Label htmlFor="confirmPassword">Confirm password</Label>
                <PasswordInput
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  placeholder="Repeat your password"
                  disabled={loading}
                  autoComplete="new-password"
                />
                {confirmPassword.length > 0 && (
                  <p className={`text-xs ${passwordsMatch ? 'text-green-600' : 'text-amber-600'}`}>
                    {passwordsMatch ? '✓ Passwords match' : 'Passwords do not match'}
                  </p>
                )}
              </div>
            )}

            {/* Error */}
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
                : tab === 'login' ? 'Sign in' : 'Create account'}
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
