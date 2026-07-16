# Context Pack: soil-health-assistance-system

Path: /Users/seunome/Code/soil-health-assistance-system
Generated: 2026-07-11T23:03:19Z

## Directory tree (depth 3, filtered)
```
.
./.DS_Store
./frontend
./.ruff_cache
./almostglobal-results.sarif
./FALA_APRESENTACAO.md
./.claude
./backend
./.fable-review
./README.md
./mypy.ini
./.gitignore
./docker-compose.yml
./APRESENTACAO.md
./CLAUDE.md
./frontend/tsconfig.node.json
./frontend/index.html
./frontend/.DS_Store
./frontend/Dockerfile
./frontend/package-lock.json
./frontend/package.json
./frontend/.env
./frontend/tsconfig.json
./frontend/.env.example
./frontend/vite.config.ts
./frontend/src
./.ruff_cache/CACHEDIR.TAG
./.ruff_cache/0.15.12
./.ruff_cache/.gitignore
./.claude/settings.local.json
./backend/.DS_Store
./backend/app
./backend/requirements.txt
./backend/.pytest_cache
./backend/alembic.ini
./backend/Dockerfile
./backend/tests
./backend/mypy.ini
./backend/seed.py
./backend/.env
./backend/alembic
./backend/.env.example
./backend/test.db
./backend/seed_demo.py
./.fable-review/CONTEXT_PACK.md
./frontend/src/App.vue
./frontend/src/types
./frontend/src/composables
./frontend/src/main.ts
./frontend/src/tests
./frontend/src/stores
./frontend/src/components
./frontend/src/vite-env.d.ts
./frontend/src/views
./frontend/src/assets
./frontend/src/services
./frontend/src/router
./.ruff_cache/0.15.12/11024922184768997205
./.ruff_cache/0.15.12/15013981346792244706
./.ruff_cache/0.15.12/3086530832850717678
./backend/app/routers
./backend/app/config.py
./backend/app/core
./backend/app/database.py
./backend/app/__init__.py
./backend/app/models
./backend/app/schemas
./backend/app/main.py
./backend/app/services
./backend/.pytest_cache/CACHEDIR.TAG
./backend/.pytest_cache/README.md
./backend/.pytest_cache/.gitignore
./backend/.pytest_cache/v
./backend/tests/test_simulator_router.py
./backend/tests/test_recommendation_service.py
./backend/tests/conftest.py
./backend/tests/test_assistant_router.py
./backend/tests/test_notifications_router.py
./backend/tests/__init__.py
./backend/tests/test_dashboard_router.py
./backend/tests/test_soil_analyses_router.py
./backend/alembic/script.py.mako
./backend/alembic/env.py
./backend/alembic/versions
```

