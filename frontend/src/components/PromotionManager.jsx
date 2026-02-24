import { useState } from 'react'

export function PromotionManager({ apiBase }) {
  const [route, setRoute] = useState('GRU-REC')
  const [price, setPrice] = useState('499.9')
  const [items, setItems] = useState([])

  const createPromotion = async () => {
    await fetch(`${apiBase}/api/v1/promotions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        route,
        valid_from: '2026-03-01',
        valid_to: '2026-03-31',
        price_brl: Number(price),
        source: 'frontend',
        notes: 'promo cadastrada no painel'
      })
    })
    await loadPromotions()
  }

  const loadPromotions = async () => {
    const res = await fetch(`${apiBase}/api/v1/promotions?route=${route}`)
    const data = await res.json()
    setItems(data)
  }

  return (
    <div className="card">
      <h2>Promoções</h2>
      <div className="grid">
        <input value={route} onChange={(e) => setRoute(e.target.value.toUpperCase())} />
        <input value={price} onChange={(e) => setPrice(e.target.value)} />
      </div>
      <div className="row">
        <button onClick={createPromotion}>Salvar promoção</button>
        <button onClick={loadPromotions}>Listar promoções</button>
      </div>
      <ul>
        {items.map((p, idx) => (
          <li key={`${p.route}-${idx}`}>{p.route} • R$ {p.price_brl} • {p.source}</li>
        ))}
      </ul>
    </div>
  )
}
