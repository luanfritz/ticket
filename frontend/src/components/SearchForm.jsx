import { useState } from 'react'

export function SearchForm({ onSearch }) {
  const [origin, setOrigin] = useState('GRU')
  const [destination, setDestination] = useState('REC')
  const [date, setDate] = useState('2026-03-10')
  const [program, setProgram] = useState('LATAM_PASS')

  const submit = (e) => {
    e.preventDefault()
    onSearch({ origin, destination, date, prefer_miles_program: program })
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>Buscar passagens</h2>
      <div className="grid">
        <input value={origin} onChange={(e) => setOrigin(e.target.value.toUpperCase())} placeholder="Origem" />
        <input value={destination} onChange={(e) => setDestination(e.target.value.toUpperCase())} placeholder="Destino" />
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <select value={program} onChange={(e) => setProgram(e.target.value)}>
          <option value="LATAM_PASS">LATAM Pass</option>
          <option value="SMILES">Smiles</option>
          <option value="TUDO_AZUL">TudoAzul</option>
        </select>
      </div>
      <button type="submit">Buscar</button>
    </form>
  )
}
