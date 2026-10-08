import io
import sys
from pathlib import Path

# Asegurar importación del backend
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.services.matching import fuzzy_matcher
from app.schemas.reunion import EstadoReunion, EstrategiaIA
from app.schemas.acuerdo import EstadoAcuerdo
from app.db.session import SessionLocal
from app.db.models.responsable import Responsable
from app.db.models.reunion import Reunion
from app.db.models.acuerdo import Acuerdo

client = TestClient(app)

def test_fuzzy_matching_levenshtein():
    # 1. Distancia pura
    assert fuzzy_matcher.distancia_levenshtein("Juna", "Juan") == 2
    assert fuzzy_matcher.distancia_levenshtein("Carlos", "Carlos") == 0

    # 2. Similitud pura
    ratio = fuzzy_matcher.similitud_ratio("Juna Pérez", "Juan Pérez")
    assert ratio >= 0.80

    # 3. Matching contra catálogo
    db = SessionLocal()
    try:
        catalogo = db.query(Responsable).all()
        resp, nombre_resuelto, score = fuzzy_matcher.emparejar_responsable("Juna Pérez", catalogo)
        assert resp is not None
        assert nombre_resuelto == "Juan Pérez"
        assert score >= 0.80

        resp_alias, nombre_alias, score_alias = fuzzy_matcher.emparejar_responsable("Carlitos", catalogo)
        assert resp_alias is not None
        assert nombre_alias == "Carlos Ruiz"
    finally:
        db.close()

def test_responsables_api():
    # 1. Listar catálogo
    res = client.get("/api/v1/responsables/")
    assert res.status_code == 200
    body = res.json()
    assert body["code"] == 200
    lista = body["data"]
    assert len(lista) >= 3
    assert any(r["nombre_completo"] == "Juan Pérez" for r in lista)

    # 2. Crear nuevo miembro
    nuevo_res = client.post(
        "/api/v1/responsables/",
        json={
            "nombre_completo": "Andrés Morales",
            "alias_conocidos": ["Andrés", "Andy", "Morales"],
            "email": "andres.morales@empresa.com",
            "rol": "DevOps Engineer"
        }
    )
    assert nuevo_res.status_code == 201
    body_nuevo = nuevo_res.json()
    assert body_nuevo["code"] == 201
    data_nuevo = body_nuevo["data"]
    assert data_nuevo["nombre_completo"] == "Andrés Morales"

def test_persistencia_y_matching_e2e():
    # 1. Subir y procesar reunión con Estrategia 1 (offline)
    fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....data....")
    upload_res = client.post(
        "/api/v1/reuniones/upload?procesar_inmediato=false",
        files={"file": ("reunion_fase3.wav", fake_audio, "audio/wav")}
    )
    assert upload_res.status_code == 202
    id_reunion = upload_res.json()["data"]["id_reunion"]

    # Procesar
    proc_res = client.post(
        f"/api/v1/reuniones/{id_reunion}/procesar",
        json={"estrategia": EstrategiaIA.ESTRATEGIA_1_REGLAS_OFFLINE.value}
    )
    assert proc_res.status_code == 200

    # 2. Consultar resultados desde la base de datos PostgreSQL
    res = client.get(f"/api/v1/reuniones/{id_reunion}/resultados")
    assert res.status_code == 200
    body_res = res.json()
    assert body_res["code"] == 200
    detalle = body_res["data"]
    assert detalle["estado"] == EstadoReunion.COMPLETADO
    assert len(detalle["acuerdos"]) > 0

    primer_acuerdo = detalle["acuerdos"][0]
    assert primer_acuerdo["responsable"] == "Juan Pérez"
    assert primer_acuerdo["similitud_fuzzy"] is not None
    assert primer_acuerdo["similitud_fuzzy"] >= 0.70

def test_trazabilidad_historica():
    db = SessionLocal()
    try:
        id_reunion_previa = "MEET-PREVIA-TEST"
        id_acuerdo_previo = "AC-HISTORICO-TEST"

        reunion_previa = db.query(Reunion).filter(Reunion.id == id_reunion_previa).first()
        if not reunion_previa:
            reunion_previa = Reunion(
                id=id_reunion_previa,
                nombre_archivo="reunion_sprint_1.wav",
                ruta_audio="dummy/path",
                estado_proceso="COMPLETADO"
            )
            db.add(reunion_previa)
            db.commit()

        existente = db.query(Acuerdo).filter(Acuerdo.id == id_acuerdo_previo).first()
        if existente:
            db.delete(existente)
            db.commit()

        acuerdo_previo = Acuerdo(
            id=id_acuerdo_previo,
            reunion_id=id_reunion_previa,
            tarea_desc="revisar los endpoints del backend",
            responsable="Carlos Ruiz",
            fragmento_original="Carlos debe revisar los endpoints",
            estado="pendiente"
        )
        db.add(acuerdo_previo)
        db.commit()

        transcripcion_nueva = (
            "Buenas tardes equipo. Carlos ya reviso y quedo listo los endpoints del backend con el equipo tecnico."
        )
        detectados = fuzzy_matcher.detectar_cumplimiento_historico(
            transcripcion=transcripcion_nueva,
            acuerdos_pendientes=[acuerdo_previo]
        )
        assert len(detectados) == 1
        assert detectados[0]["acuerdo_id"] == id_acuerdo_previo
        assert detectados[0]["estado_nuevo"] == "completado"
    finally:
        db.close()
