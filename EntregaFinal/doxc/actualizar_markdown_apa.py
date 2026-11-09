# -*- coding: utf-8 -*-
"""
Script de procesamiento académico:
1. Elimina todos los emojis del documento.
2. Reemplaza los bloques mermaid por figuras APA con sus imágenes generadas en alta resolución.
3. Incorpora numeración, titulación en cursiva y notas explicativas con formato APA 7 para todas las Tablas y Figuras.
"""
import os
import re

MD_PATH = r"C:\MisProyectos\ECCI\trasncriptor maestro\EntregaFinal\DOCUMENTO_FINAL_PROYECTO.md"

with open(MD_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Retirar emojis
emojis = ['🟡', '📘', '🟣', '📑', '🔵', '🔔', '🟢']
for e in emojis:
    text = text.replace(e, '')

# Limpiar espacios dobles dejados por emojis en títulos
text = text.replace('#  DOCUMENTO TÉCNICO', '# DOCUMENTO TÉCNICO')
text = text.replace('##  TABLA DE CONTENIDO', '## TABLA DE CONTENIDO')
text = text.replace('Campana Angular ()', 'Campana Angular de Alertas')

# 2. Reemplazar Mermaid 1 por Figura 1 APA
mermaid_1 = """```mermaid
flowchart LR
    A["Audio Continuo (8+ min)"] --> B["Chunk 1 [0s - 30s]"]
    A --> C["Chunk 2 [25s - 55s] (Stride 5s)"]
    A --> D["Chunk 3 [50s - 80s] (Stride 5s)"]
    B --> E["Inferencia Whisper"]
    C --> E
    D --> E
    E --> F["Reconstrucción Textual y Desduplicación"]
```"""

figura_1_apa = """**Figura 1**  
*Esquema de segmentación temporal deslizante (Chunking 30s con Stride 5s) para mitigación de sobrecarga atencional y memoria en ASR*

![](doxc/imagenes/figura1_chunking.png)

*Nota.* Flujo de división de señales acústicas extensas en bloques con traslape temporal de 5 segundos para garantizar continuidad léxica y contextual antes del motor Whisper. Fuente: Elaboración propia (2026)."""

if mermaid_1 in text:
    text = text.replace(mermaid_1, figura_1_apa)
    print("Mermaid 1 reemplazado con éxito")
else:
    print("AVISO: Mermaid 1 no encontrado exactamente")

# 3. Reemplazar Mermaid 2 por Figura 2 APA
mermaid_2 = """```mermaid
flowchart TD
    subgraph Cliente ["Capa de Presentación (Frontend SPA)"]
        UI["Angular 19 SPA"]
        UI_UP["Subida de Audio & Configuración"]
        UI_DASH["Minuta, Kanban y MLOps Tab"]
        UI_BELL["Campana de Alertas y Curva Espacios Iguales"]
    end

    subgraph API ["Capa de Exposición y Control (FastAPI)"]
        ROUTER["API Router REST (/api/v1)"]
        BG["FastAPI BackgroundTasks"]
        SCHED["SystemScheduler (APScheduler)"]
    end

    subgraph Core ["Capa de Inteligencia y Negocio"]
        AIH["AIHandler (Orquestador Dinámico)"]
        ASR["ASR Engine (Whisper Chunking 30s)"]
        VACAS["VACASManager (Respaldo Gemelo & Consenso)"]
        PERC["PerceptronAuditor (SLA 3s & Telemetría)"]
        FUZZY["FuzzyMatcher (Resolución de Responsables)"]
        EVAL["EvalService (WER, WERw y Data Drift)"]
        REG["PromptRegistry (MD5 Hashes)"]
    end

    subgraph Datos ["Capa de Persistencia y Almacenamiento"]
        PG[("PostgreSQL 16 (transcriptor_db)")]
        FS["Storage Local (Audios y Salidas MD/JSON)"]
    end

    UI_UP -->|HTTP POST Multipart| ROUTER
    ROUTER --> BG
    BG --> AIH
    AIH --> ASR
    ASR --> FS
    AIH --> VACAS
    VACAS -->|Auditoría| PERC
    PERC --> PG
    AIH --> FUZZY
    FUZZY --> PG
    SCHED -->|Barrido Medianoche| PG
    SCHED -->|Alertas| UI_BELL
    UI_DASH -->|Telemetría MLOps| EVAL
    EVAL --> PG
    REG --> AIH
```"""

figura_2_apa = """**Figura 2**  
*Arquitectura general en cuatro capas desacopladas del sistema Transcriptor Maestro*

![](doxc/imagenes/figura2_arquitectura.png)

*Nota.* Distribución desacoplada entre cliente Angular 19, orquestación asíncrona FastAPI, módulos cognitivos VACAS/Perceptrón y persistencia transaccional en PostgreSQL 16. Fuente: Elaboración propia (2026)."""

if mermaid_2 in text:
    text = text.replace(mermaid_2, figura_2_apa)
    print("Mermaid 2 reemplazado con éxito")
else:
    print("AVISO: Mermaid 2 no encontrado exactamente")

# 4. Reemplazar Mermaid 3 por Figura 3 APA
mermaid_3 = """```mermaid
sequenceDiagram
    autonumber
    participant S as SystemScheduler (APScheduler)
    participant DB as PostgreSQL (acuerdos)
    participant AS as AlertService
    participant UI as Campana Angular ()

    S->>DB: Escanear acuerdos en estado "pendiente"
    DB-->>S: Lista de compromisos activos
    loop Para cada acuerdo
        opt Fecha límite < Fecha actual
            S->>DB: Actualizar estado a "atrasado"
            S->>DB: Registrar en historial_estados
            S->>AS: Emitir Alerta WARNING (Atraso)
        end
        opt Compromiso no mencionado en >= 2 reuniones posteriores
            S->>AS: Emitir Alerta CRITICAL (Omisión Sistemática)
        end
    end
    AS->>DB: Persistir en alertas_sistema
    AS-->>UI: Reflejar en contador de alertas no leídas
```"""

# Si el emoji original estaba presente antes del replace
mermaid_3_alt = mermaid_3.replace("Campana Angular ()", "Campana Angular (🔔)")

figura_3_apa = """**Figura 3**  
*Diagrama de secuencia temporal del proceso de auditoría y disparo de alertas bajo la Curva de Espacios Iguales*

![](doxc/imagenes/figura3_secuencia_curva.png)

*Nota.* Ciclo de barrido periódico ejecutado por APScheduler para la identificación de compromisos en mora y omisiones sistemáticas en reuniones secuenciales. Fuente: Elaboración propia (2026)."""

if mermaid_3 in text:
    text = text.replace(mermaid_3, figura_3_apa)
    print("Mermaid 3 reemplazado con éxito")
elif mermaid_3_alt in text:
    text = text.replace(mermaid_3_alt, figura_3_apa)
    print("Mermaid 3 (alt) reemplazado con éxito")
else:
    # Buscar patrón genérico de sequenceDiagram
    m = re.search(r'```mermaid\s*sequenceDiagram[\s\S]*?```', text)
    if m:
        text = text.replace(m.group(0), figura_3_apa)
        print("Mermaid 3 (regex) reemplazado con éxito")
    else:
        print("AVISO: Mermaid 3 no encontrado")

# 5. Formatear Tablas APA

# Tabla 1
t1_target = "Las características físicas y espectrales del dataset se estandarizaron conforme a los estándares de la industria en procesamiento de voz:\n\n| Parámetro Acústico |"
t1_apa = """Las características físicas y espectrales del dataset se estandarizaron conforme a los estándares de la industria en procesamiento de voz:

**Tabla 1**  
*Especificaciones físicas, acústicas y formales del Dataset de Machine Learning*

| Parámetro Acústico |"""

t1_note = """| **Frecuencia Fundamental ($F_0$)** | $85 - 255\text{ Hz}$ | Cobertura integral de formantes vocálicos masculinos y femeninos sin atenuación espectral. |

*Nota.* Parámetros estandarizados para el entrenamiento y evaluación de modelos convolucionales de reconocimiento automático de voz. Fuente: Elaboración propia (2026)."""

text = text.replace(t1_target, t1_apa)
text = text.replace("| **Frecuencia Fundamental ($F_0$)** | $85 - 255\\text{ Hz}$ | Cobertura integral de formantes vocálicos masculinos y femeninos sin atenuación espectral. |", t1_note)

# Tabla 2
t2_target = "Se evaluó el audio patrón de oro (`original.mp3`, $N = 1\\,504$ palabras en Ground Truth) sobre las 3 variantes de OpenAI Whisper bajo igualdad de condiciones computacionales (GPU CUDA):\n\n| Métrica Evaluada |"
t2_apa = """Se evaluó el audio patrón de oro (`original.mp3`, $N = 1\\,504$ palabras en Ground Truth) sobre las 3 variantes de OpenAI Whisper bajo igualdad de condiciones computacionales (GPU CUDA):

**Tabla 2**  
*Benchmarking cuantitativo de las variantes de OpenAI Whisper sobre el audio patrón de oro ($N = 1.504$ palabras)*

| Métrica Evaluada |"""

t2_note = """| **Longitud Relativa ($\\text{LR}$)** | $0.996$ | $0.998$ | $1.001$ | $1.00 \\pm 0.05$ |

*Nota.* Pruebas realizadas sobre GPU NVIDIA con remuestreo homogéneo a 16 kHz. Métricas computadas mediante alineación dinámica de Levenshtein. Fuente: Elaboración propia (2026)."""

text = text.replace(t2_target, t2_apa)
text = text.replace("| **Longitud Relativa ($\\text{LR}$)** | $0.996$ | $0.998$ | $1.001$ | $1.00 \\pm 0.05$ |", t2_note)

# Tabla 3
t3_target = "Los 3 registros procesados en la base de datos del sistema (`transcriptor_db`) arrojaron los siguientes resultados objetivos:\n\n| Métrica de Producción |"
t3_apa = """Los 3 registros procesados en la base de datos del sistema (`transcriptor_db`) arrojaron los siguientes resultados objetivos:

**Tabla 3**  
*Métricas empíricas de ejecución en producción sobre hardware CPU convencional (Intel/AMD)*

| Métrica de Producción |"""

t3_note = """| **Reconocimiento de Entidades** | `Billatkinson` (unido), `Liza` | `Bill Atkinson`, `Elisa` | **`Bill Atkinson`, `Lisa` (Exacto)** |

*Nota.* Resultados obtenidos en entorno local de ejecución (CPU x86_64) con audio real no controlado de 4:50 minutos. Fuente: Base de datos transcriptor_db (2026)."""

text = text.replace(t3_target, t3_apa)
text = text.replace("| **Reconocimiento de Entidades** | `Billatkinson` (unido), `Liza` | `Bill Atkinson`, `Elisa` | **`Bill Atkinson`, `Lisa` (Exacto)** |", t3_note)

# Tabla 4
t4_target = "A lo largo de la asignatura, el equipo exploró y construyó 5 enfoques sucesivos para resolver la extracción cognitiva de acuerdos:\n\n| Enfoque / Prototipo |"
t4_apa = """A lo largo de la asignatura, el equipo exploró y construyó 5 enfoques sucesivos para resolver la extracción cognitiva de acuerdos:

**Tabla 4**  
*Evolución y caracterización comparativa de los cinco prototipos del orquestador AIHandler*

| Enfoque / Prototipo |"""

t4_note = """| **Intento 5 (Híbrido Maduro)** | **Whisper Medium (Chunking 30s)** | **DeepSeek + OpenAI (Doble llamada + VACAS)** | **Total (Hot-Failover + Consenso)** | **Cumple el 100% de los SLOs; captura el 95%+ de tareas con tolerancia a caídas.** | Requiere gestión de credenciales y orquestación multi-hilo. |

*Nota.* Comparativa de madurez técnica y tolerancia a fallos entre los enfoques implementados durante el ciclo de vida del proyecto. Fuente: Elaboración propia (2026)."""

text = text.replace(t4_target, t4_apa)
text = text.replace("| **Intento 5 (Híbrido Maduro)** | **Whisper Medium (Chunking 30s)** | **DeepSeek + OpenAI (Doble llamada + VACAS)** | **Total (Hot-Failover + Consenso)** | **Cumple el 100% de los SLOs; captura el 95%+ de tareas con tolerancia a caídas.** | Requiere gestión de credenciales y orquestación multi-hilo. |", t4_note)

# Tabla 5
t5_target = "### 5.1. Matriz de Cumplimiento de Promesas frente a la Entrega Final\n\n| Requisito / Promesa Inicial |"
t5_apa = """### 5.1. Matriz de Cumplimiento de Promesas frente a la Entrega Final

**Tabla 5**  
*Matriz de verificación y cumplimiento del 100% de los compromisos de la asignatura*

| Requisito / Promesa Inicial |"""

t5_note = """| **Frontend Full-Stack Desplegado** |  **100% CUMPLIDO** | Angular 19 SPA interactiva (`http://localhost:4200`) conectada por HTTP REST a FastAPI. |

*Nota.* Estado final de verificación contra las especificaciones funcionales y no funcionales comprometidas en los Cortes 1 y 2. Fuente: Elaboración propia (2026)."""

text = text.replace(t5_target, t5_apa)
text = text.replace("| **Frontend Full-Stack Desplegado** |  **100% CUMPLIDO** | Angular 19 SPA interactiva (`http://localhost:4200`) conectada por HTTP REST a FastAPI. |", t5_note)

with open(MD_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print("DOCUMENTO_FINAL_PROYECTO.md actualizado y formateado con éxito bajo normas APA.")
