import { useVacancyStore } from '../../store/vacancyStore'

export default function Pagination() {
  const { pagination, filters, goToPage } = useVacancyStore()

  if (!pagination || pagination.last_page <= 1) return null

  const current = filters.page ?? 1

  return (
    <div className="flex items-center justify-between text-sm text-gray-600">
      <span>
        Página {current} de {pagination.last_page} — {pagination.total} vacantes
      </span>
      <div className="flex gap-2">
        <button
          onClick={() => goToPage(current - 1)}
          disabled={current === 1}
          className="px-3 py-1.5 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50"
        >
          ← Anterior
        </button>
        <button
          onClick={() => goToPage(current + 1)}
          disabled={current === pagination.last_page}
          className="px-3 py-1.5 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50"
        >
          Siguiente →
        </button>
      </div>
    </div>
  )
}