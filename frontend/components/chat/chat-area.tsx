'use client'

import { RefObject } from 'react'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { Message } from '@/app/page'
import { MessageBubble } from './message-bubble'
import { EmptyState } from './empty-state'
import { ChatInput } from './chat-input'
import { TypingIndicator } from './typing-indicator'

interface ChatAreaProps {
  messages: Message[]
  input: string
  isLoading: boolean
  onInputChange: (value: string) => void
  onSend: () => void
  onNewChat: () => void
  onSuggestionClick: (suggestion: string) => void
  messagesEndRef: RefObject<HTMLDivElement | null>
}

export function ChatArea({
  messages,
  input,
  isLoading,
  onInputChange,
  onSend,
  onNewChat,
  onSuggestionClick,
  messagesEndRef
}: ChatAreaProps) {
  const hasMessages = messages.length > 0

  return (
    <div className="flex-1 flex flex-col bg-background min-h-0">
      {/* Top Bar - Desktop only */}
      <header className="hidden lg:flex items-center justify-between px-6 py-3 border-b border-border">
        <span className="text-sm text-muted-foreground">SproutAI</span>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onNewChat}
          className="text-primary border-primary hover:bg-primary/10"
        >
          <Plus className="w-4 h-4 mr-1" />
          New chat
        </Button>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {hasMessages ? (
          <div className="max-w-[720px] mx-auto px-4 py-6 space-y-4">
            {messages.map((message, index) => (
              <MessageBubble 
                key={message.id} 
                message={message} 
                index={index}
              />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        ) : (
          <EmptyState onSuggestionClick={onSuggestionClick} />
        )}
      </div>

      {/* Input Area */}
      <ChatInput
        value={input}
        onChange={onInputChange}
        onSend={onSend}
        isLoading={isLoading}
      />
    </div>
  )
}
