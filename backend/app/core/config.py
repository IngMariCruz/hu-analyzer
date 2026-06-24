from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    MAX_FILE_SIZE_MB: int = 10
    # Máximo de llamadas LLM por-HU concurrentes (orquestación híbrida, Story 1.5)
    LLM_MAX_CONCURRENCY: int = 5
    # Rate-limiting efímero del endpoint anónimo (Story 1.11); IP nunca se persiste
    RATE_LIMIT: str = "10/minute"
    # Base de datos de resultados/métricas sin identidad (Story 1.9)
    DATABASE_URL: str = "sqlite:///./hu_analyzer.db"
    # Auth del panel admin (Epic 3). Generar el hash con passlib/bcrypt; nunca el cliente.
    ADMIN_PASSWORD_HASH: str = ""
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
