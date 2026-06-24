import { useState } from 'react'
import { Link } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import ResultCard from '../components/ResultCard'
import ProjectSummary from '../components/ProjectSummary'
import { analyzeFile, downloadReportById } from '../services/api'

function LoadingState() {
  return (
    <div className="flex flex-col items-center gap-4 py-16">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-violet-100" />
        <div className="absolute inset-0 rounded-full border-4 border-violet-600 border-t-transparent animate-spin" />
      </div>
      <div className="text-center">
        <p className="font-semibold text-gray-800">Analizando Historias de Usuario</p>
        <p className="text-sm text-gray-500 mt-1">Esto puede tardar unos minutos...</p>
      </div>
    </div>
  )
}

function ErrorBanner({ message, onRetry, onDismiss }) {
  return (
    <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
      <svg className="w-5 h-5 text-red-500 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
      <div className="flex-1">
        <p className="text-sm font-semibold text-red-800">No se pudo completar el análisis</p>
        <p className="text-sm text-red-700 mt-0.5">{message}</p>
        {onRetry && (
          <button onClick={onRetry} className="mt-2 text-sm font-semibold text-red-700 underline hover:text-red-900">
            Reintentar
          </button>
        )}
      </div>
      <button onClick={onDismiss} className="text-red-400 hover:text-red-600 transition-colors">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}

// Alerta para los estados del gate (no_project / invalid).
function GateAlert({ status, message, onReset }) {
  const isNoProject = status === 'no_project'
  const title = isNoProject
    ? 'El documento no contiene un proyecto'
    : 'El contenido debe replantearse'
  const wrapClass = isNoProject
    ? 'bg-amber-50 border-amber-200'
    : 'bg-violet-50 border-violet-200'
  return (
    <div className={`${wrapClass} border rounded-2xl p-6 text-center`}>
      <div className="text-4xl mb-3">{isNoProject ? '📄' : '✏️'}</div>
      <h2 className="text-lg font-bold text-gray-900 mb-2">{title}</h2>
      <p className="text-sm text-gray-700 leading-relaxed max-w-md mx-auto">
        {message || 'No fue posible analizar el documento.'}
      </p>
      <button
        onClick={onReset}
        className="mt-5 px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold rounded-lg transition-colors"
      >
        Subir otro documento
      </button>
    </div>
  )
}

function PartialBanner() {
  return (
    <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4">
      <span className="text-lg">⚠️</span>
      <p className="text-sm text-amber-800">
        Algunas Historias de Usuario no pudieron evaluarse y se marcaron como
        <strong> No evaluada</strong>. El resto del análisis es válido.
      </p>
    </div>
  )
}

function DownloadButton({ label, loading, disabled, onClick }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex items-center gap-1.5 px-3 py-2 bg-violet-600 hover:bg-violet-700
        disabled:bg-violet-300 text-white text-sm font-semibold rounded-lg
        transition-colors duration-200 shadow-sm"
    >
      {loading ? (
        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      ) : (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )}
      {label}
    </button>
  )
}

export default function AnalyzerPage() {
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(null) // 'business' | 'hu' | null
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [lastFile, setLastFile] = useState(null)

  const runAnalysis = async (file) => {
    setLastFile(file)
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await analyzeFile(file)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (type) => {
    if (!result?.analysis_id) {
      setError('El análisis ya no está disponible. Vuelve a subir el documento.')
      return
    }
    setDownloading(type)
    try {
      await downloadReportById(result.analysis_id, type)
    } catch (err) {
      setError(err.message)
    } finally {
      setDownloading(null)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError('')
    setLastFile(null)
  }

  const isGate = result && (result.status === 'no_project' || result.status === 'invalid')
  const hasResults = result && (result.status === 'ok' || result.status === 'partial')

  return (
    <div className="min-h-screen bg-[#FAFAF9]">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="font-bold text-gray-900 text-lg tracking-tight">HU Analyzer</span>
          </div>

          {hasResults ? (
            <div className="flex items-center gap-2">
              <DownloadButton
                label="Reglas de negocio"
                loading={downloading === 'business'}
                disabled={downloading !== null}
                onClick={() => handleDownload('business')}
              />
              <DownloadButton
                label="Validación de HUs"
                loading={downloading === 'hu'}
                disabled={downloading !== null}
                onClick={() => handleDownload('hu')}
              />

              <button
                onClick={handleReset}
                className="ml-1 text-sm text-violet-600 hover:text-violet-700 font-medium
                  flex items-center gap-1.5 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Nuevo análisis
              </button>
            </div>
          ) : (
            <Link
              to="/admin"
              className="text-sm text-gray-500 hover:text-violet-600 font-medium flex items-center gap-1.5 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Admin
            </Link>
          )}
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10">
        {!result && !loading && (
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-3">
              Analiza la calidad de tus HU
            </h1>
            <p className="text-gray-500 text-base max-w-md mx-auto leading-relaxed">
              Sube un archivo con tus Historias de Usuario y obtén calificaciones,
              retroalimentación y un reporte PDF descargable.
            </p>
          </div>
        )}

        {error && (
          <div className="mb-6">
            <ErrorBanner
              message={error}
              onRetry={lastFile ? () => runAnalysis(lastFile) : null}
              onDismiss={() => setError('')}
            />
          </div>
        )}

        {!result && !loading && <FileUpload onFileSelect={runAnalysis} loading={loading} />}
        {loading && <LoadingState />}

        {isGate && (
          <GateAlert status={result.status} message={result.message} onReset={handleReset} />
        )}

        {hasResults && !loading && (
          <div className="flex flex-col gap-6">
            {result.status === 'partial' && <PartialBanner />}
            <ProjectSummary
              summary={result.project_summary}
              overallScore={result.overall_score}
              overallBand={result.overall_band}
            />
            <div>
              <h2 className="text-base font-bold text-gray-900 mb-3">
                Análisis por Historia de Usuario
                <span className="ml-2 text-sm font-medium text-gray-400">
                  ({result.hu_results.length} HU analizadas)
                </span>
              </h2>
              <div className="flex flex-col gap-3">
                {result.hu_results.map((hu) => (
                  <ResultCard key={hu.hu_id} result={hu} />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
