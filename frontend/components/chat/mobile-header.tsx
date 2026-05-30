import { Menu, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { SproutIcon } from './sprout-icon'

interface MobileHeaderProps {
  onMenuClick: () => void
  onNewChat: () => void
}

export function MobileHeader({ onMenuClick, onNewChat }: MobileHeaderProps) {
  return (
    <header className="flex lg:hidden items-center justify-between px-4 py-3 border-b border-border bg-card">
      <button 
        onClick={onMenuClick}
        className="p-2 -ml-2 text-foreground hover:bg-muted rounded-lg transition-colors"
      >
        <Menu className="w-5 h-5" />
        <span className="sr-only">Open menu</span>
      </button>

      <div className="flex items-center gap-2">
        <SproutIcon className="w-5 h-5 text-primary" />
        <span className="font-semibold text-foreground">GrowSage</span>
      </div>

      <Button 
        variant="ghost" 
        size="icon"
        onClick={onNewChat}
        className="text-primary hover:bg-primary/10"
      >
        <Plus className="w-5 h-5" />
        <span className="sr-only">New chat</span>
      </Button>
    </header>
  )
}
