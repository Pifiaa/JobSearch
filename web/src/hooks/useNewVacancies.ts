import { useEffect, useState } from 'react'

const STORAGE_KEY = 'jobsearch_last_visit'

export function useNewVacancies() {
  const [lastVisit, setLastVisit] = useState<Date | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    const last = stored ? new Date(stored) : null
    setLastVisit(last)
    localStorage.setItem(STORAGE_KEY, new Date().toISOString())
  }, [])

  return { lastVisit }
}