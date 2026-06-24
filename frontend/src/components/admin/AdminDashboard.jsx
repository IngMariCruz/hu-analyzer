import { useEffect, useState } from 'react'
import { getAnalyses, getBands, getMetrics } from '../../services/adminApi'

const BAND_COLOR = {
  Excepcional: { bar: 'bg-emerald-500', text: 'text-emerald-700', chip: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
  Bueno: { bar: 'bg-teal-500', text: 'text-teal-700', chip: 'bg-teal-50 border-teal-200 text-teal-700' },
  Regular: { bar: 'bg-amber-500', text: 'text-amber-700', chip: 'bg-amber-50 border-amber-200 text-amber-700' },
  Crítico: { bar: 'bg-red-500', text: 'text-red-700', chip: 'bg-red-50 border-red-200 text-red-700' },
}

const STATUS_LABEL = {
  ok: 'Completo', partial: 'Parcial', no_project: 'Sin proyecto', invalid: 'Inválido', error: 'Error',
}

// Suma total de una serie [{period, count}].
const seriesTotal = (s) => (s || []).reduce((acc, x) => acc + x.count, 0)
// Conteo del bucket más reciente (último de la serie ordenada ascendente).
const latest = (s) => (s && s.length ? s[s.length - 1].count : 0)

function StatCard({ label, value, hint }) {
  return (
    <div className="card p-4">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      {hint && <p className="text-xs text-gray-400 mt-0.5">{hint}</p>}
    </div>
  )
}

export default function AdminDashboard({ onUnauthorized }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getMetrics(), getBands(), getAnalyses()])
      .then(([metrics, bands, analyses]) => setData({ metrics, bands, analyses }))
      .catch((err) => {
        if (err.message === 'UNAUTHORIZED') onUnauthorized()
        else setError(err.message)
      })
  }, [onUnauthorized])

  if (error) {
    return <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">{error}</p>
  }
  if (!data) {
    return (
      <div className="flex justify-center py-16">
        <div className="w-10 h-10 rounded-full border-4 border-violet-100 border-t-violet-600 animate-spin" />
      </div>
    )
  }

  const { metrics, bands, analyses } = data

  return (
    <div className="flex flex-col gap-8">
      {/* Uso por periodo */}
      <section>
        <h2 className="text-base font-bold text-gray-900 mb-3">Uso de la herramienta</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard label="Total" value={seriesTotal(metrics.by_day)} hint="análisis registrados" />
          <StatCard label="Último día" value={latest(metrics.by_day)} hint="con actividad" />
          <StatCard label="Último mes" value={latest(metrics.by_month)} hint="con actividad" />
          <StatCard label="Último año" value={latest(metrics.by_year)} hint="con actividad" />
        </div>
      </section>

      {/* Distribución por banda */}
      <section>
        <h2 className="text-base font-bold text-gray-900 mb-3">
          Distribución por banda
          <span className="ml-2 text-sm font-medium text-gray-400">({bands.total} con calificación)</span>
        </h2>
        <div className="card p-5 flex flex-col gap-3">
          {bands.distribution.map((b) => {
            const c = BAND_COLOR[b.band] || BAND_COLOR.Crítico
            return (
              <div key={b.band} className="flex items-center gap-3">
                <span className={`w-24 text-sm font-semibold ${c.text}`}>{b.band}</span>
                <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div className={`h-full ${c.bar} rounded-full`} style={{ width: `${b.percentage}%` }} />
                </div>
                <span className="w-20 text-right text-sm text-gray-600">
                  {b.count} · {b.percentage}%
                </span>
              </div>
            )
          })}
          {bands.total === 0 && (
            <p className="text-sm text-gray-400 text-center py-2">Aún no hay análisis con calificación.</p>
          )}
        </div>
      </section>

      {/* Listado de análisis */}
      <section>
        <h2 className="text-base font-bold text-gray-900 mb-3">
          Análisis realizados
          <span className="ml-2 text-sm font-medium text-gray-400">(sin documentos)</span>
        </h2>
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wide">
                <th className="text-left font-semibold px-4 py-2.5">Fecha</th>
                <th className="text-left font-semibold px-4 py-2.5">Estado</th>
                <th className="text-left font-semibold px-4 py-2.5">Banda</th>
                <th className="text-right font-semibold px-4 py-2.5">Score</th>
                <th className="text-right font-semibold px-4 py-2.5">HUs</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((a) => {
                const c = BAND_COLOR[a.band] || BAND_COLOR.Crítico
                const scored = a.status === 'ok' || a.status === 'partial'
                return (
                  <tr key={a.analysis_id} className="border-t border-gray-100">
                    <td className="px-4 py-2.5 text-gray-600 whitespace-nowrap">
                      {a.created_at ? new Date(a.created_at).toLocaleString('es') : '—'}
                    </td>
                    <td className="px-4 py-2.5 text-gray-700">{STATUS_LABEL[a.status] || a.status}</td>
                    <td className="px-4 py-2.5">
                      {scored ? (
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${c.chip}`}>{a.band}</span>
                      ) : <span className="text-gray-300">—</span>}
                    </td>
                    <td className="px-4 py-2.5 text-right font-semibold text-gray-800">
                      {scored ? Math.round(a.overall_score) : '—'}
                    </td>
                    <td className="px-4 py-2.5 text-right text-gray-600">{a.story_count}</td>
                  </tr>
                )
              })}
              {analyses.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-400">Sin análisis todavía.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
