import type { TailoredCv } from '../types'

const BASE_URL = '/api'

export async function generateTailoredCv(vacancyId: number): Promise<TailoredCv> {
  const response = await fetch(`${BASE_URL}/vacancies/${vacancyId}/tailor-cv`, {
    method: 'POST',
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.error ?? `Error ${response.status}: ${response.statusText}`)
  }
  const result: { tailored_cv: TailoredCv } = await response.json()
  return result.tailored_cv
}

export function tailoredCvPdfUrl(vacancyId: number): string {
  return `${BASE_URL}/vacancies/${vacancyId}/tailor-cv/pdf`
}

export function tailoredCvBriefUrl(vacancyId: number): string {
  return `${BASE_URL}/vacancies/${vacancyId}/tailor-cv/brief`
}
