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
