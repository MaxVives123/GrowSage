import { FileText, X, LogOut } from 'lucide-react'
import { SproutIcon } from './sprout-icon'

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
}

export function Sidebar({ onClose, onLogout }: SidebarProps) {
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

      {/* Divider */}
      <div className="mx-5 h-px bg-sidebar-border" />

      {/* Knowledge Base Section */}
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

      {/* Stats + Logout */}
      <div className="p-5 border-t border-sidebar-border space-y-3">
        <div className="text-xs text-sidebar-foreground/50 space-y-1">
          <p>2,288 chunks indexed</p>
          <p>13 documents</p>
        </div>
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