## README
```
# Sistema de Assistência à Saúde do Solo

Sistema de Suporte à Decisão Agrônoma (DSS) para gestão de análises de solo e recomendações automáticas de manejo — com IA conversacional, simulador de calagem e visualização de perfil de solo.

Domínio: solos tropicais brasileiros (Cerrado/Latossolos), padrões Embrapa.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Vue 3 + TypeScript + Pinia + Vue Router + Chart.js |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.0 + Alembic |
| Banco | PostgreSQL 15 |
| IA | OpenAI SDK (compatível com qualquer endpoint OpenAI) |
| Infra | Docker Compose |
| Testes | pytest + pytest-mock (backend) · vitest + @vue/test-utils (frontend) |

---

## Funcionalidades

### Motor Agronômico
Cálculos determinísticos baseados em fórmulas Embrapa Cerrado — sem IA:
- Soma de Bases (SB), CTC estimada, Saturação de Bases (V%)
- Necessidade de Calagem pelo método da saturação de bases (PRNT 80%)
- Score de saúde do solo 0–100 por desvio normalizado
- Interpretação do fósforo por classe textural (Mehlich-1)

### Recomendações com IA
A IA recebe métricas já calculadas e gera recomendações técnicas em linguagem natural (até 5 por análise, ordenadas por prioridade).

### Simulador de Calagem
Simulação interativa "e se": o usuário ajusta a dosagem de calcário (t/ha) e o sistema calcula deterministicamente o novo V% e pH, depois gera uma narrativa agronômica para a cultura selecionada.

### Assistente Conversacional
Chat com os dados do próprio usuário. Perguntas como "qual propriedade tem o pior score?" ou "quando precisarei calcular novamente?" são respondidas com base no histórico completo de análises injetado no contexto da IA.

### Visualizador de Perfil Munsell
Conversão da notação Munsell (ex: `10YR 3/2`) para RGB real. Renderiza uma coluna visual de solo por camadas de análise — solos escuros indicam alta matéria orgânica.

### Relatórios e Exportação
- Radar chart de adequação nutricional por cultura
- Evolução temporal do score de saúde
- Exportação em PDF (html2canvas + jsPDF)
- Calculadora de custo de fertilizantes

---

## Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│  Vue 3 SPA (porta 5173)                                       │
│  Dashboard · Propriedades · Análises · Recomendações         │
│  Simulador · Assistente · Relatório · Fertilizantes          │
├──────────────────────────────────────────────────────────────┤
│  FastAPI (porta 8000)                                         │
│  JWT Auth · CRUD · Motor Agronômico · Simulador · Chat       │
│                                                               │
│  Padrão híbrido neuro-simbólico:                             │
│  → Python calcula toda a matemática (Embrapa)                │
│  → IA só narra resultados verificados                        │
├──────────────────────────────────────────────────────────────┤
│  PostgreSQL 15 (porta 5432)                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Pastas

```
soil-health-assistance-system/
├── backend/
│   ├── app/
│   │   ├── core/            # JWT, bcrypt, dependências FastAPI
│   │   ├── models/          # User, Property, SoilAnalysis, Recommendation
│   │   ├── routers/         # auth, users, properties, analyses,
│   │   │                    # recommendations, dashboard, notifications,
│   │   │                    # simulator, assistant
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── services/
│   │   │   ├── recommendation_service.py   # motor agronômico + LLM
│   │   │   ├── simulation_service.py       # simulador de calagem
│   │   │   └── assistant_service.py        # context stuffing + chat
│   │   ├── config.py        # Settings (Pydantic BaseSettings)
│   │   ├── database.py      # engine + sessão SQLAlchemy
│   │   └── main.py          # app FastAPI (9 routers)
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       ├── 002_add_clay_content.py     # teor_argila
│   │       └── 003_add_munsell.py          # cor_munsell
│   ├── tests/
│   │   ├── conftest.py                     # fixtures SQLite + mocks
│   │   ├── test_recommendation_service.py  # 19 testes unitários puros
│   │   ├── test_simulator_router.py        # 4 testes de integração
│   │   └── test_assistant_router.py        # 3 testes de integração
```

## Dependency manifest
```
```

## Git log (last 30 days)
```
c4d3171 Merge branch 'main' of https://github.com/GuigohC0D3/soil-health-assistance-system
8c2b4af docs: add presentation script
```

## Top churned files (last 30 days)
```
3 FALA_APRESENTACAO.md
```

## Top churned files content (capped 300 lines each)
### FALA_APRESENTACAO.md
```
Bom dia. Nós, Matheus, Mateus, Victor, Jesley, Lara e Guilherme, desenvolvemos este Sistema de Assistência à Saúde do Solo como MVP para a disciplina de Gerência e Manutenção de Software no ICEV. É um sistema de gestão de análises de solo para o Cerrado brasileiro, seguindo padrões Embrapa, com recomendações geradas automaticamente. Vou mostrar o sistema funcionando e depois explicar a arquitetura e o código. O João, produtor rural, faz login e cai no dashboard. Lá ele vê os totais de propriedades, análises, recomendações e alertas críticos, um medidor visual com o score de saúde do solo de zero a cem, a evolução do pH em gráfico de linhas, o ranking das propriedades e as últimas análises registradas. Ele vai em Propriedades, vê a lista, cadastra uma nova. Depois em Análises de Solo, registra uma análise com os dados do laboratório — pH, matéria orgânica, fósforo, potássio, cálcio, magnésio, teor de argila e cor Munsell. Na hora que salva, o sistema calcula tudo e gera recomendações priorizadas: calagem com prioridade alta porque o pH está baixo, adubação fosfatada com prioridade média. João vai na Calculadora de Fertilizantes, digita os preços cotados e vê o custo por hectare. Depois no Simulador de Calagem, arrasta um slider de dosagem de calcário e vê na hora como a saturação por bases e o pH reagem. Ele testa cenários, pergunta ao Assistente "O que limita a produtividade?" e recebe resposta com base nos dados reais. Por fim gera um Relatório PDF com gráfico radar, perfil de solo colorido, evolução temporal, tabela de resultados e recomendações. Tudo integrado e funcionando.

