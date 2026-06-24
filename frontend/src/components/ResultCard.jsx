import { useState } from 'react'
import ScoreBadge from './ScoreBadge'

export default function ResultCard({ result }) {
  const [expanded, setExpanded] = useState(false)
  const [activeTab, setActiveTab] = useState('feedback')

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center gap-4 p-5 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <ScoreBadge score={result.score} band={result.band} size={72} />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-sm font-semibold text-violet-600 bg-violet-50
              px-2 py-0.5 rounded-md border border-violet-200">
              {result.hu_id}
            </span>
            {result.evaluated === false ? (
              <span className="text-xs font-semibold text-red-600 bg-red-50 px-2 py-0.5 rounded-md border border-red-200">
                No evaluada
              </span>
            ) : (
              <span className="text-xs text-gray-400">
                {result.feedback.length} observaciones · {result.suggestions.length} sugerencias
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 leading-relaxed line-clamp-2">
            {result.original_text || <span className="italic text-gray-400">Texto no disponible (no se almacena el documento).</span>}
          </p>
        </div>

        <svg
          className={`w-5 h-5 text-gray-400 transition-transform duration-200 shrink-0
            ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Expandido */}
      {expanded && (
        <div className="border-t border-gray-100">
          {/* Texto original completo */}
          <div className="px-5 pt-4 pb-3">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
              Texto original
            </p>
            <p className="text-sm text-gray-700 leading-relaxed bg-gray-50
              rounded-xl p-3 border border-gray-200 font-mono">
              {result.original_text}
            </p>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-100 px-5">
            {['feedback', 'suggestions'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2.5 px-4 text-sm font-medium border-b-2 transition-colors
                  ${activeTab === tab
                    ? 'border-violet-600 text-violet-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
              >
                {tab === 'feedback' ? `Observaciones (${result.feedback.length})` : `Sugerencias (${result.suggestions.length})`}
              </button>
            ))}
          </div>

          {/* Contenido del tab */}
          <div className="p-5">
            {activeTab === 'feedback' ? (
              result.feedback.length > 0 ? (
                <ul className="flex flex-col gap-2.5">
                  {result.feedback.map((item, i) => (
                    <li key={i} className="flex gap-3 items-start">
                      <span className="mt-0.5 w-5 h-5 rounded-full bg-amber-100 border border-amber-200
                        flex items-center justify-center shrink-0">
                        <svg className="w-3 h-3 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </span>
                      <p className="text-sm text-gray-700 leading-relaxed">{item}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">Sin observaciones — ¡HU bien redactada!</p>
              )
            ) : (
              result.suggestions.length > 0 ? (
                <ul className="flex flex-col gap-2.5">
                  {result.suggestions.map((item, i) => (
                    <li key={i} className="flex gap-3 items-start">
                      <span className="mt-0.5 w-5 h-5 rounded-full bg-emerald-100 border border-emerald-200
                        flex items-center justify-center shrink-0">
                        <svg className="w-3 h-3 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </span>
                      <p className="text-sm text-gray-700 leading-relaxed">{item}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">Sin sugerencias adicionales.</p>
              )
            )}
          </div>
        </div>
      )}
    </div>
  )
}
