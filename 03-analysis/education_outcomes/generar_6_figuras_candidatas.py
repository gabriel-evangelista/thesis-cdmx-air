import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy.interpolate import CubicSpline

BASE       = "/Users/gabrielevangelista/thesis-cdmx-air"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
OUT_DIR    = f"{BASE}/figuras_tesis"
os.makedirs(OUT_DIR, exist_ok=True)

# Estilo global consistente con Figuras 2.1 y 4.1
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 10,
    "axes.edgecolor": "#4a5568",
    "axes.linewidth": 0.8,
})

C_NAVY   = "#005a9c"
C_DARK   = "#1a252f"
C_RED    = "#b2182b"
C_AMBER  = "#d95f02"
C_TEAL   = "#1b9e77"
C_GRAY   = "#7f8c8d"
C_LIGHT  = "#f4f8fb"


# =====================================================================
# FIGURA CANDIDATA 1: PIPELINE DE ARQUITECTURA DE DATOS Y MODELADO
# =====================================================================
def crear_fig1_pipeline():
    fig, ax = plt.subplots(figsize=(13.6, 8.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.3):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.4",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
        )
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 2.3, title, ha="center", va="top",
                fontsize=9.3, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w/2, y + h/2 - 1.5, body, ha="center", va="center",
                fontsize=8.0, color=C_DARK, linespacing=1.28, zorder=4)

    def arrow(x1, y1, x2, y2, color="#4a5568", lw=1.35):
        a = FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>,head_length=6,head_width=3.5",
            color=color, linewidth=lw, zorder=2, connectionstyle="arc3,rad=0.0"
        )
        ax.add_patch(a)

    # Etiquetas de capas a la izquierda
    capas = [
        (87.5, "1. INSUMOS\nPÚBLICOS"),
        (66.5, "2. PREPROCESO\nY PUENTE FÍSICO"),
        (45.0, "3. DISPERSIÓN\nATMOSFÉRICA"),
        (22.5, "4. IDENTIFICACIÓN\nECONOMÉTRICA"),
        (5.5,  "5. POLÍTICA\nPÚBLICA"),
    ]
    for yc, lbl in capas:
        ax.text(5.8, yc, lbl, ha="center", va="center", fontsize=8.2,
                fontweight="bold", color="#5d6d7e")

    # CAPA 1: 4 dominios de datos (x: 13 a 98)
    box(13.0, 81.0, 19.5, 13.5, "RETC / COA (SEMARNAT)",
        "723 establecimientos (2015–2019)\nCO2 como trazador de actividad\n→ 285 fuentes fijas activas",
        fc="#fdf6f0", ec=C_AMBER, title_color="#9a3412")
    box(34.5, 81.0, 19.5, 13.5, "Meteorología (NOAA / CENACE)",
        "ISD superficie + IGRA radiosondeo\nEstación AICM (WMO 76679)\n8,760 h/año + demanda SIN",
        fc="#f0f7fb", ec=C_NAVY, title_color=C_NAVY)
    box(56.0, 81.0, 19.5, 13.5, "Relieve (SRTM 30 m)",
        "4 mosaicos GeoTIFF (1 arc-seg)\nCuenca de México y sierras\nProyección UTM 14N (EPSG:32614)",
        fc="#f0f7fb", ec=C_NAVY, title_color=C_NAVY)
    box(77.5, 81.0, 20.5, 13.5, "PLANEA / SIGED (SEP–INEE)",
        "3° Secundaria (2015, 2017, 2019)\n3,833 CCT → 3,172 inmuebles\n2,392 inmuebles en Cuenca (9,459 obs.)",
        fc="#f2faf6", ec=C_TEAL, title_color="#116b50")

    # CAPA 2: Preprocesamiento
    box(13.0, 60.0, 25.5, 13.0, "Auditoría RETC y Puente AP-42",
        "Corrección de anomalías e imputación 2018\nConversión CO2 → PM2.5 en 6 familias AP-42\nParámetros de chimenea + perfiles EMISFACT",
        fc="#ffffff", ec=C_AMBER, title_color="#9a3412")
    box(41.0, 60.0, 22.0, 13.0, "AERMET (Etapas 1–3)",
        "Flujo de calor, u*, longitud L,\ncapas límite convectiva (Zic) y mecánica\n→ Archivos .sfc/.pfl + controles Wrt",
        fc="#ffffff", ec=C_NAVY, title_color=C_NAVY)
    box(65.5, 60.0, 32.5, 13.0, "AERMAP y Armonización Escolar",
        "Elevación (Zelev) y altura crítica de colina (Zhill)\nDeduplicación CCT ↔ RECID y turnos armonizados\nPuntajes estandarizados (media 500, DE 100)",
        fc="#ffffff", ec=C_TEAL, title_color="#116b50")

    # Flechas Capa 1 -> Capa 2
    arrow(22.7, 81.0, 25.5, 73.2)
    arrow(44.2, 81.0, 52.0, 73.2)
    arrow(44.2, 81.0, 34.0, 73.2, color=C_GRAY, lw=1.0)
    arrow(65.7, 81.0, 76.0, 73.2)
    arrow(87.7, 81.0, 86.0, 73.2)

    # CAPA 3: Motor de Dispersión AERMOD
    cont_aermod = FancyBboxPatch(
        (13.0, 37.5), 85.0, 15.0, boxstyle="round,pad=0.5,rounding_size=1.6",
        facecolor=C_LIGHT, edgecolor=C_NAVY, linewidth=1.5, linestyle="--", zorder=1
    )
    ax.add_patch(cont_aermod)
    ax.text(55.5, 51.4, "MODELO REGULATORIO AERMOD (concentraciones de PM2.5 industrial a z = 1.5 m)",
            ha="center", va="center", fontsize=8.8, fontweight="bold", color=C_NAVY, zorder=4)

    box(15.5, 39.0, 38.0, 10.5, "Corrida Anual con EMISFACT + SRCGROUP",
        "Promedio anual (2015, 2017, 2019) por inmueble\nDesagregación por 5 ramas tecnológicas AP-42",
        fc="#ffffff", ec=C_NAVY, title_color=C_DARK, lw=1.1)
    box(57.5, 39.0, 38.0, 10.5, "Corrida Horaria POSTFILE (95 días pre/post PLANEA)",
        "Resolución 1 h (28 abr – 31 jul) filtrada al horario exacto\nde cada turno (matutino, vespertino, tiempo completo)",
        fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.1)

    # Flechas Capa 2 -> Capa 3
    arrow(25.7, 60.0, 34.5, 52.6)
    arrow(52.0, 60.0, 55.5, 52.6)
    arrow(81.7, 60.0, 76.5, 52.6)

    # CAPA 4: Dos Pilares Econométricos
    box(13.0, 15.0, 40.5, 15.0, "Pilar 1: Panel Anual TWFE (pyfixest)",
        "EF unidad (αi) + año (γt) / Mun×Año + controles Wrt\n• Efecto promedio metropolitano (nulo)\n• Heterogeneidad por rama AP-42 y alta marginación\n• 5 especificaciones de robustez (cluster RECID/Mun.)",
        fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.4)
    box(57.5, 15.0, 40.5, 15.0, "Pilar 2: Identificación Causal 2SLS y Forma Reducida",
        "Exposición física POSTFILE por turno (30d previos, μg/m³)\n• Instrumento: alineación horaria de viento con Q2015 fija\n• Contraste simétrico TWFE vs. 2SLS (sesgo de atenuación)\n• Pruebas de mecanismo: 24h vs. turno y placebo 30d post.",
        fc="#fff8f8", ec=C_RED, title_color=C_RED, lw=1.4)

    # Flechas Capa 3 -> Capa 4
    arrow(34.5, 38.8, 33.2, 30.3, color=C_NAVY)
    arrow(76.5, 38.8, 77.7, 30.3, color=C_RED)

    # CAPA 5: Política Pública
    box(13.0, 1.2, 85.0, 8.8, "Transferencia a Política Pública (ProAire ZMVM / SEP / SEDEMA)",
        "Focalización escolar: 27 inmuebles públicos hipervulnerables (36 CCT, ~17,600 alumnos; filtración HEPA ≈ $2.46M MXN)   |   "
        "Regulación ambiental: auditoría dirigida a 56 plantas (47 fundiciones + 9 vidrieras = 40.6% de emisiones)",
        fc="#eef6f2", ec=C_TEAL, title_color="#116b50", lw=1.4)

    arrow(33.2, 14.8, 42.0, 10.3, color=C_TEAL)
    arrow(77.7, 14.8, 69.0, 10.3, color=C_TEAL)

    ax.set_title("Arquitectura de Integración de Datos, Modelación Física (AERMOD) e Identificación Econométrica",
                 fontsize=12.0, fontweight="bold", color=C_DARK, pad=6)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cand1_pipeline_arquitectura.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cand1_pipeline_arquitectura.png")


