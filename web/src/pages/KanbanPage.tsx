import { useEffect, useState, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { fetchVacancies, updateVacancyStatus } from '../api/vacancies'
import VacancyCard from '../components/vacancy/VacancyCard'
import VacancyDetail from '../components/vacancy/VacancyDetail'
import Pagination from '../components/ui/Pagination'
import type { Vacancy, VacancyStatus, PaginatedResponse } from '../types'

// ─── tipos ────────────────────────────────────────────────────────────────────

type KanbanStatus = 'guardada' | 'postulada' | 'observada'

interface ColumnState {
  vacancies: Vacancy[]
  loading: boolean
  error: string | null
  page: number
  lastPage: number
  total: number
}

const COLUMNS: { status: KanbanStatus; label: string; color: string; dot: string }[] = [
  { status: 'guardada',  label: 'Guardadas',  color: 'border-yellow-300', dot: 'bg-yellow-400' },
  { status: 'postulada', label: 'Postuladas', color: 'border-blue-400',   dot: 'bg-blue-500'   },
  { status: 'observada', label: 'Observadas', color: 'border-purple-300', dot: 'bg-purple-400' },
]

const PER_PAGE = 10

// ─── estado inicial ────────────────────────────────────────────────────────────

function emptyColumn(): ColumnState {
  return { vacancies: [], loading: true, error: null, page: 1, lastPage: 1, total: 0 }
}

// ─── componente ───────────────────────────────────────────────────────────────

export default function KanbanPage() {
  const [columns, setColumns] = useState<Record<KanbanStatus, ColumnState>>({
    guardada:  emptyColumn(),
    postulada: emptyColumn(),
    observada: emptyColumn(),
  })
  const [selected, setSelected] = useState<Vacancy | null>(null)
  const cardRefs = useRef<Map<number, HTMLDivElement>>(new Map())

  // ── carga de columna ────────────────────────────────────────────────────────

  const loadColumn = useCallback(async (status: KanbanStatus, page: number) => {
    setColumns((prev) => ({
      ...prev,
      [status]: { ...prev[status], loading: true, error: null },
    }))
    try {
      const result: PaginatedResponse<Vacancy> = await fetchVacancies({
        status,
        page,
        per_page: PER_PAGE,
        sort: 'score',
      })
      setColumns((prev) => ({
        ...prev,
        [status]: {
          vacancies: result.data,
          loading:   false,
          error:     null,
          page:      result.current_page,
          lastPage:  result.last_page,
          total:     result.total,
        },
      }))
    } catch (err) {
      setColumns((prev) => ({
        ...prev,
        [status]: {
          ...prev[status],
          loading: false,
          error:   err instanceof Error ? err.message : 'Error al cargar',
        },
      }))
    }
  }, [])

  // ── carga inicial ────────────────────────────────────────────────────────────

  useEffect(() => {
    loadColumn('guardada',  1)
    loadColumn('postulada', 1)
    loadColumn('observada', 1)
  }, [loadColumn])

  // ── cambio de página ─────────────────────────────────────────────────────────

  function handlePageChange(status: KanbanStatus, page: number) {
    loadColumn(status, page)
  }

  // ── cambio de status desde el detalle ────────────────────────────────────────

  function handleStatusChange(updated: Vacancy) {
    // Quitar de todas las columnas y reinsertar donde corresponda
    setColumns((prev) => {
      const next = { ...prev }
      ;(Object.keys(next) as KanbanStatus[]).forEach((s) => {
        next[s] = {
          ...next[s],
          vacancies: next[s].vacancies.filter((v) => v.id !== updated.id),
        }
      })
      const target = updated.status as KanbanStatus
      if (target in next) {
        next[target] = {
          ...next[target],
          vacancies: [updated, ...next[target].vacancies],
        }
      }
      return next
    })
    setSelected(updated)
  }

  function handleSelect(vacancy: Vacancy) {
    setSelected((prev) => prev?.id === vacancy.id ? null : vacancy)
  }

  // ── render ────────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">

      {/* Header */}
      <header className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-4">
          <Link to="/" className="text-xl font-bold text-blue-600">JobSearch</Link>
          <span className="text-gray-300">·</span>
          <span className="text-sm font-semibold text-gray-700">Seguimiento</span>
          <Link to="/" className="text-xs text-gray-500 hover:text-blue-500 transition-colors ml-auto">
            ← Vacantes
          </Link>
          <Link to="/analytics" className="text-xs text-gray-500 hover:text-blue-500 transition-colors">
            Analytics →
          </Link>
        </div>
      </header>

      {/* Contenido */}
      <div className="max-w-7xl mx-auto w-full px-4 py-6 flex gap-6 items-start">

        {/* Columnas */}
        <div className={`grid gap-4 transition-all duration-300 ${selected ? 'w-[58%] shrink-0 grid-cols-3' : 'w-full grid-cols-3'}`}>
          {COLUMNS.map(({ status, label, color, dot }) => {
            const col = columns[status]
            return (
              <div key={status} className={`bg-white rounded-xl border-t-4 ${color} shadow-sm flex flex-col`}>

                {/* Cabecera de columna */}
                <div className="px-4 py-3 flex items-center gap-2 border-b border-gray-100">
                  <span className={`w-2 h-2 rounded-full ${dot}`} />
                  <span className="text-sm font-semibold text-gray-700">{label}</span>
                  {!col.loading && (
                    <span className="ml-auto text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                      {col.total}
                    </span>
                  )}
                </div>

                {/* Lista */}
                <div className="flex flex-col gap-2 p-3 flex-1">
                  {col.loading ? (
                    <div className="flex flex-col items-center justify-center py-12 gap-2">
                      <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                      <p className="text-xs text-gray-400">Cargando...</p>
                    </div>
                  ) : col.error ? (
                    <p className="text-xs text-red-500 text-center py-8">{col.error}</p>
                  ) : col.vacancies.length === 0 ? (
                    <p className="text-xs text-gray-400 text-center py-12">Sin vacantes</p>
                  ) : (
                    col.vacancies.map((v) => (
                      <div key={v.id} ref={(el) => { if (el) cardRefs.current.set(v.id, el) }}>
                        <VacancyCard
                          vacancy={v}
                          onClick={handleSelect}
                          isSelected={selected?.id === v.id}
                        />
                      </div>
                    ))
                  )}
                </div>

                {/* Paginación */}
                {!col.loading && col.lastPage > 1 && (
                  <div className="px-3 pb-3">
                    <ColumnPagination
                      page={col.page}
                      lastPage={col.lastPage}
                      onChange={(p) => handlePageChange(status, p)}
                    />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Detalle lateral */}
        {selected && (
          <div className="flex-1 sticky top-20">
            <VacancyDetail
              vacancy={selected}
              onClose={() => setSelected(null)}
              onStatusChange={handleStatusChange}
              onFilterCompany={() => {}}
              onFilterCity={() => {}}
            />
          </div>
        )}
      </div>
    </div>
  )
}

// ─── paginación inline por columna ────────────────────────────────────────────

function ColumnPagination({ page, lastPage, onChange }: {
  page: number
  lastPage: number
  onChange: (p: number) => void
}) {
  return (
    <div className="flex items-center justify-center gap-2">
      <button
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="text-xs text-gray-500 hover:text-blue-600 disabled:opacity-30 disabled:cursor-not-allowed px-2 py-1 rounded transition-colors"
      >
        ← Ant
      </button>
      <span className="text-xs text-gray-400">{page} / {lastPage}</span>
      <button
        onClick={() => onChange(page + 1)}
        disabled={page >= lastPage}
        className="text-xs text-gray-500 hover:text-blue-600 disabled:opacity-30 disabled:cursor-not-allowed px-2 py-1 rounded transition-colors"
      >
        Sig →
      </button>
    </div>
  )
}