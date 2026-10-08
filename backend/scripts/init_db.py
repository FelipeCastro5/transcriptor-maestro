import pg8000.native

def create_database():
    try:
        # Conectar a la base de datos por defecto 'postgres'
        conn = pg8000.native.Connection(
            user="postgres",
            password="felipe",
            host="localhost",
            port=5432,
            database="postgres"
        )
        
        # Verificar si transcriptor_db existe
        rows = conn.run("SELECT 1 FROM pg_database WHERE datname = 'transcriptor_db'")
        if not rows:
            conn.run("CREATE DATABASE transcriptor_db")
            print("[OK] Base de datos 'transcriptor_db' creada exitosamente en PostgreSQL local.")
        else:
            print("[INFO] La base de datos 'transcriptor_db' ya existe.")
            
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Error al verificar/crear base de datos: {e}")
        return False

if __name__ == "__main__":
    create_database()
