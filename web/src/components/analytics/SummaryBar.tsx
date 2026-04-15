import { useEffect } from 'react'
import { useAnalyticsStore } from '../../store/analyticsStore'

const MODALITY_LABELS: Record<string, string> = {
  presencial: 'Presencial',
  hibrido: 'Híbrido',
  remoto_colombia: 'Remoto CO',
  remoto_internacional: 'Remoto INT',
}

export default function SummaryBar() {
  const { summary, loadSummary } = useAnalyticsStore()

  useEffect(() => {
    loadSummary()
  }, [])

  if (!summary) return null

  return (
    <div className="bg-white border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-6 overflow-x-auto text-sm">
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="text-2xl font-bold text-blue-600">{summary.total}</span>
          <span className="text-gray-500 text-xs font-medium">vacantes</span>
          {summary.new_since !== null && summary.new_since > 0 && (
            <span className="text-xs font-semibold bg-green-500 text-white px-1.5 py-0.5 rounded-full ml-1">
              +{summary.new_since} nuevas
            </span>
          )}
        </div>

        <div className="w-px h-6 bg-gray-200 shrink-0" />

        <div className="flex items-center gap-4 shrink-0">
          {summary.by_modality.map((m) => (
            <div key={m.modality} className="flex items-center gap-1.5">
              <span className="text-gray-800 font-semibold">{m.total}</span>
              <span className="text-gray-500 text-xs">{MODALITY_LABELS[m.modality] ?? m.modality}</span>
            </div>
          ))}
        </div>

        <div className="w-px h-6 bg-gray-200 shrink-0" />

        <div className="flex items-center gap-4 shrink-0">
          {summary.by_source.map((s) => (
            <div key={s.source} className="flex items-center gap-1.5">
              <span className="text-gray-800 font-semibold">{s.total}</span>
              <span className="text-gray-500 text-xs">{s.source}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}