A arquitetura é de três camadas: Apresentação com Vue três e TypeScript, Aplicação com FastAPI e Python, Dados com PostgreSQL quinze. O backend usa SQLAlchemy e Pydantic para ORM e validação. O motor de recomendações está no arquivo `recommendation_service.py`: a função `calcular_metricas` calcula soma de bases, CTC, saturação V%, necessidade de calagem e score de saúde usando as fórmulas da Embrapa de forma determinística. A IA só entra para escrever o texto das recomendações — ela não faz conta, evitando alucinação de dosagem. Os thresholds de fósforo variam com o teor de argila seguindo a tabela Mehlich-um. O simulador implementa a fórmula V2 igual a V1 mais dose vezes PRNT sobre CTC e a correlação empírica do Raij para pH. O assistente usa context stuffing: envia todas as análises do usuário em JSON junto com a pergunta para o modelo. No frontend, o `SoilGaugeChart.vue` renderiza o medidor com SVG animado, o `SoilRadarChart.vue` desenha o radar de seis parâmetros com Chart.js, o `SoilCoreViz.vue` converte Munsell para RGB e desenha o perfil do solo. O `AppLayout.vue` tem a sidebar com oito itens de navegação e notificações. Documentamos nove decisões de design: arquitetura SPA mais API separados, FastAPI sobre Django, Vue três com Composition API e TypeScript, PostgreSQL relacional, migrações com Alembic, containerização com Docker, motor de recomendações no backend, segurança com JWT HS256 e bcrypt, e variáveis de ambiente sensíveis fora do Git. São trinta e quatro testes — vinte e três no backend com pytest e onze no frontend com vitest — cobrindo as fórmulas agronômicas, os endpoints e os componentes visuais. O repositório está no GitHub em GuigohC0D3/soil-health-assistance-system com trinta commits na main.
```

## Vault context (ClaudeBrain/Projects/soil-health-assistance-system.md)
```
# Soil Health Assistance System

**Repo:** `/Users/seunome/Code/soil-health-assistance-system`
**Stack:** Vue 3 + TypeScript (frontend) · FastAPI + SQLAlchemy 2.0 (backend) · PostgreSQL 15 · Docker Compose
**LLM:** OpenAI SDK → xiaomimimo.com (mimo-v2-flash)

---

## Architecture

- **Backend models:** User, Property, SoilAnalysis, Recommendation
- **Core logic:** `backend/app/services/recommendation_service.py` — Embrapa Cerrado agronomic formulas (SB, CTC, V%, lime requirement, health score 0–100)
- **10 frontend views:** Dashboard, Properties, SoilAnalysisForm, AnalysisHistory, Recommendations, Report (PDF), Fertilizer, Simulator, Assistant, Register/Login
- **Migrations:** Alembic, chain 001→002→003

---

## Session 1 — 2026-05-09 (Impressiveness Upgrade + Tests)

