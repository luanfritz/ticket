export function ResultsPanel({ result }) {
  if (!result) return null

  return (
    <div className="card">
      <h2>Recomendação</h2>
      <p><strong>Estratégia:</strong> {result.strategic_recommendation.strategy}</p>
      <p>{result.strategic_recommendation.reason}</p>
      <h3>Melhores opções</h3>
      <ul>
        {result.ranked_options.slice(0, 5).map((item) => (
          <li key={item.option.id}>
            {item.option.airline} • R$ {item.option.cash_price_brl} • score {item.score}
          </li>
        ))}
      </ul>
      {result.split_ticket_suggestions.length > 0 && (
        <>
          <h3>Split tickets sugeridos</h3>
          <ul>
            {result.split_ticket_suggestions.map((item) => (
              <li key={item.option.id}>{item.option.airline} • R$ {item.option.cash_price_brl}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
