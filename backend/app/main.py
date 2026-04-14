from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, properties, soil_analyses, recommendations, dashboard

app = FastAPI(
    title="Sistema de Assistência à Saúde do Solo",
    description="API para gestão de análises de solo e recomendações de manejo agrícola",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(users.router, prefix="/api/users", tags=["Usuários"])
app.include_router(properties.router, prefix="/api/properties", tags=["Propriedades"])
app.include_router(soil_analyses.router, prefix="/api/analyses", tags=["Análises de Solo"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recomendações"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/api/health", tags=["Status"])
def health_check():
    return {"status": "ok", "message": "Sistema de Saúde do Solo funcionando"}
