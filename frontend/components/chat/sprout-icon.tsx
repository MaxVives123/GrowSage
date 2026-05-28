interface SproutIconProps {
  className?: string
}

export function SproutIcon({ className }: SproutIconProps) {
  return (
    <svg 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Soil/ground */}
      <ellipse cx="12" cy="20" rx="6" ry="2" fill="currentColor" opacity="0.3" />
      
      {/* Stem */}
      <path 
        d="M12 20V12" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round"
      />
      
      {/* Left leaf */}
      <path 
        d="M12 14C12 14 8 12 6 8C6 8 10 8 12 12" 
        fill="currentColor" 
        opacity="0.8"
      />
      
      {/* Right leaf */}
      <path 
        d="M12 10C12 10 16 8 18 4C18 4 14 4 12 8" 
        fill="currentColor"
      />
    </svg>
  )
}

export function SproutIllustration({ className }: SproutIconProps) {
  return (
    <svg 
      viewBox="0 0 120 120" 
      fill="none" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background circle */}
      <circle cx="60" cy="60" r="55" fill="#f0fdf4" />
      
      {/* Soil/pot */}
      <ellipse cx="60" cy="95" rx="25" ry="8" fill="#8B7355" opacity="0.6" />
      <ellipse cx="60" cy="93" rx="22" ry="6" fill="#A0826D" opacity="0.8" />
      
      {/* Main stem */}
      <path 
        d="M60 93V55" 
        stroke="#16a34a" 
        strokeWidth="4" 
        strokeLinecap="round"
      />
      
      {/* Left large leaf */}
      <path 
        d="M60 65C60 65 45 58 35 40C35 40 50 42 60 60" 
        fill="#4ade80"
      />
      <path 
        d="M60 65C60 65 48 55 42 45" 
        stroke="#16a34a" 
        strokeWidth="1.5" 
        strokeLinecap="round"
        opacity="0.5"
      />
      
      {/* Right large leaf */}
      <path 
        d="M60 55C60 55 75 48 85 30C85 30 70 32 60 50" 
        fill="#22c55e"
      />
      <path 
        d="M60 55C60 55 72 45 78 35" 
        stroke="#16a34a" 
        strokeWidth="1.5" 
        strokeLinecap="round"
        opacity="0.5"
      />
      
      {/* Small left leaf */}
      <path 
        d="M60 75C60 75 50 72 45 62C45 62 55 64 60 72" 
        fill="#86efac"
      />
      
      {/* Small right leaf */}
      <path 
        d="M60 70C60 70 68 66 73 58C73 58 65 60 60 68" 
        fill="#86efac"
      />
      
      {/* Decorative dots */}
      <circle cx="30" cy="75" r="3" fill="#bbf7d0" />
      <circle cx="90" cy="70" r="2" fill="#bbf7d0" />
      <circle cx="25" cy="55" r="2" fill="#dcfce7" />
      <circle cx="95" cy="50" r="3" fill="#dcfce7" />
    </svg>
  )
}
