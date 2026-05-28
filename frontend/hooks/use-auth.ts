'use client'
import { useState, useEffect, useCallback } from 'react'
import { getToken, setToken, clearToken, apiLogin, apiRegister } from '@/lib/auth'

export type AuthState = 'loading' | 'authenticated' | 'unauthenticated'

export function useAuth() {
  const [state, setState] = useState<AuthState>('loading')

  useEffect(() => {
    setState(getToken() ? 'authenticated' : 'unauthenticated')
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const token = await apiLogin(email, password)
    setToken(token)
    setState('authenticated')
  }, [])

  const register = useCallback(async (email: string, password: string) => {
    await apiRegister(email, password)
    // Auto-login after register
    const token = await apiLogin(email, password)
    setToken(token)
    setState('authenticated')
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setState('unauthenticated')
  }, [])

  const onSessionExpired = useCallback(() => {
    clearToken()
    setState('unauthenticated')
  }, [])

  return { state, login, register, logout, onSessionExpired }
}
