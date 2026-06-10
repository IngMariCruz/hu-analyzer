import { useState, useRef } from 'react'

const ACCEPTED = {
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/pdf': '.pdf',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
  'text/plain': '.txt',
}

export default function FileUpload({ onFileSelect, loading }) {
  const [dragging, setDragging] = useState(false)
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  const validate = (file) => {
    if (!ACCEPTED[file.type]) {
      setError(`Formato no soportado. Usa ${Object.values(ACCEPTED).join(', ')}`)
      return false
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('El archivo supera el límite de 10 MB.')
      return false
    }
    setError('')
    return true
  }

  const handleFile = (file) => {
    if (!file) return
    if (validate(file)) {
      setSelected(file)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleAnalyze = () => {
    if (selected) onFileSelect(selected)
  }

  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-4">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !loading && inputRef.current.click()}
        className={`
          relative flex flex-col items-center justify-center gap-3
          rounded-2xl border-2 border-dashed p-10 cursor-pointer
          transition-all duration-200
          ${dragging
            ? 'border-violet-600 bg-violet-50'
            : selected
              ? 'border-violet-400 bg-violet-50/50'
              : 'border-gray-300 bg-white hover:border-violet-400 hover:bg-violet-50/30'
          }
          ${loading ? 'pointer-events-none opacity-60' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".docx,.pdf,.xlsx,.txt"
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {/* Ícono */}
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center
          ${selected ? 'bg-violet-100' : 'bg-gray-100'}`}>
          <svg className={`w-7 h-7 ${selected ? 'text-violet-600' : 'text-gray-400'}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            {selected
              ? <path strokeLinecap="round" strokeLinejoin="round"
                  d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              : <path strokeLinecap="round" strokeLinejoin="round"
                  d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            }
          </svg>
        </div>

        {selected ? (
          <div className="text-center">
            <p className="font-semibold text-gray-800">{selected.name}</p>
            <p className="text-sm text-gray-500 mt-0.5">
              {(selected.size / 1024).toFixed(0)} KB · Clic para cambiar
            </p>
          </div>
        ) : (
          <div className="text-center">
            <p className="font-semibold text-gray-700">Arrastra tu archivo aquí</p>
            <p className="text-sm text-gray-500 mt-0.5">o haz clic para seleccionar</p>
            <p className="text-xs text-gray-400 mt-2">.docx · .pdf · .xlsx · .txt · máx 10 MB</p>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <p className="text-sm text-red-600 text-center">{error}</p>
      )}

      {/* Botón analizar */}
      {selected && !error && (
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full py-3 px-6 bg-violet-600 hover:bg-violet-700 disabled:bg-violet-300
            text-white font-semibold rounded-xl transition-colors duration-200 shadow-sm"
        >
          {loading ? 'Analizando...' : 'Analizar Historias de Usuario'}
        </button>
      )}
    </div>
  )
}
