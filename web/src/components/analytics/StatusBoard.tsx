import type { StatusTimelineData } from '../../api/analytics'

const STATUS_LABELS: Record<string, string> = {
  nueva:      'Nueva',
  guardada:   'Guardada',
  postulada:  'Postulada',
  descartada: 'Descartada',
  observada:  'Observada',
}

const STATUS_COLORS: Record<string, string> = {
  nueva:      'bg-gray-100 text-gray-600 border-gray-200',
  guardada:   'bg-yellow-50 text-yellow-700 border-yellow-200',
  postulada:  'bg-blue-50 text-blue-700 border-blue-200',
  descartada: 'bg-red-50 text-red-600 border-red-200',
  observada:  'bg-orange-50 text-orange-700 border-orange-200',
}

const STATUS_BAR_COLORS: Record<string, string> = {
  nueva:      'bg-gray-400',
  guardada:   'bg-yellow-400',
  postulada:  'bg-blue-500',
  descartada: 'bg-red-400',
  observada:  'bg-orange-400',
}

interface Props {
  data: StatusTimelineData
}

export default function StatusBoard({ data }: Props) {
  const total = data.by_status.reduce((acc, s) => acc + s.total, 0)
  const max = data.by_status[0]?.total ?? 1

  // Agrupar timeline por fecha
  const timelineByDate = data.timeline.reduce<Record<string, Record<string, number>>>(
    (acc, row) => {
      const date = row.date.split('T')[0]
      if (!acc[date]) acc[date] = {}
      acc[date][row.status] = row.total
      return acc
    },
    {}
  )

  const dates = Object.keys(timelineByDate).sort()

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 md:col-span-2 flex flex-col gap-6">
      <h2 className="text-sm font-semibold text-gray-700">Postulaciones y estados</h2>

      {/* Tarjetas de conteo por status */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {data.by_status.map((s) => (
          <div key={s.status} className={`rounded-lg border px-4 py-3 flex flex-col gap-1 ${STATUS_COLORS[s.status] ?? 'bg-gray-50 text-gray-600 border-gray-200'}`}>
            <span className="text-2xl font-bold">{s.total}</span>
            <span className="text-xs">{STATUS_LABELS[s.status] ?? s.status}</span>
            <div className="w-full bg-white/60 rounded-full h-1.5 mt-1">
              <div
                className={`h-1.5 rounded-full ${STATUS_BAR_COLORS[s.status] ?? 'bg-gray-400'}`}
                style={{ width: `${(s.total / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Barras por status */}
      <div className="flex flex-col gap-2">
        {data.by_status.map((s) => (
          <div key={s.status} className="flex items-center gap-3">
            <span className="text-sm text-gray-600 w-24 shrink-0">{STATUS_LABELS[s.status] ?? s.status}</span>
            <div className="flex-1 bg-gray-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${STATUS_BAR_COLORS[s.status] ?? 'bg-gray-400'}`}
                style={{ width: `${(s.total / max) * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-400 w-8 text-right">{s.total}</span>
          </div>
        ))}
      </div>

      {/* Timeline */}
      {dates.length === 0 ? (
        <p className="text-sm text-gray-400">Sin actividad registrada — los cambios de estado aparecerán aquí.</p>
      ) : (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Actividad por día</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-400 border-b border-gray-100">
                  <th className="text-left py-2 pr-4">Fecha</th>
                  {Object.keys(STATUS_LABELS).filter(s => s !== 'nueva').map(s => (
                    <th key={s} className="text-right py-2 px-2">{STATUS_LABELS[s]}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dates.map((date) => (
                  <tr key={date} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 text-gray-600">{date}</td>
                    {Object.keys(STATUS_LABELS).filter(s => s !== 'nueva').map(s => (
                      <td key={s} className="py-2 px-2 text-right text-gray-500">
                        {timelineByDate[date][s] ?? '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}