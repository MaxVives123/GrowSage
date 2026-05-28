export function TypingIndicator() {
  return (
    <div className="flex justify-start animate-message-in">
      <div className="bg-card rounded-2xl shadow-sm border-l-[3px] border-l-accent px-4 py-4">
        <div className="flex items-center gap-1">
          <span 
            className="w-2 h-2 rounded-full bg-primary animate-bounce-dot"
            style={{ animationDelay: '0ms' }}
          />
          <span 
            className="w-2 h-2 rounded-full bg-primary animate-bounce-dot"
            style={{ animationDelay: '150ms' }}
          />
          <span 
            className="w-2 h-2 rounded-full bg-primary animate-bounce-dot"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  )
}