# =====================================================================
# FIGURA CANDIDATA 2: CONO DE VIENTO vs. RADIOS CONCÉNTRICOS (SULLIVAN)
# =====================================================================
def crear_fig2_cono_vs_radios():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.8), dpi=300)

    # Malla 2D en km (-3.4 a 3.4)
    grid = np.linspace(-3.4, 3.4, 300)
    X, Y = np.meshgrid(grid, grid)
    R = np.maximum(np.sqrt(X**2 + Y**2), 0.18)

    # Viento dominante ZMVM: sopla del NE (45°) hacia el SO (225°) -> vector (-0.707, -0.707)
    wx, wy = -np.sqrt(0.5), -np.sqrt(0.5)
    cos_th = (X * wx + Y * wy) / R
    pluma = (np.maximum(0.0, cos_th) ** 10) / (R ** 1.35)
    pluma = np.where(R < 0.12, np.nan, pluma)
    pluma_norm = np.clip(pluma / np.nanpercentile(pluma[pluma > 0], 98.5), 0, 1)

    # Escuelas ilustrativas
    esc_A = (0.55, 0.55)    # 0.78 km barlovento (NE) -> falsamente tratada en anillos
    esc_B = (-1.60, -1.55)  # 2.23 km sotavento (SO)  -> control contaminado en anillos
    esc_C = (-1.55, 1.55)   # 2.19 km lateral (NO)    -> control limpio real

    for ax in (ax1, ax2):
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-3.4, 3.4)
        ax.set_aspect("equal")
        ax.set_xlabel("Distancia Este–Oeste desde la fuente (km)", fontsize=9.5)
        ax.set_ylabel("Distancia Norte–Sur desde la fuente (km)", fontsize=9.5)
        ax.grid(True, linestyle=":", alpha=0.45, color="#bdc3c7")
        ax.axhline(0, color="#cbd5e0", lw=0.7, zorder=1)
        ax.axvline(0, color="#cbd5e0", lw=0.7, zorder=1)

    # --- PANEL A: Enfoque tradicional por radios concéntricos ---
    c1 = plt.Circle((0, 0), 1.0, facecolor="#fed976", edgecolor=C_AMBER, alpha=0.35, lw=1.6, ls="--", zorder=2)
    c2 = plt.Circle((0, 0), 3.0, facecolor="#deebf7", edgecolor=C_NAVY, alpha=0.22, lw=1.4, ls="--", zorder=1)
    ax1.add_patch(c2)
    ax1.add_patch(c1)

    # Sombra tenue de la pluma real que el modelo ingenuo ignora
    ax1.contourf(X, Y, pluma_norm, levels=np.linspace(0.06, 1.0, 8), cmap="Reds", alpha=0.28, zorder=2)

    ax1.scatter([0], [0], marker="^", s=160, c=C_DARK, edgecolors="white", lw=1.0, zorder=6, label="Chimenea industrial (RETC)")
    ax1.scatter(*esc_A, s=110, c=C_TEAL, edgecolors=C_DARK, lw=1.0, zorder=6)
    ax1.scatter(*esc_B, s=110, c=C_RED, edgecolors="white", lw=1.0, zorder=6)
    ax1.scatter(*esc_C, s=90,  c=C_NAVY, edgecolors="white", lw=1.0, zorder=6)

    ax1.annotate("Tratamiento ingenuo\n(r ≤ 1 km)", xy=(0.1, -0.95), xytext=(1.1, -1.65),
                 fontsize=8.2, fontweight="bold", color="#9a3412",
                 arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.0))
    ax1.annotate("Control ingenuo\n(1 < r ≤ 3 km)", xy=(2.1, -2.0), xytext=(1.05, -3.1),
                 fontsize=8.2, fontweight="bold", color=C_NAVY,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.0))

    ax1.annotate("Escuela A (0.8 km, barlovento)\nError Tipo I: aire limpio,\nclasificada como 'tratada'",
                 xy=esc_A, xytext=(0.55, 1.95), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_TEAL, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.1), zorder=7)
    ax1.annotate("Escuela B (2.2 km, sotavento)\nControl contaminado:\nrecibe la pluma de lleno",
                 xy=esc_B, xytext=(-3.25, -0.55), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_RED, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.1), zorder=7)

    ax1.set_title("A. Radios concéntricos tradicionales (sesgo por viento)", fontsize=10.3, fontweight="bold", color=C_DARK, pad=8)

    # --- PANEL B: Enfoque direccional (AERMOD + Cono de viento) ---
    cf = ax2.contourf(X, Y, pluma_norm, levels=np.linspace(0.04, 1.0, 14), cmap="YlOrRd", alpha=0.82, zorder=2)
    ax2.contour(X, Y, pluma_norm, levels=[0.08], colors=C_RED, linewidths=1.1, linestyles="--", zorder=3)

    # Anillos en gris muy tenue solo como referencia visual
    ax2.add_patch(plt.Circle((0, 0), 1.0, fill=False, edgecolor="#cbd5e0", lw=0.9, ls=":", zorder=2))
    ax2.add_patch(plt.Circle((0, 0), 3.0, fill=False, edgecolor="#cbd5e0", lw=0.9, ls=":", zorder=2))

    # Vector de viento y eje de la pluma
    ax2.annotate("", xy=(-2.6, -2.6), xytext=(0, 0),
                 arrowprops=dict(arrowstyle="-|>,head_length=8,head_width=4.5", color=C_DARK, lw=2.0), zorder=5)
    ax2.text(-2.78, -2.95, r"Vector de viento $\vec{w}$" + "\n(NE → SO)", fontsize=8.3,
             fontweight="bold", color=C_DARK, ha="center")

    # Rayo hacia un punto con ángulo theta
    ax2.plot([0, -2.2], [0, -1.35], color=C_NAVY, lw=1.2, ls="-.", zorder=5)
    arc = patches.Arc((0, 0), 2.1, 2.1, angle=0, theta1=211.5, theta2=225.0, color=C_NAVY, lw=1.6, zorder=6)
    ax2.add_patch(arc)
    ax2.text(-1.28, -0.98, r"$\theta_{sr}$", fontsize=10, fontweight="bold", color=C_NAVY, zorder=7)

    ax2.scatter([0], [0], marker="^", s=160, c=C_DARK, edgecolors="white", lw=1.0, zorder=6)
    ax2.scatter(*esc_A, s=110, c=C_TEAL, edgecolors=C_DARK, lw=1.0, zorder=6)
    ax2.scatter(*esc_B, s=110, c=C_RED, edgecolors="white", lw=1.0, zorder=6)
    ax2.scatter(*esc_C, s=90,  c=C_NAVY, edgecolors="white", lw=1.0, zorder=6)

    ax2.annotate("Escuela A (barlovento)\nExposición ≈ 0\n(cos θ < 0)",
                 xy=esc_A, xytext=(0.75, 1.95), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_TEAL, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.1), zorder=7)
    ax2.annotate("Escuela B (sotavento)\nAlta exposición capturada\npor AERMOD e IV",
                 xy=esc_B, xytext=(0.45, -2.55), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_RED, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.1), zorder=7)
    ax2.annotate("Escuela C (lateral)\nControl limpio\n(fuera del cono)",
                 xy=esc_C, xytext=(-3.25, 2.15), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_NAVY, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.1), zorder=7)

    ax2.text(-3.2, 0.35, r"Cono direccional:" + "\n" + r"$\max\{0,\cos\theta_{sr,th}\}^{10} \cdot x_{sr}^{-1.5}$",
             fontsize=8.3, color=C_DARK, bbox=dict(boxstyle="round,pad=0.35", fc="#fffdf7", ec=C_AMBER, lw=0.9))

    cbar = plt.colorbar(cf, ax=ax2, fraction=0.044, pad=0.03)
    cbar.set_label("Intensidad relativa de la pluma", fontsize=8.5)
    ax2.set_title("B. Dispersión direccional (AERMOD + cono de viento)", fontsize=10.3, fontweight="bold", color=C_DARK, pad=8)

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cand2_cono_viento_vs_radios.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cand2_cono_viento_vs_radios.png")


