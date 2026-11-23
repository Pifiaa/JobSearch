import { useState } from 'react'
import type { Vacancy } from '../../types'
import { generateTailoredCv, tailoredCvPdfUrl, tailoredCvBriefUrl } from '../../api/cvTailor'

interface Props {
  vacancy: Vacancy
  onGenerated: (updated: Partial<Vacancy>) => void
}

export default function TailorCvPanel({ vacancy, onGenerated }: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<string | null>(null)

  const data = vacancy.tailored_cv

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    try {
      const tailored = await generateTailoredCv(vacancy.id)
      onGenerated({ tailored_cv: tailored, tailored_cv_generated_at: new Date().toISOString() })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo generar el CV adaptado')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-blue-50/50 border border-blue-100 rounded-lg px-4 py-3">
      <div className="flex items-center justify-between gap-2 mb-2">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">CV a medida</p>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="text-xs px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors disabled:opacity-50"
        >
          {loading ? 'Generando…' : data ? 'Regenerar' : 'Generar CV a medida'}
        </button>
      </div>

      {error && <p className="text-xs text-red-500 mb-2">{error}</p>}

      {loading && (
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <div className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin" />
          Consultando el modelo local, puede tardar hasta un minuto…
        </div>
      )}

      {!loading && data && !data.error && (
        <div className="flex flex-col gap-3">
          <p className="text-sm text-gray-700 leading-relaxed">{data.resumen_profesional}</p>

          {data.habilidades_destacadas.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {data.habilidades_destacadas.map((h) => (
                <span key={h} className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">{h}</span>
              ))}
            </div>
          )}

          {data.sugerencias_bullets.length > 0 && (
            <ul className="list-disc list-inside text-xs text-gray-600 flex flex-col gap-1">
              {data.sugerencias_bullets.map((b, i) => <li key={i}>{b}</li>)}
            </ul>
          )}

          {data.brechas.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-amber-600 mb-1">Brechas frente a esta vacante</p>
              <div className="flex flex-wrap gap-1.5">
                {data.brechas.map((b) => (
                  <span key={b} className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full">{b}</span>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2 pt-1">
            <a
              href={tailoredCvPdfUrl(vacancy.id)}
              className="text-xs px-3 py-1.5 rounded-lg border border-blue-200 text-blue-700 hover:bg-blue-50 transition-colors"
            >
              Descargar PDF
            </a>
            <a
              href={tailoredCvBriefUrl(vacancy.id)}
              className="text-xs px-3 py-1.5 rounded-lg border border-blue-200 text-blue-700 hover:bg-blue-50 transition-colors"
            >
              Descargar brief (.md, para IA)
            </a>
          </div>
        </div>
      )}

      {!loading && data?.error && (
        <p className="text-xs text-red-500">
          El modelo no pudo generar el resultado ({data.error}). Verifica que Ollama esté corriendo e inténtalo de nuevo.
        </p>
      )}
    </div>
  )
}
