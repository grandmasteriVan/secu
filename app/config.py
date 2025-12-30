from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    # Додаємо це поле, щоб Pydantic його прийняв
    OPENAI_API_KEY: str = "" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Це дозволить ігнорувати будь-які інші змінні в .env
    )

settings = Settings()
