import { useEffect, useState } from 'react'
import type { Vacancy, VacancyStatus, StatusHistoryEntry } from '../../types'
import ModalityBadge from '../ui/ModalityBadge'
import StatusBadge from '../ui/StatusBadge'
import CoherenceBadge from '../ui/CoherenceBadge'
import { updateVacancyStatus, fetchStatusHistory, blacklistCompany } from '../../api/vacancies'
import { timeAgo } from '../../utils/date'
import TailorCvPanel from './TailorCvPanel'

interface Props {
  vacancy: Vacancy
  onClose: () => void
  onStatusChange: (updated: Vacancy) => void
  onFilterCompany: (company: string) => void
  onFilterCity: (city: string) => void
}

const STATUS_OPTIONS: { value: VacancyStatus; label: string }[] = [
  { value: 'nueva',      label: 'Nueva' },
  { value: 'guardada',   label: 'Guardada' },
  { value: 'postulada',  label: 'Postulada' },
  { value: 'observada',  label: 'Observada' },
  { value: 'descartada', label: 'Descartada' },
  { value: 'no_idoneo',  label: 'No idóneo' },
]

const STATUS_LABELS: Record<VacancyStatus, string> = {
  nueva:      'Nueva',
  guardada:   'Guardada',
  postulada:  'Postulada',
  observada:  'Observada',
  descartada: 'Descartada',
  no_idoneo:  'No idóneo',
}

