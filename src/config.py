from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_USER: str
    DATABASE_NAME: str
    DATABASE_PASSWORD: str

    SECRET_KEY: str

    FIRST_ADMIN_EMAIL: str
    FIRST_ADMIN_PASSWORD: str

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str


CONFIG = Settings()
