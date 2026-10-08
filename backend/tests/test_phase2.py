import io
import sys
from pathlib import Path

# Asegurar importación del backend
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.schemas.reunion import EstadoReunion, EstrategiaIA
from app.schemas.acuerdo import EstadoAcuerdo
from app.services.ai_handler import ai_handler

client = TestClient(app)

def test_estrategia_1_reglas_offline_directa():
    texto = (
        "Juan Pérez debe entregar el reporte financiero este viernes. "
        "María Gómez yo me encargo de revisar la interfaz el lunes."
    )
    acuerdos = ai_handler._extraer_reglas_offline(texto)
    assert len(acuerdos) >= 1
    primer_acuerdo = acuerdos[0]
    assert "Juan Pérez" in primer_acuerdo["responsable"]
    assert "reporte financiero" in primer_acuerdo["tarea_desc"].lower()

def test_flujo_completo_fase_2():
    # 1. Subir audio con procesamiento inmediato desactivado
    fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....data....")
    upload_res = client.post(
        "/api/v1/reuniones/upload?procesar_inmediato=false",
        files={"file": ("reunion_estrategia5.wav", fake_audio, "audio/wav")}
    )
    assert upload_res.status_code == 202
    body_upload = upload_res.json()
    assert body_upload["code"] == 202
    data_upload = body_upload["data"]
    id_reunion = data_upload["id_reunion"]
    assert data_upload["estado"] == EstadoReunion.EN_COLA

    # 2. Disparar procesamiento con Estrategia 1 (offline)
    proc_res = client.post(
        f"/api/v1/reuniones/{id_reunion}/procesar",
        json={"estrategia": EstrategiaIA.ESTRATEGIA_1_REGLAS_OFFLINE.value}
    )
    assert proc_res.status_code == 200
    assert proc_res.json()["code"] == 200

    # 3. Obtener resultados estandarizados con ResponseDto
    resultados_res = client.get(f"/api/v1/reuniones/{id_reunion}/resultados")
    assert resultados_res.status_code == 200
    body_res = resultados_res.json()
    assert body_res["code"] == 200
    detalle = body_res["data"]
    assert detalle["id_reunion"] == id_reunion
    assert detalle["estado"] == EstadoReunion.COMPLETADO
    assert detalle["transcripcion"] is not None
    assert detalle["resumen_ejecutivo"] is not None
    assert len(detalle["acuerdos"]) > 0

    id_acuerdo = detalle["acuerdos"][0]["id_acuerdo"]
    assert detalle["acuerdos"][0]["estado"] == EstadoAcuerdo.PENDIENTE.value

    # 4. Listar acuerdos por endpoint dedicado
    acuerdos_res = client.get(f"/api/v1/acuerdos/?id_reunion={id_reunion}")
    assert acuerdos_res.status_code == 200
    lista_acuerdos = acuerdos_res.json()["data"]
    assert len(lista_acuerdos) == len(detalle["acuerdos"])

    # 5. Actualizar estado del acuerdo a "completado"
    patch_res = client.patch(
        f"/api/v1/acuerdos/{id_acuerdo}/estado",
        json={"estado": EstadoAcuerdo.COMPLETADO.value, "nota_actualizacion": "Entregado a tiempo"}
    )
    assert patch_res.status_code == 200
    acuerdo_actualizado = patch_res.json()["data"]
    assert acuerdo_actualizado["estado"] == EstadoAcuerdo.COMPLETADO.value

    # 6. Comprobar en resultados que el acuerdo cambió a completado
    resultados_actualizados = client.get(f"/api/v1/reuniones/{id_reunion}/resultados").json()["data"]
    acuerdo_en_reunion = next(a for a in resultados_actualizados["acuerdos"] if a["id_acuerdo"] == id_acuerdo)
    assert acuerdo_en_reunion["estado"] == EstadoAcuerdo.COMPLETADO.value

def test_procesar_reunion_inexistente():
    res = client.post(
        "/api/v1/reuniones/MEET-INVENTADA/procesar",
        json={"estrategia": 1}
    )
    assert res.status_code == 404
    body = res.json()
    assert body["code"] == 404
    assert body["data"] is None
