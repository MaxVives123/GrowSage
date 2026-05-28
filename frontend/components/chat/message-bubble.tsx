'use client'

import { useState } from 'react'
import { ChevronDown, FileText } from 'lucide-react'
import type { Message } from '@/app/page'

interface MessageBubbleProps {
  message: Message
  index: number
}

export function MessageBubble({ message, index }: MessageBubbleProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const isUser = message.role === 'user'

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
            <div className="prose prose-sm max-w-none text-card-foreground">
              {message.content.split('\n').map((paragraph, i) => {
                if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
                  return (
                    <h4 key={i} className="font-semibold text-sm mt-3 mb-1 first:mt-0">
                      {paragraph.replace(/\*\*/g, '')}
                    </h4>
                  )
                }
                if (paragraph.startsWith('- ')) {
                  return (
                    <li key={i} className="text-sm leading-relaxed ml-4 list-disc">
                      {paragraph.slice(2)}
                    </li>
                  )
                }
                if (paragraph.trim() === '') return null
                return (
                  <p key={i} className="text-sm leading-relaxed mb-2 last:mb-0">
                    {paragraph}
                  </p>
                )
              })}
            </div>
          </div>

          {/* Sources disclosure */}
          {message.sources && message.sources.length > 0 && (
            <div className="border-t border-border">
              <button
                onClick={() => setSourcesOpen(!sourcesOpen)}
                className="w-full flex items-center gap-2 px-4 py-2 text-xs text-muted-foreground hover:bg-muted/50 transition-colors"
              >
                <ChevronDown 
                  className={`w-3 h-3 transition-transform ${sourcesOpen ? 'rotate-180' : ''}`} 
                />
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
        </div>
      )}
    </div>
  )
}
