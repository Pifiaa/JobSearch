import { create } from 'zustand'
import { fetchVacancies } from '../api/vacancies'
import type { Vacancy, VacancyFilters, PaginatedResponse } from '../types'

interface VacancyState {
  vacancies: Vacancy[]
  pagination: Omit<PaginatedResponse<Vacancy>, 'data'> | null
  filters: VacancyFilters
  loading: boolean
  error: string | null

  setFilters: (filters: Partial<VacancyFilters>) => void
  loadVacancies: () => Promise<void>
  goToPage: (page: number) => void
  updateVacancy: (updated: Vacancy) => void
}

export const useVacancyStore = create<VacancyState>((set, get) => ({
  vacancies: [],
  pagination: null,
  filters: { per_page: 20, page: 1 },
  loading: false,
  error: null,

  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters, page: 1 },
    }))
    get().loadVacancies()
  },

  loadVacancies: async () => {
    set({ loading: true, error: null })
    try {
      const { data, ...pagination } = await fetchVacancies(get().filters)
      set({ vacancies: data, pagination, loading: false })
    } catch (e) {
      set({ error: (e as Error).message, loading: false })
    }
  },

  goToPage: (page) => {
    set((state) => ({ filters: { ...state.filters, page } }))
    get().loadVacancies()
  },

  updateVacancy: (updated) => {
    set((state) => ({
      vacancies: state.vacancies.map((v) => v.id === updated.id ? updated : v),
    }))
  },
}))