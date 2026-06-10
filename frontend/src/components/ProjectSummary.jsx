import ScoreBadge from './ScoreBadge'

function Section({ title, icon, children }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">{icon}</span>
        <h3 className="font-semibold text-gray-800">{title}</h3>
      </div>
      {children}
    </div>
  )
}

export default function ProjectSummary({ summary, overallScore }) {
  return (
    <div className="card p-6">
      {/* Encabezado con score global */}
      <div className="flex items-center justify-between mb-6 pb-5 border-b border-gray-100">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Resumen del proyecto</h2>
          <p className="text-sm text-gray-500 mt-0.5">Extraído del conjunto de Historias de Usuario</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <ScoreBadge score={overallScore} size={88} />
          <span className="text-xs text-gray-400">Calificación general</span>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        {/* Objetivo */}
        <Section title="Objetivo del proyecto" icon="🎯">
          <p className="text-sm text-gray-700 leading-relaxed bg-violet-50
            border border-violet-100 rounded-xl p-4">
            {summary.objective}
          </p>
        </Section>

        {/* Stakeholders */}
        <Section title="Stakeholders identificados" icon="👥">
          {summary.stakeholders.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {summary.stakeholders.map((s, i) => (
                <span key={i} className="text-sm bg-white border border-violet-200
                  text-violet-700 px-3 py-1 rounded-full font-medium">
                  {s}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">No se identificaron stakeholders.</p>
          )}
        </Section>

        {/* Reglas de negocio */}
        <Section title="Reglas de negocio" icon="📋">
          {summary.business_rules.length > 0 ? (
            <ul className="flex flex-col gap-2">
              {summary.business_rules.map((rule, i) => (
                <li key={i} className="flex gap-3 items-start">
                  <span className="mt-1 shrink-0 w-4 h-4 rounded bg-violet-100
                    text-violet-600 flex items-center justify-center">
                    <svg className="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 8 8">
                      <circle cx="4" cy="4" r="3" />
                    </svg>
                  </span>
                  <p className="text-sm text-gray-700 leading-relaxed">{rule}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-400">No se detectaron reglas de negocio explícitas.</p>
          )}
        </Section>
      </div>
    </div>
  )
}
