# Smart Fare Engine

Projeto full-stack para busca inteligente de passagens com dinheiro, milhas, combinações de trechos e promoções.

## O que já está implementado

### Backend (FastAPI)
- Busca inteligente de voos: `GET /api/v1/search`
- Ranking por score (preço + tempo + conexões)
- Melhor estratégia automática (`SPLIT_TICKET`, `MILES`, `CASH`, `NO_OPTIONS`)
- Sugestões de split-ticket com filtro de risco
- CRUD básico de promoções em SQLite
- Alertas de preço em SQLite
- Histórico de tarifas por rota (registrado em buscas)
- Forecast simples de tarifa por rota
- Simulador de transferência bonificada
- Recomendação multi-cidade básica

### Frontend (React + Vite)
- Formulário de busca
- Exibição de recomendação estratégica e top resultados
- Painel para cadastrar/listar promoções

## Rodando localmente (backend)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse: `http://localhost:8000/docs`

## Rodando localmente (frontend)

```bash
cd frontend
npm install
npm run dev
```

Frontend em `http://localhost:5173`.

> Em Docker Compose o frontend já aponta para `http://api:8000`.

## Docker

```bash
docker compose up --build
```

## Integração Amadeus (opcional)

Para usar busca real de ofertas via Amadeus Self-Service API, configure:

```bash
export AMADEUS_API_KEY="seu_api_key"
export AMADEUS_API_SECRET="seu_api_secret"
```

Sem essas variáveis o provider da Amadeus é ignorado e o sistema segue com provider mock local.


## Scraping multi-site (opcional)

Foi adicionado um provider de scraping com cobertura de metabuscadores e cias aéreas (Google Flights, Kayak, Skyscanner, Decolar, ViajaNet, 123Milhas, LATAM, GOL e Azul).

Por padrão ele fica **desligado** para evitar bloqueios/rate-limit em ambientes de teste. Para ativar:

```bash
export ENABLE_WEB_SCRAPING=true
# opcionais
export WEB_SCRAPING_TIMEOUT_SECONDS=3
export WEB_SCRAPING_MAX_SOURCES=9
```

> Observação: alguns sites têm rendering por JavaScript e anti-bot, então a captura é best-effort e pode retornar zero resultados em alguns cenários.

## Endpoints principais

- `GET /health`
- `GET /api/v1/search`
- `POST /api/v1/promotions`
- `GET /api/v1/promotions`
- `POST /api/v1/alerts`
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/check?route=AAA-BBB&price_brl=999`
- `GET /api/v1/history/{route}`
- `GET /api/v1/forecast/{route}`
- `POST /api/v1/simulate/transfer-bonus`
- `POST /api/v1/multicity/recommendation`

## Testes

```bash
pytest -q
```
