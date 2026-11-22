import pg8000.native

import os
import pg8000.native

def create_database():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    db_target = os.getenv("DB_NAME", "transcriptor_db")

    try:
        # Conectar a la base de datos de administración por defecto 'postgres'
        conn = pg8000.native.Connection(
            user=user,
            password=password,
            host=host,
            port=port,
            database="postgres"
        )
        
        # Verificar si db_target existe
        rows = conn.run(f"SELECT 1 FROM pg_database WHERE datname = '{db_target}'")
        if not rows:
            conn.run(f"CREATE DATABASE {db_target}")
            print(f"[OK] Base de datos '{db_target}' creada exitosamente en PostgreSQL ({host}:{port}).")
        else:
            print(f"[INFO] La base de datos '{db_target}' ya existe.")
            
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Error al verificar/crear base de datos: {e}")
        return False

if __name__ == "__main__":
    create_database()
