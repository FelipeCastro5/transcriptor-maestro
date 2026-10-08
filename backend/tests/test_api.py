import io
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.reunion import EstadoReunion

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["status"] == "online"
    assert "service" in body["data"]

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert "docs" in body["data"]

def test_upload_audio_invalido():
    # Intento de subir archivo no permitido (.exe o .txt)
    fake_file = io.BytesIO(b"contenido de prueba")
    response = client.post(
        "/api/v1/reuniones/upload",
        files={"file": ("malware.exe", fake_file, "application/octet-stream")}
    )
    assert response.status_code == 400
    body = response.json()
    assert body["code"] == 400
    assert body["data"] is None
    assert "Formato no permitido" in body["message"]

def test_ciclo_reunion_upload_y_estado():
    # 1. Subir audio válido (.mp3) con procesar_inmediato=false para verificar estado EN_COLA
    fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....data....")
    upload_res = client.post(
        "/api/v1/reuniones/upload?procesar_inmediato=false",
        files={"file": ("reunion_sprint.mp3", fake_audio, "audio/mpeg")}
    )
    assert upload_res.status_code == 202
    body_upload = upload_res.json()
    assert body_upload["code"] == 202
    data_upload = body_upload["data"]
    assert "id_reunion" in data_upload
    assert data_upload["estado"] == EstadoReunion.EN_COLA
    id_reunion = data_upload["id_reunion"]

    # 2. Consultar estado de la reunión
    estado_res = client.get(f"/api/v1/reuniones/{id_reunion}/estado")
    assert estado_res.status_code == 200
    body_estado = estado_res.json()
    assert body_estado["code"] == 200
    data_estado = body_estado["data"]
    assert data_estado["id_reunion"] == id_reunion
    assert data_estado["nombre_archivo"] == "reunion_sprint.mp3"
    assert data_estado["estado"] == EstadoReunion.EN_COLA

    # 3. Listar reuniones
    list_res = client.get("/api/v1/reuniones/")
    assert list_res.status_code == 200
    body_list = list_res.json()
    assert body_list["code"] == 200
    data_list = body_list["data"]
    assert len(data_list) >= 1
    assert any(r["id_reunion"] == id_reunion for r in data_list)

def test_estado_reunion_no_encontrada():
    res = client.get("/api/v1/reuniones/MEET-INEXISTENTE/estado")
    assert res.status_code == 404
    body = res.json()
    assert body["code"] == 404
    assert body["data"] is None
