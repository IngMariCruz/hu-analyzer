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
 * Recupera un análisis previo por su identificador opaco (sin re-subir el documento).
 * @param {string} analysisId
 * @returns {Promise<object>} AnalyzeResponse
 */
export async function getAnalysis(analysisId) {
  const response = await fetch(`${API_BASE}/analyze/${analysisId}`)
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || 'No se pudo recuperar el análisis.')
  }
  return data
}

const REPORT_FILENAMES = {
  business: 'reglas-de-negocio.pdf',
  hu: 'validacion-hus.pdf',
}

/**
 * Descarga un reporte PDF persistido por analysis_id.
 * @param {string} analysisId
 * @param {'business'|'hu'} type
 */
export async function downloadReportById(analysisId, type) {
  const response = await fetch(`${API_BASE}/report/${analysisId}?type=${type}`)

  if (!response.ok) {
    let detail = 'Error al generar el reporte.'
    try {
      detail = (await response.json()).detail || detail
    } catch {
      // respuesta sin JSON
    }
    if (response.status === 404) {
      detail = 'El análisis ya no está disponible. Vuelve a subir el documento.'
    }
    throw new Error(detail)
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = REPORT_FILENAMES[type] || 'reporte.pdf'
  a.click()
  URL.revokeObjectURL(url)
}
