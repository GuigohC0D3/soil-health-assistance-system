from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str  # obrigatório — defina no .env; nunca use um valor padrão em produção
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h
    LLM_API_BASE: str
    LLM_API_KEY: str
    LLM_MODEL: str

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]
