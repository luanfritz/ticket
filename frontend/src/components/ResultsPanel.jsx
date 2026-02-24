const currency = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL'
})

const dateTime = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
})

const buildOfferUrl = (option) => {
  const query = new URLSearchParams({
    from: option.origin,
    to: option.destination,
    depart: option.departure_at,
    airline: option.airline
  })
  return `https://www.google.com/travel/flights?${query.toString()}`
}

function OptionCard({ item, rank }) {
  const { option } = item

  return (
    <article className="offer-card">
      <div className="offer-head">
        <span className="offer-rank">#{rank}</span>
        <strong>{option.airline}</strong>
        <span className={`badge badge-${item.risk_level.toLowerCase()}`}>{item.risk_level}</span>
      </div>

      <div className="offer-grid">
        <p><small>Rota</small><br />{option.origin} → {option.destination}</p>
        <p><small>Preço</small><br />{currency.format(option.cash_price_brl)}</p>
        <p><small>Milhas</small><br />{option.miles_price ? option.miles_price.toLocaleString('pt-BR') : 'N/A'}</p>
        <p><small>Score</small><br />{item.score}</p>
        <p><small>Partida</small><br />{dateTime.format(new Date(option.departure_at))}</p>
        <p><small>Chegada</small><br />{dateTime.format(new Date(option.arrival_at))}</p>
      </div>

      <div className="offer-actions">
        <a href={buildOfferUrl(option)} target="_blank" rel="noreferrer" className="button-link">
          Ir para oferta
        </a>
        <span className="offer-source">Fonte: {option.source}</span>
      </div>
    </article>
  )
}

export function ResultsPanel({ result }) {
  if (!result) return null

  return (
    <section className="card">
      <h2>Recomendação inteligente</h2>
      <p><strong>Estratégia:</strong> {result.strategic_recommendation.strategy}</p>
      <p>{result.strategic_recommendation.reason}</p>

      <div className="highlights">
        {result.recommended_best_cash && (
          <div className="highlight-box">
            <small>Melhor em dinheiro</small>
            <strong>{result.recommended_best_cash.option.airline}</strong>
            <span>{currency.format(result.recommended_best_cash.option.cash_price_brl)}</span>
          </div>
        )}
        {result.recommended_best_miles && (
          <div className="highlight-box">
            <small>Melhor em milhas</small>
            <strong>{result.recommended_best_miles.option.airline}</strong>
            <span>{result.recommended_best_miles.option.miles_price?.toLocaleString('pt-BR')} milhas</span>
          </div>
        )}
      </div>

      <h3>Top ofertas</h3>
      <div className="offers-list">
        {result.ranked_options.slice(0, 5).map((item, idx) => (
          <OptionCard key={item.option.id} item={item} rank={idx + 1} />
        ))}
      </div>

      {result.split_ticket_suggestions.length > 0 && (
        <>
          <h3>Split tickets sugeridos</h3>
          <div className="offers-list">
            {result.split_ticket_suggestions.map((item, idx) => (
              <OptionCard key={item.option.id} item={item} rank={idx + 1} />
            ))}
          </div>
        </>
      )}
    </section>
  )
}
