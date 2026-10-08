import io
import sys
from pathlib import Path

# Asegurar importación del backend
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.core.perceptron import perceptron, NivelError, EstadoBinario
from app.services.vacas import vacas_manager
from app.schemas.reunion import EstadoReunion, EstrategiaIA
from app.db.session import SessionLocal
from app.db.models.auditoria import AuditoriaIALog

client = TestClient(app)

def test_perceptron_clasificacion_errores():
    # 1. Caso normal: < 3000ms, sin fallo -> Nivel 4 (Informativo), Estado 0 (Éxito)
    est, niv = perceptron.clasificar_ejecucion(latencia_ms=1200, fallo_proveedor=False, conmutacion_activada=False)
    assert est == EstadoBinario.EXITO.value
    assert niv == NivelError.NIVEL_4_INFORMATIVO.value

    # 2. Caso latencia alta (> 3000ms) -> Nivel 2 (Medio / Alerta SLA)
    est_sla, niv_sla = perceptron.clasificar_ejecucion(latencia_ms=4500, fallo_proveedor=False, conmutacion_activada=False)
    assert est_sla == EstadoBinario.EXITO.value
    assert niv_sla == NivelError.NIVEL_2_MEDIO.value

    # 3. Caso fallo primario recuperado por VACA -> Nivel 1 (Crítico recuperable)
    est_vaca, niv_vaca = perceptron.clasificar_ejecucion(latencia_ms=800, fallo_proveedor=True, conmutacion_activada=True)
    assert est_vaca == EstadoBinario.FALLO.value
    assert niv_vaca == NivelError.NIVEL_1_CRITICO.value

    # 4. Caso fallo total irrecuperable -> Nivel 0 (Catastrófico)
    est_cat, niv_cat = perceptron.clasificar_ejecucion(latencia_ms=200, fallo_proveedor=True, conmutacion_activada=False)
    assert est_cat == EstadoBinario.FALLO.value
    assert niv_cat == NivelError.NIVEL_0_CATASTROFICO.value

def test_vacas_conmutacion_directa():
    vacas_manager.simular_fallo_primaria = True
    try:
        resultado, proveedor, conmutacion, latencia = vacas_manager.ejecutar_con_conmutacion(
            prompt="Extraer tareas",
            system_prompt="Eres un asistente",
            reunion_id="MEET-TEST-VACAS",
            etapa="TEST_CONMUTACION"
        )
        assert conmutacion is True
        assert proveedor in [vacas_manager.PROVEEDOR_REPLICA, vacas_manager.PROVEEDOR_EMERGENCIA]
    finally:
        vacas_manager.simular_fallo_primaria = False

def test_auditoria_endpoints_y_chaos_testing_e2e():
    # 1. Consultar estado del Perceptrón
    res_estado = client.get("/api/v1/auditoria/estado")
    assert res_estado.status_code == 200
    body_estado = res_estado.json()
    assert body_estado["code"] == 200
    data_estado = body_estado["data"]
    assert data_estado["perceptron_activo"] is True
    assert "DEEPSEEK" in data_estado["vaca_primaria"]

    # 2. Activar simulación de fallo vía API (Chaos Testing)
    res_chaos = client.post("/api/v1/auditoria/simular-conmutacion", json={"activar_fallo": True})
    assert res_chaos.status_code == 200
    body_chaos = res_chaos.json()
    assert body_chaos["code"] == 200
    assert body_chaos["data"]["simulacion_activa"] is True

    try:
        # 3. Procesar reunión bajo fallo simulado (Estrategia 5 Híbrido)
        fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....data....")
        upload_res = client.post(
            "/api/v1/reuniones/upload?procesar_inmediato=false",
            files={"file": ("reunion_chaos_vaca.wav", fake_audio, "audio/wav")}
        )
        assert upload_res.status_code == 202
        id_reunion = upload_res.json()["data"]["id_reunion"]

        proc_res = client.post(
            f"/api/v1/reuniones/{id_reunion}/procesar",
            json={"estrategia": EstrategiaIA.ESTRATEGIA_5_HIBRIDO_MADURO.value}
        )
        assert proc_res.status_code == 200

        # La reunión debe haberse completado con éxito gracias a la VACA de respaldo
        det_res = client.get(f"/api/v1/reuniones/{id_reunion}/resultados")
        assert det_res.status_code == 200
        body_det = det_res.json()
        assert body_det["code"] == 200
        detalle = body_det["data"]
        assert detalle["estado"] == EstadoReunion.COMPLETADO
        assert len(detalle["acuerdos"]) > 0

        # 4. Verificar en los logs de PostgreSQL que se registró la conmutación
        logs_res = client.get(f"/api/v1/auditoria/logs?reunion_id={id_reunion}")
        assert logs_res.status_code == 200
        logs = logs_res.json()["data"]
        assert len(logs) >= 1
        assert any(l["conmutacion_vaca"] is True for l in logs)

        # 5. Consultar métricas globales
        metrics_res = client.get("/api/v1/auditoria/metricas")
        assert metrics_res.status_code == 200
        metricas = metrics_res.json()["data"]
        assert metricas["total_ejecuciones"] > 0
        assert metricas["total_conmutaciones_vaca"] > 0

    finally:
        client.post("/api/v1/auditoria/simular-conmutacion", json={"activar_fallo": False})
