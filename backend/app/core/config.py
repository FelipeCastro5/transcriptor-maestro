import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Transcriptor Maestro API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Directorio base del backend
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Rutas de almacenamiento
    UPLOAD_DIR: str = "storage/audios_temp"
    OUTPUT_DIR: str = "storage/salidas"

    # Base de Datos PostgreSQL (parametrizado sin credenciales hardcodeadas)
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "transcriptor_db"
    DATABASE_URL: str = ""

    def model_post_init(self, __context) -> None:
        if not self.DATABASE_URL:
            if self.DB_PASSWORD:
                self.DATABASE_URL = f"postgresql+pg8000://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            else:
                self.DATABASE_URL = f"postgresql+pg8000://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Normalizar para SQLAlchemy con driver puro pg8000
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
        elif self.DATABASE_URL.startswith("postgresql://") and not self.DATABASE_URL.startswith("postgresql+"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

    # Credenciales IA (Tolerancia a fallos VACAS)
    DEEPSEEK_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Parámetros Fuzzy Matching
    FUZZY_THRESHOLD: float = 0.70  # Similitud mínima (70%) para auto-asignar responsable

    # Formatos de audio y texto permitidos
    ALLOWED_AUDIO_EXTENSIONS: list[str] = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".txt"]
    MAX_AUDIO_SIZE_MB: int = 250

    @property
    def full_upload_path(self) -> Path:
        path = self.BASE_DIR / self.UPLOAD_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def full_output_path(self) -> Path:
        path = self.BASE_DIR / self.OUTPUT_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
