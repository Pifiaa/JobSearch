import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useVacancyStore } from '../../store/vacancyStore'
import type { VacancyModality, VacancyStatus, VacancySort } from '../../types'

export default function VacancyFilters() {
  const { filters, setFilters } = useVacancyStore()
  const [searchParams, setSearchParams] = useSearchParams()
  const [search, setSearch] = useState(filters.search ?? '')

  // Sincronizar URL → store al montar
  useEffect(() => {
    const params: Partial<typeof filters> = {}
    if (searchParams.get('search'))   params.search   = searchParams.get('search')!
    if (searchParams.get('city'))     params.city     = searchParams.get('city')!
    if (searchParams.get('modality')) params.modality = searchParams.get('modality') as VacancyModality
    if (searchParams.get('status'))   params.status   = searchParams.get('status') as VacancyStatus
    if (searchParams.get('sort'))     params.sort     = searchParams.get('sort') as VacancySort
    if (searchParams.get('score_min')) params.score_min = Number(searchParams.get('score_min'))
    if (Object.keys(params).length > 0) {
      if (params.search) setSearch(params.search)
      setFilters(params)
    }
  }, [])

  function updateFilters(newFilters: Partial<typeof filters>) {
    const merged = { ...filters, ...newFilters }
    const params: Record<string, string> = {}
    if (merged.search)    params.search    = merged.search
    if (merged.city)      params.city      = merged.city
    if (merged.modality)  params.modality  = merged.modality
    if (merged.status)    params.status    = merged.status
    if (merged.sort)      params.sort      = merged.sort
    if (merged.score_min) params.score_min = String(merged.score_min)
    setSearchParams(params, { replace: true })
    setFilters(newFilters)
  }

  function handleSearchKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') updateFilters({ search: search || undefined })
  }

  function handleClear() {
    setSearch('')
    setSearchParams({}, { replace: true })
    setFilters({ search: undefined, city: undefined, modality: undefined, status: undefined, score_min: undefined, sort: undefined })
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex flex-wrap gap-3 items-center">
      <input
        type="text"
        placeholder="🔍 Buscar título o skill..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onKeyDown={handleSearchKeyDown}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />

      <input
        type="text"
        placeholder="Ciudad"
        value={filters.city ?? ''}
        onChange={(e) => updateFilters({ city: e.target.value || undefined })}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-32 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />

      <select
        value={filters.modality ?? ''}
        onChange={(e) => updateFilters({ modality: (e.target.value as VacancyModality) || undefined })}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Modalidad</option>
        <option value="presencial">Presencial</option>
        <option value="hibrido">Híbrido</option>
        <option value="remoto_colombia">Remoto CO</option>
        <option value="remoto_internacional">Remoto INT</option>
      </select>

      <select
        value={filters.status ?? ''}
        onChange={(e) => updateFilters({ status: (e.target.value as VacancyStatus) || undefined })}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Estado</option>
        <option value="nueva">Nueva</option>
        <option value="guardada">Guardada</option>
        <option value="postulada">Postulada</option>
        <option value="descartada">Descartada</option>
        <option value="observada">Observada</option>
        <option value="no_idoneo">No idóneo</option>
      </select>

      <select
        value={filters.sort ?? 'recent'}
        onChange={(e) => updateFilters({ sort: e.target.value as VacancySort })}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="recent">Más recientes</option>
        <option value="score">Mayor score</option>
        <option value="company">Empresa A-Z</option>
      </select>

      <input
        type="number"
        placeholder="Score mín."
        value={filters.score_min ?? ''}
        onChange={(e) => updateFilters({ score_min: e.target.value ? Number(e.target.value) : undefined })}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-28 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        min={0}
        max={100}
      />

      <button
        onClick={handleClear}
        className="text-sm text-gray-400 hover:text-red-500 transition-colors"
      >
        Limpiar
      </button>
    </div>
  )
}