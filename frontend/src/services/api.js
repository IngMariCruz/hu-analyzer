const API_BASE = '/api/v1'

/**
 * Envía un archivo al backend para análisis de HU.
 * @param {File} file
 * @returns {Promise<object>} AnalyzeResponse
 */
export async function analyzeFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Error al analizar el archivo.')
  }

  return data
}

/**
 * Envía el resultado del análisis al backend y descarga el PDF.
 * @param {object} result - AnalyzeResponse
 */
export async function downloadReport(result) {
  const response = await fetch('/api/v1/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(result),
  })

  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.detail || 'Error al generar el reporte.')
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'reporte-hu-analyzer.pdf'
  a.click()
  URL.revokeObjectURL(url)
}
