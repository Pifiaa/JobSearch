import type { VacancyStatus } from '../../types'

const LABELS: Record<VacancyStatus, string> = {
  nueva:      'Nueva',
  guardada:   'Guardada',
  postulada:  'Postulada',
  descartada: 'Descartada',
  observada:  'Observada',
  no_idoneo:  'No idóneo',
}

const COLORS: Record<VacancyStatus, string> = {
  nueva:      'bg-gray-100 text-gray-700',
  guardada:   'bg-yellow-100 text-yellow-800',
  postulada:  'bg-blue-100 text-blue-800',
  descartada: 'bg-red-100 text-red-700',
  observada:  'bg-orange-100 text-orange-800',
  no_idoneo:  'bg-purple-100 text-purple-800',
}

interface Props {
  status: VacancyStatus
}

export default function StatusBadge({ status }: Props) {
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${COLORS[status]}`}>
      {LABELS[status]}
    </span>
  )
}