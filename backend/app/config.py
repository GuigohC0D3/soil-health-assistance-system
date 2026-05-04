from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str  # obrigatório — defina no .env; nunca use um valor padrão em produção
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24h

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]
