export type VacancyModality =
  | 'presencial'
  | 'hibrido'
  | 'remoto_colombia'
  | 'remoto_internacional'

export type VacancyStatus =
  | 'nueva'
  | 'guardada'
  | 'postulada'
  | 'descartada'
  | 'observada'
  | 'no_idoneo'

export type VacancySort = 'recent' | 'score' | 'company'

export interface Source {
  id: number
  name: string
}

export interface KeywordsDetail {
  matched: string[]
  missing: string[]
}

export interface Vacancy {
  id: number
  source_id: number
  source?: Source
  title: string
  company: string | null
  city: string | null
  department: string | null
  country: string | null
  modality: VacancyModality
  salary_range: string | null
  description: string | null
  url: string
  cv_score: number | null
  cv_score_semantic: number | null
  cv_keywords_detail: KeywordsDetail | null
  status: VacancyStatus
  status_changed_at: string | null
  published_at: string | null
  scraped_at: string
}

export interface PaginatedResponse<T> {
  current_page: number
  data: T[]
  last_page: number
  per_page: number
  total: number
}

export interface VacancyFilters {
  source_id?: number
  modality?: VacancyModality
  city?: string
  score_min?: number
  status?: VacancyStatus
  search?: string
  sort?: VacancySort
  per_page?: number
  page?: number
}

export interface StatusHistoryEntry {
  id: number
  vacancy_id: number
  status: VacancyStatus
  changed_at: string
}