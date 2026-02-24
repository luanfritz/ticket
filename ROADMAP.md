# 🧭 Visão Geral do Projeto — Motor Inteligente de Busca de Passagens

## Objetivo Final
Criar um **motor inteligente de busca de passagens** que combina:

- 💰 Dinheiro
- 💳 Milhas
- ✈️ Trechos separados
- 🔥 Promoções
- 🧠 Algoritmo de decisão

---

## 🥇 Fase 1 — Fundação Técnica (Semanas 1–3)
### 🎯 Objetivo
Construir o MVP funcional utilizando APIs oficiais.

### ✅ Entregas
- Definir stack principal (**Python + FastAPI** recomendado)
- Criar backend base
- Integrar API de voos (ex.: **Amadeus for Developers**)
- Expor endpoint de busca com parâmetros:
  - origem
  - destino
  - data
- Retornar lista de voos com preço

### 🧠 Resultado esperado
Um buscador básico e funcional para pesquisa de passagens.

---

## 🥈 Fase 2 — Motor Inteligente de Comparação (Semanas 4–6)
### 🎯 Objetivo
Evoluir de “lista de voos” para “melhor decisão recomendada”.

### ✅ Entregas
- Implementar cálculo de:
  - preço real
  - tempo total da viagem
  - número de conexões
- Criar score interno de decisão

Exemplo de lógica:

```text
Score = preço + (tempo × peso_tempo) + (conexões × penalidade_conexão)
```

- Rankear resultados
- Retornar "Melhor opção recomendada"

### 🧠 Resultado esperado
O sistema passa a oferecer recomendações inteligentes, não apenas listagem.

---

## 🥉 Fase 3 — Comparação Dinheiro vs Milhas (Semanas 7–10)
### 🎯 Objetivo
Adicionar diferencial estratégico com análise de valor de milhas.

### ✅ Entregas
- Criar base de programas de milhas:
  - LATAM Pass
  - Smiles
  - TudoAzul
- Criar estimativa média de valor da milha
- Calcular:

```text
Valor real da milha = (preço em dinheiro - taxas) ÷ milhas exigidas
```

- Comparar emissão por dinheiro vs milhas
- Destacar melhor escolha para o usuário

### 🧠 Resultado esperado
Plataforma se torna um comparador estratégico de emissão.

---

## 🏅 Fase 4 — Combinação de Trechos (Semanas 11–14)
### 🎯 Objetivo
Detectar economias ocultas por composição de trechos.

### ✅ Entregas
- Buscar rota direta **A → C**
- Buscar rota segmentada **A → B** e **B → C**
- Calcular combinações e custo total
- Verificar tempo mínimo de conexão
- Filtrar opções de risco elevado

Lógica base:

```python
if (preco_A_B + preco_B_C) < preco_A_C:
    sugerir_combinacao()
```

### 🧠 Resultado esperado
Sistema encontra oportunidades que buscadores tradicionais frequentemente não exibem.

---

## 🏆 Fase 5 — Motor de Promoções (Semanas 15–18)
### 🎯 Objetivo
Transformar a plataforma em radar ativo de oportunidades.

### ✅ Entregas
- Criar crawler para monitoramento de promoções
- Monitorar sites/fontes de ofertas
- Extrair e estruturar dados:
  - rota
  - datas
  - preço
- Armazenar no banco de dados
- Cruzar promoções com buscas dos usuários

### 🧠 Resultado esperado
Sistema passa a antecipar oportunidades e não apenas reagir à consulta.

---

## 🧠 Fase 6 — Inteligência Avançada (Opcional / Nível Startup)
### Evoluções possíveis
- 🔔 Alertas personalizados
- 🤖 Machine Learning para prever queda de preço
- 📊 Histórico de variação tarifária
- 🧮 Simulação de transferência bonificada de pontos
- 🌎 Motor multi-cidade automático

---

## 💰 Estratégia de Monetização (Paralela)
Pode iniciar já na Fase 2 com:

- Afiliados (Decolar, Booking, Expedia)
- Redirecionamento com comissão
- Plano premium com alertas e recursos avançados

---

## 🧱 Arquitetura Recomendada
- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL
- **Cache e filas:** Redis
- **Infraestrutura:** Docker + VPS/AWS
- **Frontend:** React ou Next.js

---

## 📅 Linha do Tempo Realista
| Fase | Tempo médio |
|---|---|
| Fase 1 | 3 semanas |
| Fase 2 | 2–3 semanas |
| Fase 3 | 3 semanas |
| Fase 4 | 3 semanas |
| Fase 5 | 3 semanas |

**Total estimado:** ~4 meses para um produto robusto.
