'use client'

import { useState } from 'react'
import { ChevronDown, FileText, ThumbsUp, ThumbsDown } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message } from '@/app/page'

interface MessageBubbleProps {
  message: Message
  index: number
  onFeedback?: (messageId: string, rating: 1 | -1) => void
}

export function MessageBubble({ message, index, onFeedback }: MessageBubbleProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const [feedback, setFeedback] = useState<1 | -1 | null>(null)
  const isUser = message.role === 'user'

  const handleFeedback = (rating: 1 | -1) => {
    if (feedback !== null || !message.messageId) return
    setFeedback(rating)
    onFeedback?.(message.messageId, rating)
  }

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-message-in`}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {isUser ? (
        <div className="max-w-[85%] md:max-w-[70%] px-4 py-3 rounded-2xl bg-[#1a3a1a] text-white">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      ) : (
        <div className="max-w-[85%] md:max-w-[70%] bg-card rounded-2xl shadow-sm border-l-[3px] border-l-accent overflow-hidden">
          <div className="px-4 py-3">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              className="prose prose-sm max-w-none text-card-foreground"
              components={{
                p: ({ children }) => (
                  <p className="text-sm leading-relaxed mb-2 last:mb-0">{children}</p>
                ),
                ul: ({ children }) => (
                  <ul className="text-sm leading-relaxed ml-4 list-disc mb-2 space-y-1">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="text-sm leading-relaxed ml-4 list-decimal mb-2 space-y-1">{children}</ol>
                ),
                li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                h1: ({ children }) => (
                  <h1 className="text-base font-bold mt-3 mb-1 first:mt-0">{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-sm font-bold mt-3 mb-1 first:mt-0">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm font-semibold mt-2 mb-1 first:mt-0">{children}</h3>
                ),
                code: ({ children }) => (
                  <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono">{children}</code>
                ),
              }}
            >
              {message.content || (message.isStreaming ? '▋' : '')}
            </ReactMarkdown>
          </div>

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="border-t border-border">
              <button
                onClick={() => setSourcesOpen(!sourcesOpen)}
                className="w-full flex items-center gap-2 px-4 py-2 text-xs text-muted-foreground hover:bg-muted/50 transition-colors"
              >
                <ChevronDown className={`w-3 h-3 transition-transform ${sourcesOpen ? 'rotate-180' : ''}`} />
                <span>Sources ({message.sources.length})</span>
              </button>
              {sourcesOpen && (
                <div className="px-4 pb-3 flex flex-wrap gap-2">
                  {message.sources.map((source, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-secondary text-xs text-secondary-foreground"
                    >
                      <FileText className="w-3 h-3" />
                      {source.name} · {source.page}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Feedback */}
          {message.messageId && !message.isStreaming && (
            <div className="flex items-center gap-1 px-4 pb-2 pt-0.5">
              <span className="text-xs text-muted-foreground mr-1">Helpful?</span>
              <button
                onClick={() => handleFeedback(1)}
                disabled={feedback !== null}
                className={`p-1 rounded transition-colors ${
                  feedback === 1
                    ? 'text-green-600'
                    : 'text-muted-foreground hover:text-green-600 disabled:opacity-40'
                }`}
                aria-label="Helpful"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(-1)}
                disabled={feedback !== null}
                className={`p-1 rounded transition-colors ${
                  feedback === -1
                    ? 'text-red-500'
                    : 'text-muted-foreground hover:text-red-500 disabled:opacity-40'
                }`}
                aria-label="Not helpful"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
