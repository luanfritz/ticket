import { useState } from 'react'
import { SearchForm } from './components/SearchForm'
import { ResultsPanel } from './components/ResultsPanel'
import { PromotionManager } from './components/PromotionManager'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export function App() {
  const [result, setResult] = useState(null)

  const onSearch = async (query) => {
    const params = new URLSearchParams(query)
    const res = await fetch(`${API_BASE}/api/v1/search?${params.toString()}`)
    const data = await res.json()
    setResult(data)
  }

  return (
    <main className="container">
      <h1>Smart Fare Engine</h1>
      <p>Painel de busca, decisão e promoções.</p>
      <SearchForm onSearch={onSearch} />
      <ResultsPanel result={result} />
      <PromotionManager apiBase={API_BASE} />
      <section className="card">
        <h2>Alert Checker</h2>
        <p>Use o endpoint <code>/api/v1/alerts/check</code> para validar alertas por preço atual.</p>
      </section>
    </main>
  )
}