# =====================================================================
# FIGURA CANDIDATA 3: CICLO EMISFACT + CAPA LÍMITE REAL AERMET + TURNOS
# =====================================================================
def crear_fig3_emisfact_capa_limite():
    # Leer altura real de mezcla por hora desde aer_2015, aer_2017, aer_2019 (.sfc)
    filas = []
    for yr in [2015, 2017, 2019]:
        with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
            for line in f.readlines()[1:]:
                p = line.split()
                if len(p) >= 22:
                    hr = int(p[4])
                    zic, zim = float(p[9]), float(p[10])
                    vals = [v for v in (zic, zim) if 0 < v < 5000]
                    z_eff = max(vals) if vals else np.nan
                    zim_c = zim if 0 < zim < 5000 else np.nan
                    filas.append((hr, z_eff, zim_c))
    df_pbl = pd.DataFrame(filas, columns=["hr", "z_eff", "zim"]).dropna(subset=["z_eff"])
    pbl_stats = df_pbl.groupby("hr")["z_eff"].agg(
        med="median",
        p25=lambda s: np.percentile(s, 25),
        p75=lambda s: np.percentile(s, 75),
        mean="mean"
    ).reset_index()

    # Perfiles EMISFACT exactos de la Tabla B.1 (6 bloques de 4 horas, interpolación periódica suave)
    x_blk = np.array([2.5, 6.5, 10.5, 14.5, 18.5, 22.5, 26.5])
    perfiles_b1 = {
        "Fundición y metalurgia":    ([0.64, 0.96, 1.24, 1.25, 1.12, 0.79], C_RED,   "-",  "o"),
        "Calderas industriales":     ([0.68, 0.98, 1.21, 1.22, 1.09, 0.82], C_NAVY,  "--", "s"),
        "Hornos de vidrio y min.":   ([0.94, 0.98, 1.04, 1.05, 1.02, 0.97], C_GRAY,  ":",  "^"),
        "Turbinas de gas (CFE)":     ([0.81, 0.92, 1.02, 1.08, 1.19, 0.98], C_AMBER, "-.", "D"),
    }

    h_fine = np.linspace(1, 24, 240)
    h_eval = np.where(h_fine < 2.5, h_fine + 24.0, h_fine)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.2, 7.2), dpi=300, sharex=True,
                                   gridspec_kw={"height_ratios": [1.0, 1.05], "hspace": 0.14})

    # Sombreado de horarios escolares y colapso nocturno en ambos paneles
    for ax in (ax1, ax2):
        ax.axvspan(7, 14, color=C_TEAL, alpha=0.10, zorder=0)
        ax.axvspan(14, 20, color=C_AMBER, alpha=0.10, zorder=0)
        ax.axvspan(1, 7, color="#34495e", alpha=0.06, zorder=0)
        ax.axvspan(20, 24, color="#34495e", alpha=0.06, zorder=0)
        ax.grid(True, linestyle=":", alpha=0.45)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Panel A: Factores EMISFACT
    ax1.axhline(1.0, color="#4a5568", lw=1.0, ls="--", alpha=0.7, label="Emisión constante 24/7 (factor = 1.0)")
    for lbl, (vals, col, ls, mk) in perfiles_b1.items():
        y_per = np.array(vals + [vals[0]])
        cs = CubicSpline(x_blk, y_per, bc_type="periodic")
        ax1.plot(h_fine, cs(h_eval), color=col, ls=ls, lw=2.1, label=lbl, zorder=3)
        ax1.scatter(x_blk[:-1], vals, color=col, marker=mk, s=26, zorder=4)

    ax1.set_ylim(0.55, 1.38)
    ax1.set_ylabel("Factor horario EMISFACT ($f_{k,h}$)", fontsize=9.5, fontweight="bold")
    ax1.set_title("A. Perfiles horarios de operación industrial (EMISFACT, Tabla B.1) y jornadas escolares",
                  fontsize=10.5, fontweight="bold", color=C_DARK, loc="left", pad=8)
    ax1.legend(loc="lower center", ncol=3, fontsize=8.1, framealpha=0.94, edgecolor="#cbd5e0")

    # Etiquetas de turnos en la parte superior del Panel A
    ax1.text(4.0,  1.33, "Madrugada\n(inversión)", ha="center", va="top", fontsize=7.8, color="#4a5568", style="italic")
    ax1.text(10.5, 1.33, "Turno Matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.2, fontweight="bold", color="#116b50")
    ax1.text(17.0, 1.33, "Turno Vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.2, fontweight="bold", color="#9a3412")
    ax1.text(22.0, 1.33, "Noche", ha="center", va="top", fontsize=7.8, color="#4a5568", style="italic")

    # Panel B: Altura de mezcla real AERMET
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color=C_NAVY, alpha=0.20, label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=C_NAVY, lw=2.4, marker="o", ms=4,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    # Anotaciones físicas clave
    z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8, "med"].iloc[0])
    z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])
    ax2.annotate(f"Entrada matutina (07–08 h):\ncapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8), xytext=(2.2, 1380), fontsize=8.0,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_TEAL, lw=0.95),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.1))
    ax2.annotate(f"Cierre vespertino (18–20 h):\ncolapso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19), xytext=(15.8, 1750), fontsize=8.0,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_AMBER, lw=0.95),
                 arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.1))

    ax2.set_xlim(1, 24)
    ax2.set_xticks(range(1, 25, 2))
    ax2.set_xticklabels([f"{h:02d}:00" for h in range(1, 25, 2)], fontsize=8.5)
    ax2.set_xlabel("Hora local (convención hour-ending de AERMOD)", fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("Altura de capa de mezcla $Z_i$ (m)", fontsize=9.5, fontweight="bold")
    ax2.set_title("B. Ciclo diurno de la altura de la capa límite planetaria en la ZMVM (AERMET, estación AICM)",
                  fontsize=10.5, fontweight="bold", color=C_DARK, loc="left", pad=8)
    ax2.legend(loc="upper left", fontsize=8.3, framealpha=0.94, edgecolor="#cbd5e0")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cand3_emisfact_capa_limite.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cand3_emisfact_capa_limite.png")


# =====================================================================
# FIGURA CANDIDATA 4: ROSA DE VIENTOS AICM — ANUAL vs. 30 DÍAS PRE-PLANEA
# =====================================================================
def crear_fig4_rosa_vientos():
    fechas_planea = {
        2015: datetime.date(2015, 6, 17),
        2017: datetime.date(2017, 6, 14),
        2019: datetime.date(2019, 6, 11),
    }

    wd_anual = {}
    wd_30d   = {}
    ws_anual = {}
    ws_30d   = {}

    for yr, f_ex in fechas_planea.items():
        w_all, s_all, w_30, s_30 = [], [], [], []
        with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
            for line in f.readlines()[1:]:
                p = line.split()
                if len(p) >= 22:
                    mo, dy, hr = int(p[1]), int(p[2]), int(p[4])
                    ws, wd = float(p[15]), float(p[16])
                    if 0 < ws < 50 and 0 <= wd <= 360:
                        w_all.append(wd)
                        s_all.append(ws)
                        try:
                            dt = datetime.date(yr, mo, dy)
                            dias = (f_ex - dt).days
                            if 0 <= dias <= 30 and dt.weekday() < 5 and 7 <= hr <= 19:
                                w_30.append(wd)
                                s_30.append(ws)
                        except ValueError:
                            pass
        wd_anual[yr], ws_anual[yr] = np.array(w_all), np.array(s_all)
        wd_30d[yr],   ws_30d[yr]   = np.array(w_30),  np.array(s_30)

    n_bins = 16
    edges_deg = np.arange(0, 360, 360 / n_bins)
    angles = np.deg2rad(edges_deg)
    angles_closed = np.append(angles, angles[0])

    def freq_16(wd_arr):
        bins = np.floor(((wd_arr + (180 / n_bins)) % 360) / (360 / n_bins)).astype(int)
        counts = np.bincount(bins, minlength=n_bins)
        pct = 100.0 * counts / counts.sum()
        return np.append(pct, pct[0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.9), dpi=300,
                                   subplot_kw={"projection": "polar"})

    colores_yr = {2015: (C_NAVY, "-", "o"), 2017: (C_AMBER, "--", "s"), 2019: (C_RED, "-.", "^")}

    for ax, data_dict, titulo, subnota in [
        (ax1, wd_anual,
         "A. Promedio anual completo (8,760 h/año)",
         "Alta persistencia interanual\n→ IV anual débil (DE within = 0.051, F₁ = 2.64)"),
        (ax2, wd_30d,
         "B. Ventana crítica: 30 días previos a PLANEA (07–19 h)",
         "Variación direccional exógena entre años\n→ Primera etapa física relevante (F₁ = 9.2 a 12.6)"),
    ]:
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 45), ["N", "NE", "E", "SE", "S", "SO", "O", "NO"],
                          fontsize=9.5, fontweight="bold", color=C_DARK)

        rmax = 0
        for yr in [2015, 2017, 2019]:
            f_pct = freq_16(data_dict[yr])
            rmax = max(rmax, f_pct.max())
            col, ls, mk = colores_yr[yr]
            ax.plot(angles_closed, f_pct, color=col, ls=ls, lw=2.1, marker=mk, ms=4.2, label=str(yr))
            ax.fill(angles_closed, f_pct, color=col, alpha=0.07)

        ax.set_ylim(0, np.ceil(rmax / 4) * 4 + 2)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax.tick_params(axis="y", labelsize=8, colors="#4a5568")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title(titulo, fontsize=10.5, fontweight="bold", color=C_DARK, pad=18)
        ax.text(0.5, -0.15, subnota, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.4, color=C_DARK,
                bbox=dict(boxstyle="round,pad=0.35", fc=C_LIGHT, ec="#95a5a6", lw=0.85))

    # Anotación del cuadrante industrial en Panel A
    ax1.annotate("Corredor industrial\nN / NE (viento de origen)", xy=(np.deg2rad(22), 14),
                 xytext=(np.deg2rad(58), 21), fontsize=8.0, fontweight="bold", color="#7f0000",
                 arrowprops=dict(arrowstyle="->", color="#7f0000", lw=1.1))

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, [f"Levantamiento {l}" for l in labels], loc="upper center",
               bbox_to_anchor=(0.5, 0.99), ncol=3, fontsize=9.0, frameon=True, edgecolor="#cbd5e0")
    fig.suptitle("Distribución Direccional del Viento en la Cuenca de México (AICM, WMO 76679): Estabilidad Anual vs. Variación Pre-PLANEA",
                 fontsize=11.4, fontweight="bold", color=C_DARK, y=1.05)

    plt.tight_layout(rect=[0, 0.04, 1, 0.94])
    plt.savefig(f"{OUT_DIR}/fig_cand4_rosa_vientos_anual_vs_30d.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cand4_rosa_vientos_anual_vs_30d.png")


