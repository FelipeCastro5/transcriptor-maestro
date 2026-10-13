import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from app.core.config import settings


class StorageService:
    """
    Servicio para inspección, mantenimiento y limpieza de los directorios de almacenamiento temporal.
    Gestiona storage/audios_temp y storage/salidas preservando los archivos .gitkeep.
    """

    def __init__(self):
        self.audios_dir: Path = settings.full_upload_path
        self.salidas_dir: Path = settings.full_output_path

        # Asegurar existencia de directorios
        self.audios_dir.mkdir(parents=True, exist_ok=True)
        self.salidas_dir.mkdir(parents=True, exist_ok=True)

    def _listar_archivos_dir(self, directorio: Path) -> List[Dict[str, Any]]:
        archivos = []
        if not directorio.exists():
            return archivos

        for item in directorio.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                stat = item.stat()
                archivos.append({
                    "nombre": item.name,
                    "tamano_bytes": stat.st_size,
                    "tamano_kb": round(stat.st_size / 1024, 2),
                    "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        return archivos

    def obtener_estado_storage(self) -> Dict[str, Any]:
        """
        Inspecciona los directorios de almacenamiento y devuelve un reporte detallado:
        - Si existe contenido pendiente de limpiar
        - Conteo y tamaño total en MB de audios_temp y salidas
        """
        audios = self._listar_archivos_dir(self.audios_dir)
        salidas = self._listar_archivos_dir(self.salidas_dir)

        bytes_audios = sum(a["tamano_bytes"] for a in audios)
        bytes_salidas = sum(s["tamano_bytes"] for s in salidas)
        total_bytes = bytes_audios + bytes_salidas

        total_archivos = len(audios) + len(salidas)
        tiene_contenido = total_archivos > 0

        return {
            "tiene_contenido": tiene_contenido,
            "total_archivos": total_archivos,
            "total_tamano_mb": round(total_bytes / (1024 * 1024), 2),
            "audios_temp": {
                "total_archivos": len(audios),
                "tamano_mb": round(bytes_audios / (1024 * 1024), 2),
                "archivos": audios
            },
            "salidas": {
                "total_archivos": len(salidas),
                "tamano_mb": round(bytes_salidas / (1024 * 1024), 2),
                "archivos": salidas
            }
        }

    def limpiar_todo(self, solo_audios: bool = False, solo_salidas: bool = False) -> Dict[str, Any]:
        """
        Elimina todos los archivos temporales en los directorios indicados preservando .gitkeep.
        """
        limpiar_audios = not solo_salidas
        limpiar_salidas = not solo_audios

        archivos_eliminados = 0
        bytes_liberados = 0
        detalles_eliminados = []

        directorios = []
        if limpiar_audios:
            directorios.append(("audios_temp", self.audios_dir))
        if limpiar_salidas:
            directorios.append(("salidas", self.salidas_dir))

        for nombre_dir, dir_path in directorios:
            if not dir_path.exists():
                continue

            for item in dir_path.iterdir():
                if item.is_file() and item.name != ".gitkeep":
                    try:
                        tamano = item.stat().st_size
                        item.unlink()
                        archivos_eliminados += 1
                        bytes_liberados += tamano
                        detalles_eliminados.append({
                            "directorio": nombre_dir,
                            "archivo": item.name,
                            "tamano_kb": round(tamano / 1024, 2)
                        })
                    except Exception as e:
                        print(f"[STORAGE-ERROR] No se pudo eliminar {item.name}: {e}")

        return {
            "archivos_eliminados": archivos_eliminados,
            "tamano_liberado_mb": round(bytes_liberados / (1024 * 1024), 2),
            "detalles": detalles_eliminados
        }

    def limpiar_archivos_reunion(self, id_reunion: str) -> Dict[str, Any]:
        """
        Elimina los archivos específicos asociados a una reunión particular:
        - Su audio temporal en audios_temp/ (ej: MEET-XXXXXXXX.mp3 o .wav)
        - Sus salidas en salidas/ (ej: MEET-XXXXXXXX_transcripcion.txt, _reporte.md, _acuerdos.json)
        """
        eliminados = []
        bytes_liberados = 0

        # 1. Buscar en audios_temp (archivos que comiencen con id_reunion)
        if self.audios_dir.exists():
            for item in self.audios_dir.iterdir():
                if item.is_file() and item.name.startswith(id_reunion) and item.name != ".gitkeep":
                    try:
                        tam = item.stat().st_size
                        item.unlink()
                        bytes_liberados += tam
                        eliminados.append(item.name)
                    except Exception as e:
                        print(f"[STORAGE-ERROR] Error eliminando audio de reunión {id_reunion}: {e}")

        # 2. Buscar en salidas (archivos que comiencen con id_reunion)
        if self.salidas_dir.exists():
            for item in self.salidas_dir.iterdir():
                if item.is_file() and item.name.startswith(id_reunion) and item.name != ".gitkeep":
                    try:
                        tam = item.stat().st_size
                        item.unlink()
                        bytes_liberados += tam
                        eliminados.append(item.name)
                    except Exception as e:
                        print(f"[STORAGE-ERROR] Error eliminando salida de reunión {id_reunion}: {e}")

        if eliminados:
            print(f"[STORAGE] Limpieza automática de reunión {id_reunion}: {len(eliminados)} archivo(s) eliminados ({round(bytes_liberados / 1024, 2)} KB liberados).")

        return {
            "id_reunion": id_reunion,
            "archivos_eliminados": eliminados,
            "tamano_liberado_kb": round(bytes_liberados / 1024, 2)
        }


storage_service = StorageService()
