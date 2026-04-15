export interface SummaryData {
  total: number
  by_modality: { modality: string; total: number }[]
  by_source: { source: string; total: number }[]
  new_since: number | null
}

export interface SkillData {
  skill: string
  total: number
}

export interface CompanyData {
  company: string
  total: number
}

export interface SalaryData {
  modality: string
  salary_range: string
  total: number
}

export interface StatusTimelineData {
  by_status: { status: string; total: number }[]
  timeline: { status: string; date: string; total: number }[]
}

const BASE_URL = '/api/analytics'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}

const STORAGE_KEY = 'jobsearch_last_visit'

export function fetchSummary() {
  const lastVisit = localStorage.getItem(STORAGE_KEY)
  localStorage.setItem(STORAGE_KEY, new Date().toISOString())
  const qs = lastVisit ? `?last_visit=${encodeURIComponent(lastVisit)}` : ''
  return get<SummaryData>(`/summary${qs}`)
}

export const fetchSkills        = () => get<SkillData[]>('/skills')
export const fetchCompanies     = () => get<CompanyData[]>('/companies')
export const fetchSalaries      = () => get<SalaryData[]>('/salaries')
export const fetchStatusTimeline = () => get<StatusTimelineData>('/status-timeline')