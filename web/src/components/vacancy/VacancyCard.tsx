import type { Vacancy } from '../../types'
import ModalityBadge from '../ui/ModalityBadge'
import StatusBadge from '../ui/StatusBadge'
import CoherenceBadge from '../ui/CoherenceBadge'
import { timeAgo } from '../../utils/date'

interface Props {
  vacancy: Vacancy
  onClick: (vacancy: Vacancy) => void
  isSelected?: boolean
}

function combinedScore(vacancy: Vacancy): number | null {
  if (vacancy.cv_score === null || vacancy.cv_score_semantic === null) return null
  return (vacancy.cv_score * 0.6) + (vacancy.cv_score_semantic * 0.4)
}

function ScorePill({ vacancy }: { vacancy: Vacancy }) {
  const score = combinedScore(vacancy)
  if (score === null) return null

  const color = score >= 60
    ? 'bg-green-100 text-green-700'
    : score >= 35
    ? 'bg-yellow-100 text-yellow-700'
    : 'bg-gray-100 text-gray-500'

  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
      {score.toFixed(0)}
    </span>
  )
}

export default function VacancyCard({ vacancy, onClick, isSelected = false }: Props) {
  return (
    <div
      onClick={() => onClick(vacancy)}
      className={`bg-white rounded-xl px-5 py-4 cursor-pointer transition-all group border-2 ${
        isSelected
          ? 'border-blue-500 shadow-md'
          : 'border-transparent border border-gray-100 hover:border-blue-300 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold truncate transition-colors ${isSelected ? 'text-blue-600' : 'text-gray-900 group-hover:text-blue-600'}`}>
            {vacancy.title}
          </h3>
          <p className="text-sm text-gray-400 truncate mt-0.5">
            {vacancy.company ?? 'Empresa no especificada'}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <ScorePill vacancy={vacancy} />
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <ModalityBadge modality={vacancy.modality} />
          <StatusBadge status={vacancy.status} />
          <CoherenceBadge vacanteCoherente={vacancy.vacante_coherente} />
          {vacancy.city && vacancy.city !== '4' && (
            <span className="text-xs text-gray-400">📍 {vacancy.city}</span>
          )}
          {vacancy.source && (
            <span className="text-xs text-gray-500">· {vacancy.source.name}</span>
          )}
        </div>
        <span className="text-xs text-gray-500">{timeAgo(vacancy.scraped_at)}</span>
      </div>
    </div>
  )
}