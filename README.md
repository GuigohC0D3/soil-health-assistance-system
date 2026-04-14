# Sistema de Assistência à Saúde do Solo

MVP full stack para gestão de análises de solo e recomendações automáticas de manejo agrícola.

## Stack

- **Frontend:** Vue 3 + TypeScript + Pinia + Vue Router
- **Backend:** Python + FastAPI + SQLAlchemy
- **Banco:** PostgreSQL 15
- **Infra:** Docker Compose

---

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│  Apresentação    │  Vue 3 SPA (porta 5173)           │
├─────────────────────────────────────────────────────┤
│  Aplicação       │  FastAPI (porta 8000)             │
│                  │  JWT Auth │ CRUD │ Recomendações  │
├─────────────────────────────────────────────────────┤
│  Dados           │  PostgreSQL 15 (porta 5432)       │
└─────────────────────────────────────────────────────┘
```

## Estrutura de Pastas

```
soil-health-assistance-system/
├── backend/
│   ├── app/
│   │   ├── core/          # segurança (JWT, bcrypt) e dependências
│   │   ├── models/        # modelos SQLAlchemy
│   │   ├── routers/       # rotas FastAPI
│   │   ├── schemas/       # schemas Pydantic
│   │   ├── services/      # lógica de recomendações
│   │   ├── config.py      # configurações via .env
│   │   ├── database.py    # engine + sessão
│   │   └── main.py        # app FastAPI
│   ├── alembic/           # migrations
│   ├── seed.py            # dados de exemplo
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/    # AppLayout (sidebar + main)
│       ├── views/         # telas do sistema
│       ├── stores/        # Pinia (auth)
│       ├── router/        # Vue Router
│       ├── services/      # axios com interceptors
│       └── types/         # TypeScript types
├── docker-compose.yml
└── README.md
```

---

## Como Rodar com Docker (recomendado)

### 1. Copiar os arquivos de ambiente

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Subir os containers

```bash
docker-compose up --build
```

### 3. Rodar as migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Popular com dados de exemplo (opcional)

```bash
docker-compose exec backend python seed.py
```

### 5. Acessar

| Serviço    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:5173        |
| API Docs   | http://localhost:8000/docs   |
| Redoc      | http://localhost:8000/redoc  |

**Usuários do seed:**
- `joao@exemplo.com` / `senha123` (Produtor Rural)
- `maria@exemplo.com` / `senha123` (Técnico Agrícola)

---

## Como Rodar Localmente (sem Docker)

### Backend

```bash
cd backend

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar DATABASE_URL com suas credenciais PostgreSQL

# Rodar migrations
alembic upgrade head

# Seed (opcional)
python seed.py

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar .env
cp .env.example .env
# VITE_API_URL=http://localhost:8000

# Iniciar servidor de desenvolvimento
npm run dev
```

---

## Regras de Recomendação

As recomendações são geradas automaticamente ao registrar uma análise:

| Parâmetro        | Condição crítica      | Recomendação                            |
|------------------|-----------------------|-----------------------------------------|
| pH               | < 5.5                 | Correção com calcário                   |
| pH               | > 7.5                 | Avaliação de acidificação               |
| Matéria Orgânica | < 2.5%                | Incorporar composto/palhada             |
| Fósforo          | < 10 mg/dm³           | Adubação fosfatada (superfosfato)       |
| Potássio         | < 0.15 cmolc/dm³      | Adubação potássica (KCl / K₂SO₄)       |
| Cálcio           | < 2.0 cmolc/dm³       | Calcário calcítico ou gesso agrícola    |
| Magnésio         | < 0.5 cmolc/dm³       | Calcário dolomítico                     |
| Múltiplos baixos | ≥ 3 fatores críticos  | Programa integrado de recuperação       |

---

## API — Endpoints Principais

```
POST   /api/auth/register       Cadastrar usuário
POST   /api/auth/login          Login → token JWT

GET    /api/properties/         Listar propriedades
POST   /api/properties/         Criar propriedade
PUT    /api/properties/{id}     Atualizar propriedade
DELETE /api/properties/{id}     Excluir propriedade

GET    /api/analyses/           Listar análises (filtro: ?propriedade_id=)
POST   /api/analyses/           Registrar análise (gera recomendações)
GET    /api/analyses/{id}       Detalhe de uma análise
PUT    /api/analyses/{id}       Atualizar análise (regera recomendações)
DELETE /api/analyses/{id}       Excluir análise

GET    /api/recommendations/    Listar recomendações (filtros disponíveis)

GET    /api/users/me            Dados do usuário logado
PUT    /api/users/me            Atualizar dados do usuário
```

Documentação interativa completa em `/docs` (Swagger UI).

---

## Modelagem do Banco

```
users
  id, nome, email, hashed_password, papel (produtor|tecnico|admin),
  ativo, criado_em, atualizado_em

propriedades
  id, nome, area_hectares, localizacao, cidade, estado,
  proprietario_id → users.id, criado_em, atualizado_em

analises_solo
  id, id_amostra, data_analise, ph, materia_organica, fosforo,
  potassio, calcio, magnesio, observacoes,
  propriedade_id → propriedades.id, criado_em, atualizado_em

recomendacoes
  id, tipo, descricao, prioridade (alta|media|baixa),
  analise_id → analises_solo.id, criado_em
```

---

## Variáveis de Ambiente

**backend/.env**

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saude_solo
SECRET_KEY=sua-chave-secreta-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**frontend/.env**

```env
VITE_API_URL=http://localhost:8000
```
