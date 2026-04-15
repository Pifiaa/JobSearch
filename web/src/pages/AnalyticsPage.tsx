import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAnalyticsStore } from '../store/analyticsStore'
import SummaryBar from '../components/analytics/SummaryBar'
import StatusBoard from '../components/analytics/StatusBoard'

export default function AnalyticsPage() {
  const { companies, statusTimeline, loading, error, loadAll } = useAnalyticsStore()

  useEffect(() => {
    loadAll()
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link to="/" className="text-xl font-bold text-blue-600 hover:text-blue-700 transition-colors">
            JobSearch
          </Link>
          <span className="text-gray-300">/</span>
          <span className="text-sm text-gray-500 font-medium">Analytics</span>
        </div>
        <SummaryBar />
      </header>

      <main className="max-w-7xl mx-auto w-full px-4 py-6 flex flex-col gap-6">
        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-xl px-4 py-3">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-2">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-400">Cargando analytics...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
            {/* Empresas */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Empresas más activas</h2>
              {companies.length === 0 ? (
                <p className="text-sm text-gray-400">Sin datos.</p>
              ) : (
                <div className="flex flex-col gap-2">
                  {companies.slice(0, 15).map((c) => (
                    <div key={c.company} className="flex items-center gap-3">
                      <span className="text-sm text-gray-600 w-40 truncate">{c.company}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-purple-500 h-2 rounded-full"
                          style={{ width: `${(c.total / companies[0].total) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-6 text-right">{c.total}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Status timeline */}
            {statusTimeline && <StatusBoard data={statusTimeline} />}
          </div>
        )}
      </main>
    </div>
  )
}