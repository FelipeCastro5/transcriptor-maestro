"""
Script de mantenimiento y limpieza de almacenamiento temporal (storage)
Permite limpiar audios temporales y salidas de transcripción respetando los archivos .gitkeep.
"""

import sys
import argparse
from pathlib import Path

# Configurar salida segura para consola Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Raíz del backend (un nivel arriba de scripts/)
BACKEND_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BACKEND_DIR / "storage"
AUDIOS_DIR = STORAGE_DIR / "audios_temp"
SALIDAS_DIR = STORAGE_DIR / "salidas"


def limpiar_directorio(directorio: Path, solo_simulacion: bool = False) -> int:
    """Elimina todos los archivos de un directorio excepto .gitkeep."""
    if not directorio.exists():
        print(f"[INFO] El directorio no existe: {directorio}")
        return 0

    eliminados = 0
    for archivo in directorio.iterdir():
        if archivo.is_file() and archivo.name != ".gitkeep":
            tamano_kb = round(archivo.stat().st_size / 1024, 1)
            if solo_simulacion:
                print(f"  [SIMULACION] Se eliminaria: {archivo.name} ({tamano_kb} KB)")
            else:
                try:
                    archivo.unlink()
                    eliminados += 1
                except Exception as e:
                    print(f"  [ERROR] No se pudo eliminar {archivo.name}: {e}")

    return eliminados


def main():
    parser = argparse.ArgumentParser(
        description="Limpia los archivos temporales generados en backend/storage/"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo muestra que archivos se eliminarian sin borrar nada.",
    )
    parser.add_argument(
        "--audios-only",
        action="store_true",
        help="Limpia unicamente la carpeta storage/audios_temp/",
    )
    parser.add_argument(
        "--salidas-only",
        action="store_true",
        help="Limpia unicamente la carpeta storage/salidas/",
    )

    args = parser.parse_args()

    limpiar_audios = not args.salidas_only
    limpiar_salidas = not args.audios_only

    print("=" * 60)
    print("[MANTENIMIENTO] Limpieza de Almacenamiento Temporal (Storage)")
    print("=" * 60)

    total_eliminados = 0

    if limpiar_audios:
        print(f"\n[SCAN] Analizando carpeta: storage/audios_temp...")
        count = limpiar_directorio(AUDIOS_DIR, solo_simulacion=args.dry_run)
        total_eliminados += count
        if not args.dry_run:
            print(f"   -> {count} archivo(s) de audio eliminados.")

    if limpiar_salidas:
        print(f"\n[SCAN] Analizando carpeta: storage/salidas...")
        count = limpiar_directorio(SALIDAS_DIR, solo_simulacion=args.dry_run)
        total_eliminados += count
        if not args.dry_run:
            print(f"   -> {count} archivo(s) de salida (txt, md, json) eliminados.")

    print("\n" + "=" * 60)
    if args.dry_run:
        print("[INFO] Modo simulacion completado. No se borro ningun archivo real.")
    else:
        print(f"[OK] Limpieza finalizada. Total de archivos eliminados: {total_eliminados}")
    print("=" * 60)


if __name__ == "__main__":
    main()
