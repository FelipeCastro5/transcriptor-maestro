import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.base import Base
# Import all models so metadata knows about them
import app.db.models
from app.db.models.proyecto import Proyecto
from app.db.models.responsable import Responsable

def create_db_engine():
    try:
        # Intentar conectar a PostgreSQL
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=False
        )
        # Probar conexión real
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[DB] Conectado exitosamente a: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
        return engine
    except Exception as e:
        print(f"[DB-FALLBACK] No fue posible conectar al motor principal ({e}). Usando SQLite local.")
        sqlite_url = "sqlite:///./transcriptor.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Crea todas las tablas si no existen y siembra datos iniciales de prueba (Proyecto y Responsables).
    """
    Base.metadata.create_all(bind=engine)

    # Asegurar que la restricción CHECK en PostgreSQL soporte el estado 'CANCELADO'
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE reuniones DROP CONSTRAINT IF EXISTS reuniones_estado_proceso_check"))
            conn.execute(text("ALTER TABLE reuniones ADD CONSTRAINT reuniones_estado_proceso_check CHECK (estado_proceso IN ('EN_COLA', 'PROCESANDO', 'COMPLETADO', 'FALLIDO', 'CANCELADO'))"))
    except Exception:
        pass
    
    # Sembrar datos base si la tabla responsables está vacía
    db = SessionLocal()
    try:
        if db.query(Proyecto).count() == 0:
            proyecto_default = Proyecto(
                id="PROJ-DEFAULT",
                nombre="Transcriptor Maestro - Core",
                descripcion="Proyecto principal de seguimiento de acuerdos y control"
            )
            db.add(proyecto_default)
            db.commit()

        if db.query(Responsable).count() == 0:
            miembros_base = [
                {
                    "nombre_completo": "Juan Pérez",
                    "alias_conocidos": ["Juan", "Juancho", "Juna", "Pérez", "Juan P"],
                    "email": "juan.perez@empresa.com",
                    "rol": "Project Manager"
                },
                {
                    "nombre_completo": "María Gómez",
                    "alias_conocidos": ["María", "Mary", "Mari", "Gómez", "Maria G"],
                    "email": "maria.gomez@empresa.com",
                    "rol": "Diseñadora UI/UX"
                },
                {
                    "nombre_completo": "Carlos Ruiz",
                    "alias_conocidos": ["Carlos", "Carlitos", "Ruiz", "Charlie", "Carlos R"],
                    "email": "carlos.ruiz@empresa.com",
                    "rol": "Desarrollador Backend"
                }
            ]
            for m in miembros_base:
                resp = Responsable(
                    proyecto_id="PROJ-DEFAULT",
                    nombre_completo=m["nombre_completo"],
                    alias_conocidos=m["alias_conocidos"],
                    email=m["email"],
                    rol=m["rol"]
                )
                db.add(resp)
            db.commit()
            print("[DB] Sembrado inicial de responsables y proyecto base completado.")
    except Exception as e:
        db.rollback()
        print(f"[DB] Error durante sembrado de datos: {e}")
    finally:
        db.close()
