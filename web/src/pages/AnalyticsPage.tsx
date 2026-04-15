import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAnalyticsStore } from '../store/analyticsStore'
import SummaryBar from '../components/analytics/SummaryBar'
import StatusBoard from '../components/analytics/StatusBoard'

export default function AnalyticsPage() {
  const { skills, companies, salaries, statusTimeline, loading, error, loadAll } = useAnalyticsStore()

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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Skills */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Skills más demandados</h2>
              {skills.length === 0 ? (
                <p className="text-sm text-gray-400">Sin datos — disponible después del ranking.</p>
              ) : (
                <div className="flex flex-col gap-2">
                  {skills.slice(0, 15).map((s) => (
                    <div key={s.skill} className="flex items-center gap-3">
                      <span className="text-sm text-gray-600 w-28 truncate">{s.skill}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(s.total / skills[0].total) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400 w-6 text-right">{s.total}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

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

            {/* Salarios */}
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 md:col-span-2">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Rangos salariales</h2>
              {salaries.length === 0 ? (
                <p className="text-sm text-gray-400">Sin datos — la mayoría de vacantes no publica salario.</p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {salaries.map((s, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg px-3 py-2">
                      <p className="text-xs text-gray-400">{s.modality}</p>
                      <p className="text-sm text-gray-700 font-medium truncate">{s.salary_range}</p>
                      <p className="text-xs text-gray-400">{s.total} vacantes</p>
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