**What was done:**
- Fixed `~/.claude/settings.json` malformed JSON (two trailing commas breaking all hooks)
- Fixed claude-hud status bar (was disabled due to same JSON issue)
- Deep research on AgTech academic differentiation (Gemini deep research)
- Built SDD and shipped 4 new features with 3-person team over one weekend session:
  - **Feature 1:** P interpretation by clay texture — Embrapa Mehlich-1 matrix (`teor_argila` field, `_get_p_thresholds()`)
  - **Feature 2:** "What-If" Liming Simulator — deterministic Embrapa base saturation inverse formula + LLM narrative
  - **Feature 3:** Conversational Ag Assistant — JSON context stuffing (not RAG), full chat UI
  - **Feature 4:** Munsell Soil Core Visualizer — `munsell` npm package, RGB conversion, layered Vue component
- DB migrations 002 (teor_argila) and 003 (cor_munsell) applied cleanly
- Fixed missing `cor_munsell` / `teor_argila` in `frontend/src/types/index.ts`
- Created `backend/.env` and `frontend/.env` from examples + generated SECRET_KEY
- Wired real LLM API key (xiaomimimo)
- Full Docker stack running: db (healthy) + backend (port 8000) + frontend (port 5173)
- Added full test suite:
  - Backend: pytest + pytest-mock + httpx==0.23.3 (pinned for starlette 0.35 compat)
  - 22/23 tests passing; 23rd pending fix (empty message 422 — needs `Field(min_length=1)` in ChatRequest)
  - Frontend: vitest + @vue/test-utils + jsdom configured; spec files written for SoilCoreViz, AssistantView, SimulatorView

**Files changed:**
- `backend/app/models/soil_analysis.py` — added `teor_argila`, `cor_munsell`
- `backend/app/services/recommendation_service.py` — `_get_p_thresholds()`, clay-aware P desvio
- `backend/app/services/simulation_service.py` — NEW (liming simulator math + LLM)
- `backend/app/services/assistant_service.py` — NEW (context stuffing chat)
- `backend/app/routers/simulator.py` — NEW
- `backend/app/routers/assistant.py` — NEW (pending: add `Field(min_length=1)` to ChatRequest)
- `backend/app/main.py` — registered simulator + assistant routers
- `backend/alembic/versions/002_add_clay_content.py` — NEW
- `backend/alembic/versions/003_add_munsell.py` — NEW
- `backend/requirements.txt` — added pytest, pytest-mock, httpx==0.23.3
- `backend/tests/` — NEW: conftest.py, test_recommendation_service.py, test_simulator_router.py, test_assistant_router.py
- `frontend/src/views/SimulatorView.vue` — NEW
- `frontend/src/views/AssistantView.vue` — NEW
- `frontend/src/components/SoilCoreViz.vue` — NEW
- `frontend/src/types/index.ts` — added `teor_argila`, `cor_munsell` to interfaces
- `frontend/src/router/index.ts` — added /simulador, /assistente routes
- `frontend/src/components/AppLayout.vue` — added nav links
- `frontend/package.json` — added munsell, vitest, @vue/test-utils, jsdom
- `frontend/vite.config.ts` — added vitest test block
- `frontend/src/tests/` — NEW: setup.ts, SoilCoreViz.spec.ts, AssistantView.spec.ts, SimulatorView.spec.ts
- `backend/.env` — created (not committed)
- `frontend/.env` — created (not committed)

**Decisions:**
- Context stuffing over RAG for the chat assistant (structured tabular data, small scale, zero retrieval bugs)
- Hybrid neuro-symbolic architecture: deterministic Embrapa math → LLM narrates verified outputs only
- httpx pinned to 0.23.3 to maintain compatibility with starlette 0.35.x (fastapi 0.109.2)
- Munsell visualizer requires `cor_munsell` field to be manually entered in the soil analysis form

**Status:** Docker stack fully running. 22/23 backend tests pass. One fix pending: add `Field(min_length=1)` to `ChatRequest.message` in `backend/app/routers/assistant.py`. Frontend tests written but not yet run (need `npm install` in container).

**Blockers:** None — presentation is Monday 2026-05-11.

*→ [[index]]*
```
