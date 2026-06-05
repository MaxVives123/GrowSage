'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Sidebar } from '@/components/chat/sidebar'
import { ChatArea } from '@/components/chat/chat-area'
import { MobileHeader } from '@/components/chat/mobile-header'
import { AuthScreen } from '@/components/auth/auth-screen'
import { useAuth } from '@/hooks/use-auth'
import { getDemoResponse } from '@/lib/demo-responses'
import {
  apiChatStream,
  apiGetConversations,
  apiGetConversationMessages,
  apiDeleteConversation,
  apiFeedback,
  apiResendVerification,
  getEmailVerifiedFromToken,
  type ConversationSummary,
} from '@/lib/auth'
import { Leaf, MailCheck, AlertCircle, CheckCircle2 } from 'lucide-react'

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: { name: string; page: string }[]
  isStreaming?: boolean
  messageId?: string  // DB ID used for feedback
}

export default function ChatPage() {
  const { state, login, register, logout, onSessionExpired } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [emailVerified, setEmailVerified] = useState(true)
  const [verifiedParam, setVerifiedParam] = useState<string | null>(null)
  const [resendSent, setResendSent] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Check email_verified from JWT and handle ?verified= redirect param
  useEffect(() => {
    setEmailVerified(getEmailVerifiedFromToken())
    const params = new URLSearchParams(window.location.search)
    const v = params.get('verified')
    if (v) {
      setVerifiedParam(v)
      if (v === 'success') setEmailVerified(true)
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [state])

  const loadConversations = useCallback(async () => {
    if (state !== 'authenticated') return
    const convs = await apiGetConversations()
    setConversations(convs)
  }, [state])

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const handleSelectConversation = async (convId: string) => {
    setIsSidebarOpen(false)
    const msgs = await apiGetConversationMessages(convId)
    setMessages(
      msgs.map((m) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        sources: m.sources,
        messageId: m.id,
      }))
    )
    setCurrentConversationId(convId)
  }

  const handleDeleteConversation = async (convId: string) => {
    await apiDeleteConversation(convId)
    if (currentConversationId === convId) handleNewChat()
    setConversations((prev) => prev.filter((c) => c.id !== convId))
  }

  const handleNewChat = () => {
    setMessages([])
    setInput('')
    setCurrentConversationId(null)
  }

  const handleFeedback = async (messageId: string, rating: 1 | -1) => {
    await apiFeedback(messageId, rating)
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // ── Demo mode (no API needed) ───────────────────────────────────────────
    if (DEMO_MODE) {
      await new Promise((r) => setTimeout(r, 1200))
      const demo = getDemoResponse(userMessage.content)
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: demo.answer,
          sources: demo.sources,
        },
      ])
      setIsLoading(false)
      return
    }

    // ── Streaming mode ──────────────────────────────────────────────────────
    const assistantId = (Date.now() + 1).toString()
    const history = messages.map((m) => ({ role: m.role, content: m.content }))

    try {
      for await (const event of apiChatStream(
        userMessage.content,
        history,
        currentConversationId
      )) {
        if (event.type === 'sources') {
          setCurrentConversationId(event.conversation_id)
          // Add assistant placeholder once sources arrive
          setMessages((prev) => [
            ...prev,
            {
              id: assistantId,
              role: 'assistant',
              content: '',
              sources: event.sources,
              isStreaming: true,
            },
          ])
          // Refresh sidebar conversation list
          loadConversations()
        } else if (event.type === 'token') {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + event.content } : m
            )
          )
        } else if (event.type === 'done') {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, isStreaming: false, messageId: event.message_id }
                : m
            )
          )
        } else if (event.type === 'error') {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: event.detail, isStreaming: false }
                : m
            )
          )
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.message === 'SESSION_EXPIRED') {
        onSessionExpired()
        return
      }
      if (err instanceof Error && err.message === 'UNVERIFIED_EMAIL') {
        setEmailVerified(false)
        setMessages(prev => prev.filter(m => m.id !== assistantId))
        return
      }
      const errMsg =
        err instanceof Error
          ? err.message
          : 'Could not reach the knowledge base. Make sure the API server is running.'
      // If placeholder was never added (error before sources event), append now
      setMessages((prev) => {
        const hasPlaceholder = prev.some((m) => m.id === assistantId)
        const errorMsg: Message = { id: assistantId, role: 'assistant', content: errMsg }
        return hasPlaceholder
          ? prev.map((m) =>
              m.id === assistantId ? { ...m, content: errMsg, isStreaming: false } : m
            )
          : [...prev, errorMsg]
      })
    } finally {
      setIsLoading(false)
      // Ensure isStreaming is cleared even if generator exited early
      setMessages((prev) =>
        prev.map((m) => (m.id === assistantId ? { ...m, isStreaming: false } : m))
      )
    }
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
        <Sidebar
          onLogout={logout}
          onNewChat={handleNewChat}
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        >
          <div className="w-[280px] h-full" onClick={(e) => e.stopPropagation()}>
            <Sidebar
              onClose={() => setIsSidebarOpen(false)}
              onLogout={logout}
              onNewChat={handleNewChat}
              conversations={conversations}
              currentConversationId={currentConversationId}
              onSelectConversation={handleSelectConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Email verification success banner */}
        {verifiedParam === 'success' && (
          <div className="flex items-center gap-2 px-4 py-2.5 bg-green-50 border-b border-green-200 text-green-800 text-sm">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Email verified! You can now start chatting.</span>
          </div>
        )}

        {/* Email verification error banner */}
        {verifiedParam === 'error' && (
          <div className="flex items-center gap-2 px-4 py-2.5 bg-red-50 border-b border-red-200 text-red-800 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>Verification link is invalid or expired. Please request a new one below.</span>
          </div>
        )}

        {/* Unverified email banner */}
        {!emailVerified && (
          <div className="flex items-center justify-between gap-3 px-4 py-2.5 bg-amber-50 border-b border-amber-200 text-amber-800 text-sm">
            <div className="flex items-center gap-2">
              <MailCheck className="w-4 h-4 shrink-0" />
              <span>Please verify your email to start chatting. Check your inbox.</span>
            </div>
            <button
              onClick={async () => {
                await apiResendVerification()
                setResendSent(true)
              }}
              disabled={resendSent}
              className="shrink-0 text-xs font-medium underline disabled:opacity-50"
            >
              {resendSent ? 'Sent!' : 'Resend email'}
            </button>
          </div>
        )}

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
          onFeedback={handleFeedback}
          messagesEndRef={messagesEndRef}
        />
      </div>
    </div>
  )
}
