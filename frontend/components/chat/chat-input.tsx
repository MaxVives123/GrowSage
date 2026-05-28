'use client'

import { useRef, useEffect } from 'react'
import { ArrowUp } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  isLoading: boolean
}

export function ChatInput({ value, onChange, onSend, isLoading }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      const newHeight = Math.min(textarea.scrollHeight, 120) // max 4 rows ~120px
      textarea.style.height = `${newHeight}px`
    }
  }, [value])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  const canSend = value.trim().length > 0 && !isLoading

  return (
    <div className="border-t border-border bg-card px-4 py-3">
      <div className="max-w-[720px] mx-auto">
        <div className="flex items-end gap-2 bg-background rounded-xl border border-input p-2">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your garden..."
            rows={1}
            className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm placeholder:text-muted-foreground focus:outline-none min-h-[36px]"
            disabled={isLoading}
          />
          <Button
            size="icon"
            onClick={onSend}
            disabled={!canSend}
            className="h-9 w-9 rounded-lg bg-primary hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            <ArrowUp className="w-4 h-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-2">
          Answers grounded in FAO, INIA, USDA & Junta de Andalucía manuals
        </p>
      </div>
    </div>
  )
}
