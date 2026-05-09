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
│   ├── seed_demo.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── AppLayout.vue
│       │   ├── SoilGaugeChart.vue
│       │   ├── SoilRadarChart.vue
│       │   ├── HealthEvolutionChart.vue
│       │   └── SoilCoreViz.vue             # visualizador Munsell
│       ├── views/                          # 12 telas
│       ├── tests/
│       │   ├── setup.ts
│       │   ├── SoilCoreViz.spec.ts
│       │   ├── AssistantView.spec.ts
│       │   └── SimulatorView.spec.ts
│       ├── stores/          # auth, notifications (Pinia)
│       ├── router/          # Vue Router (rotas protegidas por JWT)
│       ├── services/        # axios com interceptors de auth
│       └── types/           # TypeScript types
├── CLAUDE.md                # contexto técnico para LLMs e desenvolvedores
├── APRESENTACAO.md          # roteiro de apresentação acadêmica
└── docker-compose.yml
```

---

## Como Rodar

### Pré-requisitos
- Docker e Docker Compose instalados
- Chave de API compatível com OpenAI (endpoint configurável)

### 1. Configurar ambiente

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edite `backend/.env` e preencha:
```env
SECRET_KEY=      # gere com: python -c "import secrets; print(secrets.token_hex(32))"
LLM_API_KEY=     # sua chave de API
LLM_API_BASE=    # endpoint (ex: https://api.openai.com/v1)
LLM_MODEL=       # modelo (ex: gpt-4o-mini)
```

### 2. Subir os containers

```bash
docker-compose up --build
```

As migrations rodam automaticamente na inicialização do backend.

### 3. Popular com dados de exemplo (opcional)

```bash
docker-compose exec backend python seed_demo.py
```

**Usuários do seed:**
| Email | Senha | Papel |
|-------|-------|-------|
| joao@exemplo.com | senha123 | Produtor Rural |
| maria@exemplo.com | senha123 | Técnico Agrícola |

### 4. Acessar

| Serviço | URL |
|---------|-----|
| Aplicação | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (Redoc) | http://localhost:8000/redoc |

---

## Testes

```bash
# Backend — 23 testes (unitários + integração)
docker-compose exec backend pytest tests/ -v

# Frontend — 11 testes (componentes + views)
docker-compose exec frontend npm run test
```

**Estratégia:**
- Backend usa SQLite em memória com `app.dependency_overrides` para isolar DB e autenticação
- Chamadas à IA são mockadas — nenhum teste faz chamada real de API
- Frontend mocka axios globalmente via `vi.mock`

---

## API — Endpoints

```
# Autenticação
POST   /api/auth/register
POST   /api/auth/login

# Propriedades
GET    /api/properties/
POST   /api/properties/
PUT    /api/properties/{id}
DELETE /api/properties/{id}

# Análises de Solo
GET    /api/analyses/              ?propriedade_id=
POST   /api/analyses/              (gera recomendações automaticamente)
GET    /api/analyses/{id}
PUT    /api/analyses/{id}
DELETE /api/analyses/{id}

# Recomendações
GET    /api/recommendations/       ?propriedade_id= &analise_id=

# Dashboard
GET    /api/dashboard/stats
GET    /api/dashboard/trends

# Simulador de Calagem
POST   /api/simulate/liming        {analise_id, dosagem_calcario, cultura}

# Assistente IA
POST   /api/assistant/chat         {message, property_id?}

# Usuário
GET    /api/users/me
PUT    /api/users/me
```

---

## Modelagem do Banco

```
users
  id, nome, email, hashed_password, role (produtor|tecnico|admin), ativo

propriedades
  id, nome, area_hectares, localizacao, cidade, estado, proprietario_id → users

analises_solo
  id, id_amostra, data_analise
  ph, materia_organica, fosforo, potassio, calcio, magnesio
  teor_argila    — g/kg, para interpretação de P por textura (Mehlich-1)
  cor_munsell    — ex: "10YR 3/2", para visualizador de perfil de solo
  observacoes, propriedade_id → propriedades

recomendacoes
  id, tipo, descricao, prioridade (alta|media|baixa), analise_id → analises_solo
```

---

## Interpretação de Fósforo por Textura (Embrapa Mehlich-1)

| Textura | Argila (g/kg) | P Baixo | P Adequado |
|---------|---------------|---------|------------|
| Arenosa | < 150 | < 10 mg/dm³ | > 20 mg/dm³ |
| Média | 150–350 | < 7 mg/dm³ | > 15 mg/dm³ |
| Argilosa | > 350 | < 4 mg/dm³ | > 8 mg/dm³ |

---

## Variáveis de Ambiente

**`backend/.env`**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saude_solo
SECRET_KEY=                          # obrigatório
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=                         # obrigatório
LLM_MODEL=gpt-4o-mini
```

**`frontend/.env`**
```env
VITE_API_URL=http://localhost:8000
```
