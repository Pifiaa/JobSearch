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

function parseVacancy(vacancy: Vacancy): Vacancy {
  if (typeof vacancy.cv_keywords_detail === 'string') {
    try {
      vacancy.cv_keywords_detail = JSON.parse(vacancy.cv_keywords_detail)
    } catch {
      vacancy.cv_keywords_detail = null
    }
  }
  return vacancy
}

export async function fetchVacancies(
  filters: VacancyFilters = {}
): Promise<PaginatedResponse<Vacancy>> {
  const qs = buildQueryString(filters)
  const response = await fetch(`${BASE_URL}/vacancies${qs ? `?${qs}` : ''}`)
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`)
  }
  const result: PaginatedResponse<Vacancy> = await response.json()
  result.data = result.data.map(parseVacancy)
  return result
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
  return parseVacancy(await response.json())
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