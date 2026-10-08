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

    # Base de Datos PostgreSQL local (con fallback inteligente a SQLite)
    DATABASE_URL: str = "postgresql+pg8000://postgres:felipe@localhost:5432/transcriptor_db"

    # Credenciales IA (Tolerancia a fallos VACAS)
    DEEPSEEK_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Parámetros Fuzzy Matching
    FUZZY_THRESHOLD: float = 0.70  # Similitud mínima (70%) para auto-asignar responsable

    # Formatos de audio permitidos
    ALLOWED_AUDIO_EXTENSIONS: list[str] = [".mp3", ".wav", ".m4a", ".flac", ".ogg"]
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
