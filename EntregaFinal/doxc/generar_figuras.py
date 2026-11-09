# -*- coding: utf-8 -*-
"""
Script para generar diagramas arquitectónicos vectoriales de alta definición (300 DPI)
para las Figuras 1, 2 y 3 del documento en formato APA.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = r"C:\MisProyectos\ECCI\trasncriptor maestro\EntregaFinal\doxc\imagenes"
os.makedirs(OUT_DIR, exist_ok=True)

# Configuración estética global
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# ==============================================================================
# FIGURA 1: Segmentación temporal deslizante (Chunking 30s con Stride 5s)
# ==============================================================================
def generar_figura_1():
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Nodo Audio Continuo
    ax.add_patch(patches.FancyBboxPatch((4, 18), 18, 14, boxstyle="round,pad=0.8",
                                        ec="#1E3A8A", fc="#DBEAFE", lw=1.8))
    ax.text(13, 25, "Audio Continuo\n(8+ minutos,\n16 kHz mono)", ha='center', va='center',
            fontsize=10, fontweight='bold', color="#1E3A8A")

    # Flechas de distribución
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color="#4B5563", lw=1.5)
    ax.annotate("", xy=(30, 38), xytext=(22, 29), arrowprops=arrow_props)
    ax.annotate("", xy=(30, 25), xytext=(22, 25), arrowprops=arrow_props)
    ax.annotate("", xy=(30, 12), xytext=(22, 21), arrowprops=arrow_props)

    # Chunks
    chunks = [
        ("Chunk 1: [0s - 30s]", 38, "#ECFDF5", "#065F46"),
        ("Chunk 2: [25s - 55s]\n(Stride = 5s)", 25, "#FEF3C7", "#92400E"),
        ("Chunk 3: [50s - 80s]\n(Stride = 5s)", 12, "#FEF3C7", "#92400E")
    ]
    for label, y, fc, tc in chunks:
        ax.add_patch(patches.FancyBboxPatch((30, y-4.5), 20, 9, boxstyle="round,pad=0.5",
                                            ec=tc, fc=fc, lw=1.5))
        ax.text(40, y, label, ha='center', va='center', fontsize=9, fontweight='bold', color=tc)

    # Flechas hacia Whisper
    ax.annotate("", xy=(58, 25), xytext=(50, 38), arrowprops=arrow_props)
    ax.annotate("", xy=(58, 25), xytext=(50, 25), arrowprops=arrow_props)
    ax.annotate("", xy=(58, 25), xytext=(50, 12), arrowprops=arrow_props)

    # Inferencia Whisper
    ax.add_patch(patches.FancyBboxPatch((58, 18), 16, 14, boxstyle="round,pad=0.8",
                                        ec="#4338CA", fc="#E0E7FF", lw=1.8))
    ax.text(66, 25, "Inferencia ASR\nLocal Whisper\n(Medium)", ha='center', va='center',
            fontsize=10, fontweight='bold', color="#4338CA")

    # Flecha a Reconstrucción
    ax.annotate("", xy=(82, 25), xytext=(74, 25), arrowprops=arrow_props)

    # Reconstrucción y desduplicación
    ax.add_patch(patches.FancyBboxPatch((82, 18), 15, 14, boxstyle="round,pad=0.8",
                                        ec="#047857", fc="#D1FAE5", lw=1.8))
    ax.text(89.5, 25, "Reconstrucción\nTextual &\nDesduplicación", ha='center', va='center',
            fontsize=9.5, fontweight='bold', color="#065F46")

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "figura1_chunking.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figura 1 guardada en: {out_path}")

# ==============================================================================
# FIGURA 2: Arquitectura de 4 Capas del Sistema Transcriptor Maestro
# ==============================================================================
def generar_figura_2():
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    capas = [
        ("1. Capa de Presentación (Frontend SPA Angular 19)", 82, 14, "#EFF6FF", "#1D4ED8", [
            ("Módulo de Carga de Audio\n& Configuración de Estrategias", 20, 88),
            ("Dashboard Minutas, Kanban\n& Panel de Auditoría MLOps", 50, 88),
            ("Campana de Alertas\n& Control Espacios Iguales", 80, 88)
        ]),
        ("2. Capa de Exposición y Servicios Asíncronos (FastAPI)", 59, 14, "#F0FDF4", "#15803D", [
            ("API Router REST\n(/api/v1/reuniones, /auditoria)", 25, 65),
            ("FastAPI BackgroundTasks\n(Ejecución Asíncrona)", 55, 65),
            ("SystemScheduler (APScheduler)\n(Curva Espacios Iguales)", 82, 65)
        ]),
        ("3. Capa de Lógica de Negocio, Inteligencia Artificial & MLOps", 33, 18, "#FAF5FF", "#7E22CE", [
            ("ASR Whisper\n(Chunking 30s)", 15, 41),
            ("Sistema Gemelo VACAS\n(DeepSeek + OpenAI)", 36, 41),
            ("PerceptronAuditor\n(SLA 3s & Telemetría)", 57, 41),
            ("FuzzyMatcher\n(Resolución Nombres)", 75, 41),
            ("PromptRegistry\n(MD5 Inmutable)", 90, 41)
        ]),
        ("4. Capa de Persistencia y Almacenamiento", 8, 16, "#FFFBEB", "#B45309", [
            ("PostgreSQL 16 (transcriptor_db)\n(Reuniones, Acuerdos, Alertas, Logs Auditoría)", 40, 15),
            ("Storage Local en Disco\n(Archivos .mp3, .wav, minutas .md y JSON)", 80, 15)
        ])
    ]

    for title, y_bottom, height, bg_col, border_col, components in capas:
        ax.add_patch(patches.FancyBboxPatch((4, y_bottom), 92, height, boxstyle="round,pad=0.5",
                                            ec=border_col, fc=bg_col, lw=1.8, linestyle="--"))
        ax.text(6, y_bottom + height - 2.8, title, fontsize=10.5, fontweight='bold', color=border_col)

        for text, cx, cy in components:
            box_w = 16 if len(components) >= 5 else 24
            ax.add_patch(patches.FancyBboxPatch((cx - box_w/2, cy - 4.5), box_w, 8, boxstyle="round,pad=0.4",
                                                ec=border_col, fc="#FFFFFF", lw=1.2))
            ax.text(cx, cy - 0.5, text, ha='center', va='center', fontsize=8, color="#1F2937", fontweight='bold')

    arrow_props = dict(arrowstyle="<->,head_width=0.35,head_length=0.5", color="#4B5563", lw=1.5)
    ax.annotate("", xy=(30, 82), xytext=(30, 73), arrowprops=arrow_props)
    ax.annotate("", xy=(50, 59), xytext=(50, 51), arrowprops=arrow_props)
    ax.annotate("", xy=(50, 33), xytext=(50, 24), arrowprops=arrow_props)

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "figura2_arquitectura.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figura 2 guardada en: {out_path}")

# ==============================================================================
# FIGURA 3: Diagrama de Secuencia de la Curva de Espacios Iguales
# ==============================================================================
def generar_figura_3():
    fig, ax = plt.subplots(figsize=(10.5, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    participants = [
        ("SystemScheduler\n(APScheduler Daemon)", 15, "#DBEAFE", "#1E40AF"),
        ("PostgreSQL 16\n(Tabla 'acuerdos')", 40, "#E0E7FF", "#3730A3"),
        ("AlertService\n(Reglas de Negocio)", 65, "#FEF3C7", "#92400E"),
        ("Campana Angular\n(Interfaz de Usuario)", 90, "#FCE7F3", "#9D174D")
    ]

    for label, x, fc, tc in participants:
        ax.add_patch(patches.FancyBboxPatch((x-10, 88), 20, 9, boxstyle="round,pad=0.4",
                                            ec=tc, fc=fc, lw=1.5))
        ax.text(x, 92.5, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color=tc)
        ax.plot([x, x], [12, 88], linestyle="--", color="#9CA3AF", lw=1.2)
        ax.add_patch(patches.FancyBboxPatch((x-10, 3), 20, 7, boxstyle="round,pad=0.4",
                                            ec=tc, fc=fc, lw=1.2))
        ax.text(x, 6.5, label.split('\n')[0], ha='center', va='center', fontsize=7.5, color=tc)

    arrow_msg = dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#1F2937", lw=1.3)
    arrow_ret = dict(arrowstyle="->,head_width=0.3,head_length=0.4", color="#4B5563", lw=1.2, linestyle=":")

    secuencia = [
        (15, 40, 78, "1. Escaneo periódico de acuerdos 'pendientes'", arrow_msg),
        (40, 15, 71, "2. Retorno de tuplas de compromisos activos", arrow_ret),
        (15, 40, 62, "3. Identificación fecha vencida -> estado 'atrasado'", arrow_msg),
        (15, 65, 53, "4. Disparo de Alerta WARNING por Atraso", arrow_msg),
        (15, 65, 44, "5. Detección de Omisión (>= 2 reuniones ausente)", arrow_msg),
        (65, 40, 35, "6. Persistencia de alerta en 'alertas_sistema'", arrow_msg),
        (65, 90, 26, "7. Despacho reactivo a campana de usuario", arrow_msg),
        (90, 90, 17, "8. Actualización en tiempo real de badge y modal", arrow_ret)
    ]

    for x1, x2, y, txt, style in secuencia:
        if x1 == x2:
            ax.annotate("", xy=(x1, y-4), xytext=(x1+6, y), arrowprops=style)
            ax.plot([x1, x1+6], [y, y], color="#1F2937", lw=1.2)
            ax.text(x1+7, y-2, txt, va='center', fontsize=8, color="#1F2937")
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=style)
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 2, txt, ha='center', va='bottom', fontsize=8, color="#111827", fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "figura3_secuencia_curva.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Figura 3 guardada en: {out_path}")

if __name__ == "__main__":
    generar_figura_1()
    generar_figura_2()
    generar_figura_3()
    print("Todas las figuras generadas exitosamente en 300 DPI.")