export default function VacancyDetail({ vacancy, onClose, onStatusChange, onFilterCompany, onFilterCity }: Props) {
  const [updating, setUpdating]             = useState(false)
  const [history, setHistory]               = useState<StatusHistoryEntry[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [blacklisting, setBlacklisting]     = useState(false)
  const [blacklisted, setBlacklisted]       = useState(false)

  useEffect(() => {
    setHistory([])
    setBlacklisted(false)
    setLoadingHistory(true)
    fetchStatusHistory(vacancy.id)
      .then(setHistory)
      .catch(() => setHistory([]))
      .finally(() => setLoadingHistory(false))
  }, [vacancy.id])

  async function handleStatusChange(status: VacancyStatus) {
    if (status === vacancy.status) return
    setUpdating(true)
    try {
      const updated = await updateVacancyStatus(vacancy.id, status)
      onStatusChange(updated)
      const newEntry: StatusHistoryEntry = {
        id:         Date.now(),
        vacancy_id: vacancy.id,
        status,
        changed_at: new Date().toISOString(),
      }
      setHistory((prev) => [...prev, newEntry])
    } finally {
      setUpdating(false)
    }
  }

  async function handleBlacklist() {
    if (!vacancy.company || blacklisted) return
    setBlacklisting(true)
    try {
      await blacklistCompany(vacancy.company)
      setBlacklisted(true)
    } finally {
      setBlacklisting(false)
    }
  }

  const combinedScore = vacancy.cv_score !== null && vacancy.cv_score_semantic !== null
    ? (vacancy.cv_score * 0.6 + vacancy.cv_score_semantic * 0.4).toFixed(1)
    : null

  return (
    <div className="bg-white rounded-xl border-2 border-blue-100 shadow-lg flex flex-col overflow-hidden max-h-[calc(100vh-6rem)]">
      <div className="border-b border-gray-100 px-6 py-4 flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h2 className="text-base font-semibold text-gray-900 leading-snug">{vacancy.title}</h2>
          <p className="text-sm text-gray-400 mt-0.5">{vacancy.company ?? 'Empresa no especificada'}</p>
        </div>
        <button onClick={onClose} className="text-gray-300 hover:text-gray-600 transition-colors text-lg leading-none mt-0.5 shrink-0">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-5">
        <div className="flex flex-wrap gap-2 items-center">
          <ModalityBadge modality={vacancy.modality} />
          <StatusBadge status={vacancy.status} />
          <CoherenceBadge vacanteCoherente={vacancy.vacante_coherente} />
        </div>

        {/* Evaluación de coherencia */}
        {vacancy.vacante_coherente === false && vacancy.coherence_detail && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
            <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1.5">
              ⚠️ Posible mezcla de cargos
            </p>
            <p className="text-sm text-amber-800 leading-relaxed">
              {vacancy.coherence_detail.justificacion}
            </p>
            {vacancy.coherence_detail.cargos_detectados.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {vacancy.coherence_detail.cargos_detectados.map((cargo) => (
                  <span key={cargo} className="text-xs bg-amber-100 text-amber-700 border border-amber-300 px-2 py-0.5 rounded-full">
                    {cargo}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Scores */}
        {combinedScore !== null ? (
          <div className="bg-blue-50 rounded-lg px-4 py-3 flex items-center gap-6">
            <div className="flex flex-col items-center">
              <span className="text-2xl font-bold text-blue-600">{combinedScore}</span>
              <span className="text-xs text-blue-400">Score combinado</span>
            </div>
            <div className="w-px h-10 bg-blue-200" />
            <div className="flex flex-col items-center">
              <span className="text-lg font-semibold text-blue-500">{vacancy.cv_score}</span>
              <span className="text-xs text-blue-400">Keywords</span>
            </div>
            <div className="w-px h-10 bg-blue-200" />
            <div className="flex flex-col items-center">
              <span className="text-lg font-semibold text-blue-500">{vacancy.cv_score_semantic?.toFixed(2)}</span>
              <span className="text-xs text-blue-400">Semántico</span>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-lg px-4 py-3">
            <p className="text-xs text-gray-400">Score disponible después del ranking (Paso 7)</p>
          </div>
        )}

        {/* Estado */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Cambiar estado</p>
          <div className="flex flex-wrap gap-2">
            {STATUS_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => handleStatusChange(opt.value)}
                disabled={updating}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-all disabled:opacity-50 ${
                  vacancy.status === opt.value
                    ? 'bg-blue-600 text-white border-blue-600 font-medium'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-600'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Historial de status */}
        {(loadingHistory || history.length > 0) && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Historial</p>
            {loadingHistory ? (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-xs text-gray-400">Cargando...</span>
              </div>
            ) : (
              <div className="flex flex-col gap-1.5">
                {history.map((entry) => (
                  <div key={entry.id} className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-300 shrink-0" />
                    <span className="font-medium text-gray-700">{STATUS_LABELS[entry.status]}</span>
                    <span className="text-gray-400">{timeAgo(entry.changed_at)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Meta */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          {vacancy.city && (
            <div className="flex items-center gap-1.5 text-gray-600">
              <span>📍</span>
              <button
                onClick={() => onFilterCity(vacancy.city!)}
                className="hover:text-blue-600 hover:underline transition-colors text-left"
              >
                {vacancy.city}{vacancy.department ? `, ${vacancy.department}` : ''}
              </button>
            </div>
          )}
          {vacancy.company && (
            <div className="flex items-center gap-1.5 text-gray-600">
              <span>🏢</span>
              <div className="flex items-center gap-1.5 min-w-0">
                <button
                  onClick={() => onFilterCompany(vacancy.company!)}
                  className="hover:text-blue-600 hover:underline transition-colors text-left truncate"
                >
                  {vacancy.company}
                </button>
                <button
                  onClick={handleBlacklist}
                  disabled={blacklisting || blacklisted}
                  title="Agregar a blacklist"
                  className={`text-xs shrink-0 px-1.5 py-0.5 rounded border transition-all disabled:opacity-50 ${
                    blacklisted
                      ? 'text-red-500 border-red-200 bg-red-50'
                      : 'text-gray-400 border-gray-200 hover:text-red-500 hover:border-red-300'
                  }`}
                >
                  {blacklisted ? '🚫' : '＋🚫'}
                </button>
              </div>
            </div>
          )}
          {vacancy.salary_range && (
            <div className="flex items-center gap-1.5 text-gray-600">
              <span>💰</span>
              <span>{vacancy.salary_range}</span>
            </div>
          )}
          {vacancy.source && (
            <div className="flex items-center gap-1.5 text-gray-600">
              <span>🔗</span>
              <span>{vacancy.source.name}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5 text-gray-400 text-xs">
            <span>🕐</span>
            <span>Scrapeado {timeAgo(vacancy.scraped_at)}</span>
          </div>
          {vacancy.status_changed_at && (
            <div className="flex items-center gap-1.5 text-gray-400 text-xs">
              <span>✏️</span>
              <span>Estado cambiado {timeAgo(vacancy.status_changed_at)}</span>
            </div>
          )}
        </div>

        {/* Keywords */}
        {vacancy.cv_keywords_detail && (
          <div className="flex flex-col gap-3">
            {vacancy.cv_keywords_detail.matched.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-green-600 uppercase tracking-wide mb-2">Keywords encontradas</p>
                <div className="flex flex-wrap gap-1.5">
                  {vacancy.cv_keywords_detail.matched.map((kw) => (
                    <span key={kw} className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full">{kw}</span>
                  ))}
                </div>
              </div>
            )}
            {vacancy.cv_keywords_detail.missing.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-red-500 uppercase tracking-wide mb-2">Keywords faltantes</p>
                <div className="flex flex-wrap gap-1.5">
                  {vacancy.cv_keywords_detail.missing.map((kw) => (
                    <span key={kw} className="text-xs bg-red-50 text-red-600 border border-red-200 px-2 py-0.5 rounded-full">{kw}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Descripción */}
        {vacancy.description && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Descripción</p>
            <p className="text-sm text-gray-600 whitespace-pre-line leading-relaxed">{vacancy.description}</p>
          </div>
        )}

        {/* CV a medida — solo se genera cuando el usuario pulsa el botón */}
        <TailorCvPanel
          vacancy={vacancy}
          onGenerated={(updated) => onStatusChange({ ...vacancy, ...updated })}
        />
      </div>

      <div className="border-t border-gray-100 px-6 py-4">
        <a href={vacancy.url} target="_blank" rel="noreferrer" className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2.5 rounded-lg transition-colors">
          Ver vacante original →
        </a>
      </div>
    </div>
  )
}