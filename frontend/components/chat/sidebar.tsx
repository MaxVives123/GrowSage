import { FileText, X, LogOut, MessageSquare, Plus, Trash2, Coffee } from 'lucide-react'
import { SproutIcon } from './sprout-icon'
import type { ConversationSummary } from '@/lib/auth'

const knowledgeSources = [
  { label: 'FAO · Seeds', indexed: true },
  { label: 'INIA · Vegetables', indexed: true },
  { label: 'FAO · Composting', indexed: true },
  { label: 'USDA · Pest Control', indexed: true },
  { label: 'BPA · Tomato Guide', indexed: true },
]

interface SidebarProps {
  onClose?: () => void
  onLogout?: () => void
  onNewChat?: () => void
  conversations?: ConversationSummary[]
  currentConversationId?: string | null
  onSelectConversation?: (id: string) => void
  onDeleteConversation?: (id: string) => void
}

export function Sidebar({
  onClose,
  onLogout,
  onNewChat,
  conversations = [],
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
}: SidebarProps) {
  return (
    <aside className="w-[260px] h-full bg-sidebar flex flex-col">
      {/* Header */}
      <div className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SproutIcon className="w-7 h-7 text-accent" />
            <span className="text-lg font-bold text-sidebar-foreground">GrowSage</span>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1 text-sidebar-foreground/70 hover:text-sidebar-foreground transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        <p className="text-sm text-sidebar-muted mt-1">Your AI garden expert</p>
      </div>

      {/* New chat button */}
      {onNewChat && (
        <div className="px-5 pb-3">
          <button
            onClick={onNewChat}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border border-sidebar-border text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/30 text-sm transition-colors"
          >
            <Plus className="w-4 h-4 shrink-0" />
            New chat
          </button>
        </div>
      )}

      {/* Divider */}
      <div className="mx-5 h-px bg-sidebar-border" />

      {/* Conversation history */}
      {conversations.length > 0 && (
        <div className="flex-1 p-5 overflow-y-auto min-h-0">
          <h3 className="text-xs font-semibold text-sidebar-foreground/60 uppercase tracking-wider mb-3">
            Recent chats
          </h3>
          <div className="space-y-1">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group flex items-center gap-2 px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${
                  conv.id === currentConversationId
                    ? 'bg-sidebar-accent/50 text-sidebar-foreground'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/30 hover:text-sidebar-foreground'
                }`}
                onClick={() => onSelectConversation?.(conv.id)}
              >
                <MessageSquare className="w-3.5 h-3.5 shrink-0 text-sidebar-foreground/40" />
                <span className="flex-1 truncate text-xs">{conv.title}</span>
                {onDeleteConversation && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onDeleteConversation(conv.id) }}
                    className="opacity-0 group-hover:opacity-100 p-0.5 text-sidebar-foreground/40 hover:text-red-400 transition-all"
                    aria-label="Delete conversation"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Knowledge Base — shown when no conversations yet */}
      {conversations.length === 0 && (
        <div className="flex-1 p-5 overflow-y-auto">
          <h3 className="text-xs font-semibold text-sidebar-foreground/60 uppercase tracking-wider mb-3">
            Knowledge base
          </h3>
          <div className="space-y-2">
            {knowledgeSources.map((source, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-sidebar-accent/30 text-sidebar-foreground text-sm"
              >
                <FileText className="w-4 h-4 text-sidebar-foreground/60 shrink-0" />
                <span className="flex-1 truncate">{source.label}</span>
                {source.indexed && (
                  <span className="w-2 h-2 rounded-full bg-accent animate-pulse-dot" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-5 border-t border-sidebar-border space-y-3">
        <div className="text-xs text-sidebar-foreground/50 space-y-1">
          <p>2,288 chunks indexed · 13 documents</p>
        </div>

        {/* Support link */}
        <a
          href="https://buymeacoffee.com/growsage"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-xs text-sidebar-foreground/50 hover:text-sidebar-foreground/80 transition-colors"
        >
          <Coffee className="w-3.5 h-3.5" />
          Support GrowSage ☕
        </a>

        {onLogout && (
          <button
            onClick={onLogout}
            className="flex items-center gap-2 text-xs text-sidebar-foreground/50 hover:text-sidebar-foreground/80 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign out
          </button>
        )}
      </div>
    </aside>
  )
}
