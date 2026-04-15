import type { PaginatedResponse, Vacancy, VacancyFilters, VacancyStatus } from '../types'

const BASE_URL = '/api'

function buildQueryString(filters: VacancyFilters): string {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '' && value !== null) {
      params.append(key, String(value))
    }
  })

  return params.toString()
}

export async function fetchVacancies(
  filters: VacancyFilters = {}
): Promise<PaginatedResponse<Vacancy>> {
  const qs = buildQueryString(filters)
  const response = await fetch(`${BASE_URL}/vacancies${qs ? `?${qs}` : ''}`)

  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export async function updateVacancyStatus(id: number, status: VacancyStatus): Promise<Vacancy> {
  const response = await fetch(`${BASE_URL}/vacancies/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })

  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export async function triggerScraping(sourceId?: number): Promise<void> {
  const url = sourceId
    ? `${BASE_URL}/scraper/run/${sourceId}`
    : `${BASE_URL}/scraper/run/all`

  const response = await fetch(url, { method: 'POST' })

  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }
}