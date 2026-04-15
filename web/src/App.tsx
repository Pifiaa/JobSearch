import { BrowserRouter, Routes, Route } from 'react-router-dom'
import VacanciesPage from './pages/VacanciesPage'
import AnalyticsPage from './pages/AnalyticsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<VacanciesPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </BrowserRouter>
  )
}