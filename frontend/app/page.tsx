'use client'

import { useState, useRef, useEffect } from 'react'
import { Sidebar } from '@/components/chat/sidebar'
import { ChatArea } from '@/components/chat/chat-area'
import { MobileHeader } from '@/components/chat/mobile-header'
import { AuthScreen } from '@/components/auth/auth-screen'
import { useAuth } from '@/hooks/use-auth'
import { getDemoResponse } from '@/lib/demo-responses'
import { apiChat } from '@/lib/auth'
import { Leaf } from 'lucide-react'

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: { name: string; page: string }[]
}

export default function ChatPage() {
  const { state, login, register, logout, onSessionExpired } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    if (DEMO_MODE) {
      await new Promise(r => setTimeout(r, 1200))
      const demo = getDemoResponse(userMessage.content)
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: demo.answer,
        sources: demo.sources,
      }])
      setIsLoading(false)
      return
    }

    try {
      const data = await apiChat(userMessage.content)
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }])
    } catch (err: unknown) {
      if (err instanceof Error && err.message === 'SESSION_EXPIRED') {
        onSessionExpired()
        return
      }
      const message = err instanceof Error && err.message !== `API error 503`
        ? err.message
        : 'Could not reach the knowledge base. Make sure the API server is running on port 8000.'
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: message,
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setInput('')
  }

  // ── Loading splash ────────────────────────────────────────────────────────
  if (state === 'loading') {
    return (
      <div className="min-h-dvh flex items-center justify-center bg-[#f9faf7]">
        <Leaf className="w-8 h-8 text-[#4ade80] animate-pulse" />
      </div>
    )
  }

  // ── Auth gate ─────────────────────────────────────────────────────────────
  if (state === 'unauthenticated') {
    return <AuthScreen onLogin={login} onRegister={register} />
  }

  // ── Main chat UI ──────────────────────────────────────────────────────────
  return (
    <div className="flex h-dvh overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar onLogout={logout} />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        >
          <div
            className="w-[280px] h-full"
            onClick={e => e.stopPropagation()}
          >
            <Sidebar onClose={() => setIsSidebarOpen(false)} onLogout={logout} />
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <MobileHeader
          onMenuClick={() => setIsSidebarOpen(true)}
          onNewChat={handleNewChat}
        />
        <ChatArea
          messages={messages}
          input={input}
          isLoading={isLoading}
          onInputChange={setInput}
          onSend={handleSend}
          onNewChat={handleNewChat}
          onSuggestionClick={setInput}
          messagesEndRef={messagesEndRef}
        />
      </div>
    </div>
  )
}
