import { FileText, X, LogOut, MessageSquare, Plus, Trash2, Coffee } from 'lucide-react'
import { SproutIcon } from './sprout-icon'
import type { ConversationSummary } from '@/lib/auth'

const knowledgeSources = [
  { label: 'FAO · Seed Production',   license: 'Open access' },
  { label: 'FAO · Composting',        license: 'Open access' },
  { label: 'INIA · Vegetables',       license: 'Open access' },
  { label: 'USDA · Pest Management',  license: 'Public domain' },
  { label: 'Junta Andalucía · Compost', license: 'Open access' },
  { label: 'Univ. Missouri · Garden', license: 'Open access' },
  { label: 'Utah State · Vegetables', license: 'Open access' },
  { label: 'BPA · Tomato Guide',      license: 'Open access' },
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
          <div className="space-y-1.5">
            {knowledgeSources.map((source, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-sidebar-accent/30 text-sidebar-foreground text-sm"
              >
                <FileText className="w-4 h-4 text-sidebar-foreground/60 shrink-0" />
                <span className="flex-1 truncate text-xs">{source.label}</span>
                <span className="text-[10px] text-sidebar-foreground/40 shrink-0">{source.license}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-5 border-t border-sidebar-border space-y-3">
        <div className="text-[10px] text-sidebar-foreground/40 space-y-1 leading-relaxed">
          <p className="font-medium text-sidebar-foreground/50">Free &amp; non-profit</p>
          <p>Based on publicly available agricultural publications from FAO, USDA, INIA, Junta de Andalucía, University of Missouri and others.</p>
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
