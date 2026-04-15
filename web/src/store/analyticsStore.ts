import { create } from 'zustand'
import {
  fetchSummary,
  fetchSkills,
  fetchCompanies,
  fetchSalaries,
  fetchStatusTimeline,
  type SummaryData,
  type SkillData,
  type CompanyData,
  type SalaryData,
  type StatusTimelineData,
} from '../api/analytics'

interface AnalyticsState {
  summary: SummaryData | null
  skills: SkillData[]
  companies: CompanyData[]
  salaries: SalaryData[]
  statusTimeline: StatusTimelineData | null
  loading: boolean
  error: string | null
  loadSummary: () => Promise<void>
  loadAll: () => Promise<void>
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
  summary: null,
  skills: [],
  companies: [],
  salaries: [],
  statusTimeline: null,
  loading: false,
  error: null,

  loadSummary: async () => {
    try {
      const summary = await fetchSummary()
      set({ summary })
    } catch (e) {
      set({ error: (e as Error).message })
    }
  },

  loadAll: async () => {
    set({ loading: true, error: null })
    try {
      const [summary, skills, companies, salaries, statusTimeline] = await Promise.all([
        fetchSummary(),
        fetchSkills(),
        fetchCompanies(),
        fetchSalaries(),
        fetchStatusTimeline(),
      ])
      set({ summary, skills, companies, salaries, statusTimeline, loading: false })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },
}))