import type { VacancyModality } from '../../types'

const LABELS: Record<VacancyModality, string> = {
  presencial: 'Presencial',
  hibrido: 'Híbrido',
  remoto_colombia: 'Remoto CO',
  remoto_internacional: 'Remoto INT',
}

const COLORS: Record<VacancyModality, string> = {
  presencial: 'bg-blue-100 text-blue-800',
  hibrido: 'bg-purple-100 text-purple-800',
  remoto_colombia: 'bg-green-100 text-green-800',
  remoto_internacional: 'bg-emerald-100 text-emerald-800',
}

interface Props {
  modality: VacancyModality
}

export default function ModalityBadge({ modality }: Props) {
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${COLORS[modality]}`}>
      {LABELS[modality]}
    </span>
  )
}