# =====================================================================
# FIGURA CANDIDATA 5: FOREST PLOT PILAR 1 (TWFE HETEROGENEIDAD + ROBUSTEZ)
# =====================================================================
def crear_fig5_forest_pilar1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.0), dpi=300)

    # Panel A: Efecto promedio y heterogeneidad por marginación (Tablas 3.1 y 3.2)
    items_A = [
        ("Promedio general\n(Todas, Tabla 3.1)",                6.695,  9.417,   5.603,  8.080),
        ("Baja o media marg.\n(Todas, β₁)",                     9.871,  9.580,   8.100,  8.147),
        ("Baja o media marg.\n(Públicas, β₁)",                  2.543,  8.856,   2.947,  5.170),
        ("Alta marginación\n(Todas, efecto total β₁+β₂)",     -89.406, 46.358, -69.995, 52.143),
        ("Alta marginación\n(Públicas, efecto total β₁+β₂)",  -95.756, 42.562, -53.568, 51.655),
    ]

    # Panel B: Robustez de la interacción en secundarias públicas (Tabla 3.3 Panel A)
    items_B = [
        ("(1) Especificación central\n(cluster RECID)",        -98.299, 43.271, -56.514, 51.794),
        ("(2) Errores agrupados\npor municipio",               -98.299, 32.783, -56.514, 43.936),
        ("(3) Efectos fijos\nmunicipio × año",                 -88.888, 44.721, -58.274, 57.205),
        ("(4) Sin controles\nmicroclimáticos",                 -98.620, 43.028, -54.289, 51.274),
        ("(5) Emisión constante\n24/7 (sin EMISFACT)",        -107.208, 46.641, -59.699, 55.027),
    ]

    def plot_forest(ax, items, title, xlabel, xlim):
        y_pos = np.arange(len(items))[::-1]
        ax.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
        ax.grid(axis="x", linestyle=":", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for idx, (lbl, b_l, se_l, b_m, se_m) in enumerate(items):
            y = y_pos[idx]
            # Lenguaje (arriba +0.16)
            ax.plot([b_l - 1.96*se_l, b_l + 1.96*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.4, zorder=3)
            ax.plot([b_l - 1.645*se_l, b_l + 1.645*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.2, zorder=4)
            ax.scatter([b_l], [y + 0.16], color=C_NAVY, s=58, zorder=5,
                       label="Lenguaje y Comunicación" if idx == 0 else None)
            ax.text(b_l, y + 0.31, f"{b_l:.1f}", ha="center", va="bottom",
                    fontsize=7.8, fontweight="bold", color=C_NAVY)

            # Matemáticas (abajo -0.16)
            ax.plot([b_m - 1.96*se_m, b_m + 1.96*se_m], [y - 0.16, y - 0.16], color=C_GRAY, lw=1.3, zorder=3)
            ax.plot([b_m - 1.645*se_m, b_m + 1.645*se_m], [y - 0.16, y - 0.16], color=C_GRAY, lw=2.8, zorder=4)
            ax.scatter([b_m], [y - 0.16], color=C_GRAY, marker="s", s=46, zorder=5,
                       label="Matemáticas" if idx == 0 else None)

        ax.set_yticks(y_pos)
        ax.set_yticklabels([x[0] for x in items], fontsize=8.4)
        ax.set_ylim(-0.6, len(items) - 0.35)
        ax.set_xlim(xlim)
        ax.set_xlabel(xlabel, fontsize=9.0, fontweight="bold")
        ax.set_title(title, fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)

    plot_forest(ax1, items_A,
                "A. Efecto promedio vs. heterogeneidad por marginación",
                r"Puntos PLANEA por +1 $\mu\mathrm{g/m}^3$ anual (IC 90% y 95%)", (-205, 65))
    plot_forest(ax2, items_B,
                "B. Robustez de la interacción (Alta Marg., públicas)",
                r"Interacción $\hat{\beta}_2$ por +1 $\mu\mathrm{g/m}^3$ anual (IC 90% y 95%)", (-215, 70))

    # Destacar las filas de alta marginación en Panel A
    ax1.axhspan(-0.52, 1.50, color=C_NAVY, alpha=0.05, zorder=0)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.99),
               ncol=2, fontsize=9.0, frameon=True, edgecolor="#cbd5e0")
    fig.suptitle("Pilar 1 (TWFE Anual): Efecto Regresivo Concentrado en Lenguaje y Estabilidad ante Especificaciones",
                 fontsize=11.5, fontweight="bold", color=C_DARK, y=1.05)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(f"{OUT_DIR}/fig_cand5_forest_pilar1_twfe.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cand5_forest_pilar1_twfe.png")


# =====================================================================
# FIGURA CANDIDATA 6: FOREST PLOT PILAR 2 (POSTFILE: FR + TWFE vs 2SLS)
# =====================================================================
def crear_fig6_forest_pilar2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 6.2), dpi=300)

    # Panel A: Forma reducida (puntos PLANEA por +1 DE de alineación del viento, Tabla 3.4)
    items_RF = [
        ("Todas públicas\n(30 d previos)",               -4.870, 1.928,  -1.432, 2.388),
        ("Baja o media marg.\n(30 d previos)",           -3.809, 2.195,  -1.067, 2.538),
        ("Alta marginación\n(30 d previos)",            -10.700, 4.823,  -4.910, 3.783),
        ("Alta marginación\n(30 d, Mun. × Año)",        -18.435, 7.819, -15.447, 6.888),
        ("Alta marginación\n(15 d previos)",             -6.931, 4.823,  -0.069, 5.003),
        ("Placebo: Alta marg.\n(30 d posteriores)",     -10.429, 8.186,  -6.846, 9.236),
    ]

    # Panel B: Comparación simétrica TWFE físico vs. 2SLS físico en Lenguaje (por +0.01 ug/m3)
    # (Se dividen betas y SE entre 100 para expresar en escala física real: +0.01 ug/m3)
    items_CMP = [
        ("Todas públicas\n(30 d, F₁=8.9)",               -1.03/100,   3.93/100,   -172.20/100,  89.71/100),
        ("Baja o media marg.\n(30 d, F₁=7.2)",           -0.33/100,   3.71/100,   -133.71/100, 101.33/100),
        ("Alta marginación\n(30 d, F₁=9.2)",            -41.59/100,  36.38/100,   -450.38/100, 163.98/100),
        ("Alta marginación\n(30 d, Mun.×Año, F₁=12.6)",  10.19/100,  56.37/100,  -1098.43/100, 504.96/100),
        ("Alta marginación\n(15 d, F₁=15.2)",           -46.82/100,  39.75/100,   -216.13/100, 138.63/100),
    ]

    # --- Dibujar Panel A (Forma Reducida) ---
    yA = np.arange(len(items_RF))[::-1]
    ax1.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
    ax1.grid(axis="x", linestyle=":", alpha=0.5)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.axhspan(-0.5, 0.5, color="#f8e6e8", alpha=0.45, zorder=0)

    for idx, (lbl, bl, sel, bm, sem) in enumerate(items_RF):
        y = yA[idx]
        ax1.plot([bl - 1.96*sel, bl + 1.96*sel], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.4, zorder=3)
        ax1.plot([bl - 1.645*sel, bl + 1.645*sel], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.2, zorder=4)
        ax1.scatter([bl], [y + 0.16], color=C_NAVY, s=55, zorder=5,
                    label="Lenguaje y Comunicación" if idx == 0 else None)
        ax1.text(bl, y + 0.30, f"{bl:.1f}", ha="center", va="bottom",
                 fontsize=7.7, fontweight="bold", color=C_NAVY)

        ax1.plot([bm - 1.96*sem, bm + 1.96*sem], [y - 0.16, y - 0.16], color=C_GRAY, lw=1.3, zorder=3)
        ax1.plot([bm - 1.645*sem, bm + 1.645*sem], [y - 0.16, y - 0.16], color=C_GRAY, lw=2.8, zorder=4)
        ax1.scatter([bm], [y - 0.16], color=C_GRAY, marker="s", s=44, zorder=5,
                    label="Matemáticas" if idx == 0 else None)

    ax1.set_yticks(yA)
    ax1.set_yticklabels([x[0] for x in items_RF], fontsize=8.3)
    ax1.set_ylim(-0.6, len(items_RF) - 0.3)
    ax1.set_xlim(-36, 13)
    ax1.set_xlabel("Puntos PLANEA por +1 DE de viento desfavorable (IC 90% y 95%)", fontsize=8.8, fontweight="bold")
    ax1.set_title("A. Forma reducida: efecto directo del choque de viento", fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)
    ax1.legend(loc="lower left", fontsize=8.2, framealpha=0.95, edgecolor="#cbd5e0")

    # --- Dibujar Panel B (Comparación simétrica TWFE vs 2SLS en Lenguaje) ---
    yB = np.arange(len(items_CMP))[::-1]
    ax2.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
    ax2.grid(axis="x", linestyle=":", alpha=0.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.axhspan(0.5, 2.5, color=C_LIGHT, alpha=0.8, zorder=0)

    for idx, (lbl, btw, setw, biv, seiv) in enumerate(items_CMP):
        y = yB[idx]
        # TWFE físico (arriba +0.16)
        ax2.plot([btw - 1.96*setw, btw + 1.96*setw], [y + 0.16, y + 0.16], color=C_GRAY, lw=1.4, zorder=3)
        ax2.plot([btw - 1.645*setw, btw + 1.645*setw], [y + 0.16, y + 0.16], color=C_GRAY, lw=3.0, zorder=4)
        ax2.scatter([btw], [y + 0.16], color=C_GRAY, marker="s", s=46, zorder=5,
                    label="TWFE físico (misma muestra POSTFILE)" if idx == 0 else None)

        # 2SLS físico (abajo -0.16)
        ax2.plot([biv - 1.96*seiv, biv + 1.96*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=1.5, zorder=3)
        ax2.plot([biv - 1.645*seiv, biv + 1.645*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=3.3, zorder=4)
        ax2.scatter([biv], [y - 0.16], color=C_RED, s=58, zorder=5,
                    label="2SLS físico (viento exógeno Q2015)" if idx == 0 else None)
        ax2.text(biv, y - 0.34, f"{biv:.2f}", ha="center", va="top",
                 fontsize=7.8, fontweight="bold", color=C_RED)

    ax2.set_yticks(yB)
    ax2.set_yticklabels([x[0] for x in items_CMP], fontsize=8.3)
    ax2.set_ylim(-0.65, len(items_CMP) - 0.35)
    ax2.set_xlim(-22.5, 3.5)
    ax2.set_xlabel(r"Puntos en Lenguaje por +0.01 $\mu\mathrm{g/m}^3$ en turno escolar (IC 90% y 95%)", fontsize=8.8, fontweight="bold")
    ax2.set_title("B. Atenuación TWFE vs. 2SLS físico en Lenguaje (POSTFILE)", fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)
    ax2.legend(loc="lower left", fontsize=8.2, framealpha=0.95, edgecolor="#cbd5e0")
    ax2.text(0.02, 0.24, "Nota: Placebo 2SLS (F₁=1.1)\nes nulo (p=0.406) y se omite\npor escala de IC amplio.",
             transform=ax2.transAxes, fontsize=7.6, color="#4a5568",
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cbd5e0", lw=0.8))

    fig.suptitle("Pilar 2 (AERMOD POSTFILE por Turno): Identificación Causal por Viento Exógeno y Atenuación del TWFE",
                 fontsize=11.4, fontweight="bold", color=C_DARK, y=1.01)

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cand6_forest_pilar2_postfile.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cand6_forest_pilar2_postfile.png")


if __name__ == "__main__":
    crear_fig1_pipeline()
    crear_fig2_cono_vs_radios()
    crear_fig3_emisfact_capa_limite()
    crear_fig4_rosa_vientos()
    crear_fig5_forest_pilar1()
    crear_fig6_forest_pilar2()
    print(f"\n[LISTO] Las 6 figuras candidatas se guardaron en: {OUT_DIR}")
