import sys
from pathlib import Path

# Asegurar que el directorio raíz del backend esté en el PATH
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import traceback
from tests.test_api import (
    test_health_check,
    test_root,
    test_upload_audio_invalido,
    test_ciclo_reunion_upload_y_estado,
    test_estado_reunion_no_encontrada
)
from tests.test_phase2 import (
    test_estrategia_1_reglas_offline_directa,
    test_flujo_completo_fase_2,
    test_procesar_reunion_inexistente
)
from tests.test_phase3 import (
    test_fuzzy_matching_levenshtein,
    test_responsables_api,
    test_persistencia_y_matching_e2e,
    test_trazabilidad_historica
)
from tests.test_phase4 import (
    test_perceptron_clasificacion_errores,
    test_vacas_conmutacion_directa,
    test_auditoria_endpoints_y_chaos_testing_e2e
)

def run():
    tests = [
        # Fase 1: API REST Scaffold
        ("Fase 1: Salud (/health)", test_health_check),
        ("Fase 1: Raíz (/)", test_root),
        ("Fase 1: Validación de audio no permitido", test_upload_audio_invalido),
        ("Fase 1: Ciclo completo (Upload + Estado + Lista)", test_ciclo_reunion_upload_y_estado),
        ("Fase 1: Consulta reunión 404", test_estado_reunion_no_encontrada),

        # Fase 2: Handler de IA & Extracción
        ("Fase 2: Estrategia 1 reglas lingüísticas", test_estrategia_1_reglas_offline_directa),
        ("Fase 2: Flujo E2E (Procesamiento + Resultados + Acuerdos + PATCH)", test_flujo_completo_fase_2),
        ("Fase 2: Error al procesar reunión inexistente", test_procesar_reunion_inexistente),

        # Fase 3: Persistencia PostgreSQL + Fuzzy Matching + Trazabilidad
        ("Fase 3: Fuzzy Matching & Distancia Levenshtein", test_fuzzy_matching_levenshtein),
        ("Fase 3: CRUD Catálogo de Responsables", test_responsables_api),
        ("Fase 3: Persistencia PostgreSQL & Matching E2E", test_persistencia_y_matching_e2e),
        ("Fase 3: Trazabilidad Histórica entre Reuniones", test_trazabilidad_historica),

        # Fase 4: Resiliencia, El Perceptrón y VACAS
        ("Fase 4: Perceptrón & Clasificación de Jerarquía de Errores", test_perceptron_clasificacion_errores),
        ("Fase 4: Conmutación en Caliente de la VACA Réplica", test_vacas_conmutacion_directa),
        ("Fase 4: Chaos Testing E2E & Telemetría en PostgreSQL", test_auditoria_endpoints_y_chaos_testing_e2e),
    ]

    print("==================================================")
    print("   EJECUTANDO SUITE COMPLETA DE PRUEBAS (FASES 1-4)")
    print("==================================================")
    exitos = 0
    for nombre, func in tests:
        try:
            func()
            print(f" [OK] {nombre}")
            exitos += 1
        except Exception as e:
            print(f" [FALLO] {nombre}: {e}")
            traceback.print_exc()

    print(f"\nResultado final: {exitos}/{len(tests)} pruebas superadas.")
    if exitos == len(tests):
        print(">>> TODAS LAS PRUEBAS (FASES 1, 2, 3 Y 4) PASARON EXITOSAMENTE! <<<")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run()
