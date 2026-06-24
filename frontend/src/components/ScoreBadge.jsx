// Bandas centralizadas (escala 1–100): debe coincidir con backend/app/services/scoring.py
export function bandFor(score) {
  if (score >= 90) return { label: 'Excepcional', color: '#059669' }
  if (score >= 70) return { label: 'Bueno', color: '#0D9488' }
  if (score >= 50) return { label: 'Regular', color: '#D97706' }
  return { label: 'Crítico', color: '#DC2626' }
}

export default function ScoreBadge({ score, band, size = 80 }) {
  const radius = (size - 12) / 2
  const circumference = 2 * Math.PI * radius
  const progress = (Math.max(1, Math.min(100, score)) / 100) * circumference
  const offset = circumference - progress

  const { label, color } = bandFor(score)
  const displayLabel = band || label
  const fontSize = size >= 80 ? 18 : 15

  return (
    <div className="flex flex-col items-center gap-1 shrink-0">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#E5E7EB" strokeWidth="6" />
        <circle
          cx={size/2} cy={size/2} r={radius}
          fill="none" stroke={color} strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size/2} ${size/2})`}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="central"
          fontSize={fontSize} fontWeight="700" fontFamily="Inter" fill={color}>
          {Math.round(score)}
        </text>
      </svg>
      <span className="text-xs font-semibold" style={{ color }}>{displayLabel}</span>
    </div>
  )
}
