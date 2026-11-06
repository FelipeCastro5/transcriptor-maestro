from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    client = TestClient(app)

    print("=== 1. VERIFICANDO SALUD DEL SERVICIO ===")
    r = client.get("/health")
    assert r.status_code == 200, f"Health failed: {r.status_code}"
    print("Health OK:", r.json())

    print("\n=== 2. FASE 1: CURVA DE ESPACIOS IGUALES & ALERTAS ===")
    r_sched = client.get("/api/v1/sistema/scheduler/estado")
    assert r_sched.status_code == 200
    print("Scheduler Estado:", r_sched.json()["data"])

    r_ejec = client.post("/api/v1/sistema/scheduler/ejecutar")
    assert r_ejec.status_code == 200
    print("Barrido Ejecutado:", r_ejec.json()["data"])

    r_alt = client.get("/api/v1/sistema/alertas")
    assert r_alt.status_code == 200
    total_alt = len(r_alt.json()["data"])
    print(f"Total Alertas en Sistema: {total_alt}")

    print("\n=== 3. FASE 2: MLOPS - WER, DATA DRIFT Y PROMPT REGISTRY ===")
    r_wer = client.post("/api/v1/auditoria/calibrar-wer", json={
        "texto_referencia": "Juan debe entregar el informe el viernes 20 de octubre.",
        "texto_hipotesis": "Juan debe entregar el informe el lunes 20 de octubre."
    })
    assert r_wer.status_code == 200
    data_wer = r_wer.json()["data"]
    print(f"WER Clásico: {data_wer['wer_porcentaje']}%")
    print(f"WER Ponderado (WER_w): {data_wer['wer_ponderado_porcentaje']}%")
    print(f"Alineación Tokens: {len(data_wer['alineacion'])} tokens alineados")

    r_drift = client.post("/api/v1/auditoria/data-drift", json={
        "texto": "Oigan el camello con el parche esta tenaz para coronar la vuelta."
    })
    assert r_drift.status_code == 200
    print("Data Drift Estado:", r_drift.json()["data"]["estado_drift"], "OOV:", r_drift.json()["data"]["ratio_oov_porcentaje"], "%")

    r_prompts = client.get("/api/v1/auditoria/prompts-historial")
    assert r_prompts.status_code == 200
    print(f"Prompt Registry: {len(r_prompts.json()['data'])} versiones registradas")

    print("\n=== 4. FASE 3: CONSENSO DUAL VACAS ===")
    from app.services.vacas import vacas_manager
    disc = vacas_manager._calcular_discrepancia("Juan entrega el informe el viernes", "Juan entrega el informe el lunes")
    print(f"Discrepancia entre respuestas: {round(disc*100, 2)}%")

    print("\n>>> TODAS LAS FASES FUNCIONANDO AL 100% <<<")

if __name__ == "__main__":
    run_tests()

