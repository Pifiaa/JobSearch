import { useEffect, useState, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useVacancyStore } from '../store/vacancyStore'
import { triggerScraping } from '../api/vacancies'
import { useKeyboard } from '../hooks/useKeyboard'
import VacancyCard from '../components/vacancy/VacancyCard'
import VacancyFilters from '../components/vacancy/VacancyFilters'
import VacancyDetail from '../components/vacancy/VacancyDetail'
import Pagination from '../components/ui/Pagination'
import SummaryBar from '../components/analytics/SummaryBar'
import type { Vacancy } from '../types'

export default function VacanciesPage() {
  const { vacancies, loading, error, loadVacancies, pagination, updateVacancy, setFilters } = useVacancyStore()
  const [selected, setSelected] = useState<Vacancy | null>(null)
  const [scraping, setScraping] = useState(false)
  const [scraped, setScraped] = useState(false)
  const cardRefs = useRef<Map<number, HTMLDivElement>>(new Map())

  useEffect(() => {
    loadVacancies()
  }, [])

  function handleSelect(vacancy: Vacancy) {
    setSelected((prev) => prev?.id === vacancy.id ? null : vacancy)
  }

  function handleStatusChange(updated: Vacancy) {
    updateVacancy(updated)
    setSelected(updated)
  }

  function handleFilterCompany(company: string) {
    setSelected(null)
    setFilters({ search: company })
  }

  function handleFilterCity(city: string) {
    setSelected(null)
    setFilters({ city })
  }

  const navigateVacancy = useCallback((direction: 'up' | 'down') => {
    if (!selected) return
    const idx = vacancies.findIndex((v) => v.id === selected.id)
    if (idx === -1) return
    const next = direction === 'down' ? vacancies[idx + 1] : vacancies[idx - 1]
    if (!next) return
    setSelected(next)
    cardRefs.current.get(next.id)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [selected, vacancies])

  useKeyboard({
    Escape:    () => setSelected(null),
    ArrowDown: () => navigateVacancy('down'),
    ArrowUp:   () => navigateVacancy('up'),
  })

  async function handleScrape() {
    setScraping(true)
    setScraped(false)
    try {
      await triggerScraping()
      setScraped(true)
    } finally {
      setScraping(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold text-blue-600">JobSearch</span>
            <Link to="/analytics" className="text-xs text-gray-600 font-medium hover:text-blue-500 transition-colors">
              Analytics →
            </Link>
            {pagination && (
              <span className="text-xs text-gray-600 font-medium bg-gray-100 px-2 py-0.5 rounded-full">
                {pagination.total} vacantes
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {scraped && (
              <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                ✓ Scraping encolado
              </span>
            )}
            <button
              onClick={handleScrape}
              disabled={scraping}
              className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium"
            >
              {scraping ? '⏳ Iniciando...' : '⚡ Scraping'}
            </button>
          </div>
        </div>
        <SummaryBar />
      </header>

      <div className="max-w-7xl mx-auto w-full px-4 py-6 flex gap-6 items-start">
        <div className={`flex flex-col gap-4 transition-all duration-300 ${selected ? 'w-[42%] shrink-0' : 'w-full'}`}>
          <VacancyFilters />

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-xl px-4 py-3">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-2">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-400">Cargando vacantes...</p>
            </div>
          ) : vacancies.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-400 text-sm">Sin resultados para los filtros aplicados.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {vacancies.map((v) => (
                <div key={v.id} ref={(el) => { if (el) cardRefs.current.set(v.id, el) }}>
                  <VacancyCard
                    vacancy={v}
                    onClick={handleSelect}
                    isSelected={selected?.id === v.id}
                  />
                </div>
              ))}
            </div>
          )}

          <Pagination />
        </div>

        {selected && (
          <div className="flex-1 sticky top-20">
            <VacancyDetail
              vacancy={selected}
              onClose={() => setSelected(null)}
              onStatusChange={handleStatusChange}
              onFilterCompany={handleFilterCompany}
              onFilterCity={handleFilterCity}
            />
          </div>
        )}
      </div>
    </div>
  )
}