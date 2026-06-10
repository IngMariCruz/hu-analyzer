export default function ScoreBadge({ score, size = 80 }) {
  const radius = (size - 12) / 2
  const circumference = 2 * Math.PI * radius
  const progress = ((score - 1) / 9) * circumference
  const offset = circumference - progress

  const getColor = (s) => {
    if (s >= 8) return { stroke: '#059669', label: 'Buena', labelColor: '#059669' }
    if (s >= 6) return { stroke: '#D97706', label: 'Regular', labelColor: '#D97706' }
    return { stroke: '#DC2626', label: 'Deficiente', labelColor: '#DC2626' }
  }

  const { stroke, label, labelColor } = getColor(score)

  return (
    <div className="flex flex-col items-center gap-1 shrink-0">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#E5E7EB" strokeWidth="6" />
        <circle
          cx={size/2} cy={size/2} r={radius}
          fill="none" stroke={stroke} strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size/2} ${size/2})`}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="central"
          fontSize="15" fontWeight="700" fontFamily="Inter" fill={stroke}>
          {score.toFixed(1)}
        </text>
      </svg>
      <span className="text-xs font-semibold" style={{ color: labelColor }}>{label}</span>
    </div>
  )
}
