import { SproutIllustration } from './sprout-icon'

const suggestions = [
  'When to transplant tomatoes?',
  'How to make compost at home?',
  'What pests attack peppers?'
]

interface EmptyStateProps {
  onSuggestionClick: (suggestion: string) => void
}

export function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
      <SproutIllustration className="w-32 h-32 md:w-40 md:h-40 mb-6" />
      
      <h2 className="text-xl md:text-2xl font-semibold text-foreground text-center text-balance mb-6">
        What do you want to grow today?
      </h2>

      <div className="flex flex-wrap justify-center gap-2 max-w-lg">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSuggestionClick(suggestion)}
            className="px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm hover:bg-secondary/80 transition-colors border border-border"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
