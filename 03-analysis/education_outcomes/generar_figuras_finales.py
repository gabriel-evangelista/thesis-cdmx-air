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
OUT_DIR    = f"{BASE}/figuras_tesis/finales"
os.makedirs(OUT_DIR, exist_ok=True)

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
# FIGURA 1 (TESIS - CAP. 2): PIPELINE METODOLÓGICO SIN SPOILERS
# =====================================================================
def crear_fig1_pipeline():
    fig, ax = plt.subplots(figsize=(13.8, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.35):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.55,rounding_size=1.4",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
        )
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 1.9, title, ha="center", va="top",
                fontsize=9.2, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w/2, y + (h - 2.6)/2, body, ha="center", va="center",
                fontsize=8.0, color=C_DARK, linespacing=1.32, zorder=4)

    def arrow(x1, y1, x2, y2, color="#4a5568", lw=1.35):
        a = FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
            color=color, linewidth=lw, zorder=2
        )
        ax.add_patch(a)

    # Etiquetas de capas a la izquierda
    capas = [
        (88.5, "1. INSUMOS\nPÚBLICOS"),
        (67.5, "2. PREPROCESO\nY PUENTE FÍSICO"),
        (46.0, "3. DISPERSIÓN\nATMOSFÉRICA"),
        (23.5, "4. IDENTIFICACIÓN\nECONOMÉTRICA"),
        (6.0,  "5. POLÍTICA\nPÚBLICA"),
    ]
    for yc, lbl in capas:
        ax.text(5.8, yc, lbl, ha="center", va="center", fontsize=8.2,
                fontweight="bold", color="#5d6d7e")

    # CAPA 1: 4 dominios (NOAA sin CENACE)
    box(13.0, 82.0, 19.5, 13.2, "RETC / COA (SEMARNAT)",
        "723 establecimientos (2015–2019)\n"
        r"$\mathrm{CO_2}$ como trazador de actividad" + "\n"
        "→ 285 fuentes fijas activas",
        fc="#fdf6f0", ec=C_AMBER, title_color="#9a3412")
    box(34.5, 82.0, 19.5, 13.2, "Meteorología (NOAA)",
        "ISD superficie + IGRA radiosondeo\n"
        "Estación AICM (WMO 76679)\n"
        "8,760 h/año (2015–2019)",
        fc="#f0f7fb", ec=C_NAVY, title_color=C_NAVY)
    box(56.0, 82.0, 19.5, 13.2, "Relieve (SRTM 30 m)",
        "4 mosaicos GeoTIFF (1 arc-seg)\n"
        "Cuenca de México y sierras\n"
        "Proyección UTM 14N (EPSG:32614)",
        fc="#f0f7fb", ec=C_NAVY, title_color=C_NAVY)
    box(77.5, 82.0, 20.5, 13.2, "PLANEA / SIGED (SEP–INEE)",
        "3° Secundaria (2015, 2017, 2019)\n"
        "3,833 CCT → 3,172 inmuebles\n"
        "2,392 inmuebles en Cuenca (9,459 obs.)",
        fc="#f2faf6", ec=C_TEAL, title_color="#116b50")

    # CAPA 2: Preprocesamiento (CENACE aquí en EMISFACT)
    box(13.0, 61.0, 26.5, 13.2, "Auditoría RETC y Puente AP-42",
        "Corrección de anomalías e imputación 2018\n"
        r"Conversión $\mathrm{CO_2 \rightarrow PM_{2.5}}$ en 6 familias AP-42" + "\n"
        "Chimeneas + perfiles EMISFACT (LBNL / CENACE)",
        fc="#ffffff", ec=C_AMBER, title_color="#9a3412")
    box(41.8, 61.0, 21.5, 13.2, "AERMET (Etapas 1–3)",
        r"Flujo de calor, $u_*$, longitud $L$," + "\n"
        r"capas límite convectiva ($Z_{ic}$) y mecánica" + "\n"
        r"→ Archivos .sfc/.pfl + controles $\mathbf{W}_{rt}$",
        fc="#ffffff", ec=C_NAVY, title_color=C_NAVY)
    box(65.5, 61.0, 32.5, 13.2, "AERMAP y Armonización Escolar",
        r"Elevación ($Z_{\mathrm{elev}}$) y altura crítica de colina ($Z_{\mathrm{hill}}$)" + "\n"
        "Deduplicación CCT ↔ RECID y turnos armonizados\n"
        "Puntajes estandarizados (media 500, DE 100)",
        fc="#ffffff", ec=C_TEAL, title_color="#116b50")

    # Flechas Capa 1 -> Capa 2 (sin flecha diagonal espuria)
    arrow(22.7, 81.6, 25.5, 74.7)
    arrow(44.2, 81.6, 52.5, 74.7)
    arrow(65.7, 81.6, 75.5, 74.7)
    arrow(87.7, 81.6, 86.0, 74.7)

    # CAPA 3: Motor AERMOD
    cont_aermod = FancyBboxPatch(
        (13.0, 38.5), 85.0, 15.2, boxstyle="round,pad=0.5,rounding_size=1.6",
        facecolor=C_LIGHT, edgecolor=C_NAVY, linewidth=1.5, linestyle="--", zorder=1
    )
    ax.add_patch(cont_aermod)
    ax.text(55.5, 52.5, r"MODELO REGULATORIO AERMOD (concentraciones de $\mathrm{PM_{2.5}}$ industrial a $z = 1.5\ \mathrm{m}$)",
            ha="center", va="center", fontsize=8.9, fontweight="bold", color=C_NAVY, zorder=4)

    box(15.5, 39.8, 38.0, 10.6, "Corrida Anual con EMISFACT + SRCGROUP",
        "Promedio anual (2015, 2017, 2019) por inmueble\n"
        "Desagregación por 5 ramas tecnológicas AP-42",
        fc="#ffffff", ec=C_NAVY, title_color=C_DARK, lw=1.1)
    box(57.5, 39.8, 38.0, 10.6, "Corrida Horaria POSTFILE (95 días pre/post PLANEA)",
        "Resolución 1 h (28 abr – 31 jul) filtrada al horario exacto\n"
        "de cada turno (matutino, vespertino, tiempo completo)",
        fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.1)

    arrow(26.2, 60.5, 34.5, 54.0)
    arrow(52.5, 60.5, 55.5, 54.0)
    arrow(81.7, 60.5, 76.5, 54.0)

    # CAPA 4: Dos Pilares (sin spoilers)
    box(13.0, 16.0, 40.5, 15.2, "Pilar 1: Panel Anual TWFE (pyfixest)",
        r"EF unidad ($\alpha_i$) + año ($\gamma_t$) / Mun.$\times$Año + controles $\mathbf{W}_{rt}$" + "\n"
        "• Efecto promedio metropolitano (MCO y TWFE)\n"
        "• Heterogeneidad por rama AP-42 y alta marginación\n"
        "• 5 especificaciones de robustez (clúster RECID / Mun.)",
        fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.4)
    box(57.5, 16.0, 40.5, 15.2, "Pilar 2: Identificación Causal 2SLS y Forma Reducida",
        r"Exposición física POSTFILE por turno (30 d previos, $\mu\mathrm{g/m}^3$)" + "\n"
        r"• Instrumento: alineación horaria de viento con $Q_{2015}$ fija" + "\n"
        "• Contraste simétrico TWFE vs. 2SLS (sesgo de atenuación)\n"
        "• Pruebas de mecanismo: 24 h vs. turno y placebo 30 d post.",
        fc="#fff8f8", ec=C_RED, title_color=C_RED, lw=1.4)

    arrow(34.5, 39.3, 33.2, 31.7, color=C_NAVY)
    arrow(76.5, 39.3, 77.7, 31.7, color=C_RED)

    # CAPA 5: Entregables de Política Pública (sin spoilers y bien contenido)
    box(13.0, 1.2, 85.0, 9.8, "Transferencia a Política Pública (ProAire ZMVM / SEP / SEDEMA)",
        "• Cartografía de hipervulnerabilidad escolar: focalización de mitigación de calidad del aire en aulas\n"
        "• Priorización regulatoria e inspección dirigida por rama tecnológica AP-42",
        fc="#eef6f2", ec=C_TEAL, title_color="#116b50", lw=1.4)

    arrow(33.2, 15.5, 42.0, 11.5, color=C_TEAL)
    arrow(77.7, 15.5, 69.0, 11.5, color=C_TEAL)

    ax.set_title("Arquitectura de Integración de Datos, Modelación Física (AERMOD) e Identificación Econométrica",
                 fontsize=12.0, fontweight="bold", color=C_DARK, pad=6)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cap2_pipeline_arquitectura.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap2_pipeline_arquitectura.png")


# =====================================================================
# FIGURA 2 (DEFENSA): CONO DE VIENTO vs. RADIOS CONCÉNTRICOS (PULIDA)
# =====================================================================
def crear_fig2_cono_vs_radios():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.8), dpi=300)

    grid = np.linspace(-3.4, 3.4, 320)
    X, Y = np.meshgrid(grid, grid)
    R = np.maximum(np.sqrt(X**2 + Y**2), 0.18)

    # Viento dominante NE -> SO
    wx, wy = -np.sqrt(0.5), -np.sqrt(0.5)
    cos_th = (X * wx + Y * wy) / R
    pluma = (np.maximum(0.0, cos_th) ** 10) / (R ** 1.35)
    pluma = np.where(R < 0.12, np.nan, pluma)
    pluma_norm = np.clip(pluma / np.nanpercentile(pluma[pluma > 0], 98.5), 0, 1)
    pluma_plot = np.where(pluma_norm >= 0.04, pluma_norm, np.nan)

    esc_A = (0.55, 0.55)
    esc_B = (-1.60, -1.55)
    esc_C = (-1.55, 1.55)

    for ax in (ax1, ax2):
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-3.4, 3.4)
        ax.set_aspect("equal")
        ax.set_xlabel("Distancia Este–Oeste desde la fuente (km)", fontsize=9.5)
        ax.set_ylabel("Distancia Norte–Sur desde la fuente (km)", fontsize=9.5)
        ax.grid(True, linestyle=":", alpha=0.45, color="#bdc3c7")
        ax.axhline(0, color="#cbd5e0", lw=0.7, zorder=1)
        ax.axvline(0, color="#cbd5e0", lw=0.7, zorder=1)

    # Panel A: Radios concéntricos
    c1 = plt.Circle((0, 0), 1.0, facecolor="#fed976", edgecolor=C_AMBER, alpha=0.35, lw=1.6, ls="--", zorder=2)
    c2 = plt.Circle((0, 0), 3.0, facecolor="#deebf7", edgecolor=C_NAVY, alpha=0.22, lw=1.4, ls="--", zorder=1)
    ax1.add_patch(c2)
    ax1.add_patch(c1)
    ax1.contourf(X, Y, pluma_plot, levels=np.linspace(0.04, 1.0, 12), cmap="Reds", alpha=0.28, zorder=2)

    ax1.scatter([0], [0], marker="^", s=155, c=C_DARK, edgecolors="white", lw=1.0, zorder=6)
    ax1.scatter(*esc_A, s=105, c=C_TEAL, edgecolors=C_DARK, lw=1.0, zorder=6)
    ax1.scatter(*esc_B, s=105, c=C_RED, edgecolors="white", lw=1.0, zorder=6)
    ax1.scatter(*esc_C, s=90,  c=C_NAVY, edgecolors="white", lw=1.0, zorder=6)

    ax1.annotate("Tratamiento ingenuo\n(r ≤ 1 km)", xy=(0.1, -0.98), xytext=(1.1, -1.75),
                 fontsize=8.2, fontweight="bold", color="#9a3412",
                 arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.1))
    ax1.annotate("Control ingenuo\n(1 < r ≤ 3 km)", xy=(2.1, -2.0), xytext=(1.05, -3.12),
                 fontsize=8.2, fontweight="bold", color=C_NAVY,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.1))

    ax1.annotate("Escuela A (0.8 km, barlovento)\nError Tipo I: aire limpio,\nclasificada como 'tratada'",
                 xy=esc_A, xytext=(0.55, 1.95), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_TEAL, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.1), zorder=7)
    ax1.annotate("Escuela B (2.2 km, sotavento)\nControl contaminado:\nrecibe la pluma de lleno",
                 xy=esc_B, xytext=(-3.25, -0.55), fontsize=7.9,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C_RED, lw=1.0),
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.1), zorder=7)
    ax1.set_title("A. Radios concéntricos tradicionales (sesgo por viento)", fontsize=10.3, fontweight="bold", color=C_DARK, pad=8)

    # Panel B: Cono direccional (flecha estilizada + escala limpia 0-1)
    levels_clean = np.linspace(0.0, 1.0, 21)
    cf = ax2.contourf(X, Y, pluma_plot, levels=levels_clean, vmin=0.0, vmax=1.0,
                      cmap="YlOrRd", alpha=0.84, zorder=2)
    ax2.contour(X, Y, pluma_norm, levels=[0.08], colors=C_RED, linewidths=1.1, linestyles="--", zorder=3)
    ax2.add_patch(plt.Circle((0, 0), 1.0, fill=False, edgecolor="#cbd5e0", lw=0.9, ls=":", zorder=2))
    ax2.add_patch(plt.Circle((0, 0), 3.0, fill=False, edgecolor="#cbd5e0", lw=0.9, ls=":", zorder=2))

    # Flecha limpia y proporcionada con FancyArrowPatch
    wind_arrow = FancyArrowPatch((0, 0), (-2.55, -2.55), arrowstyle="-|>",
                                 mutation_scale=16, color=C_DARK, lw=2.1, zorder=5)
    ax2.add_patch(wind_arrow)
    ax2.text(-2.72, -2.96, r"Vector de viento $\vec{w}$" + "\n(NE → SO)", fontsize=8.3,
             fontweight="bold", color=C_DARK, ha="center")

    # Rayo y ángulo theta
    ax2.plot([0, -2.25], [0, -1.35], color=C_NAVY, lw=1.25, ls="-.", zorder=5)
    arc = patches.Arc((0, 0), 2.1, 2.1, angle=0, theta1=211.0, theta2=225.0, color=C_NAVY, lw=1.7, zorder=6)
    ax2.add_patch(arc)
    ax2.text(-1.26, -0.96, r"$\theta$", fontsize=10.5, fontweight="bold", color=C_NAVY, zorder=7)

    ax2.scatter([0], [0], marker="^", s=155, c=C_DARK, edgecolors="white", lw=1.0, zorder=6)
    ax2.scatter(*esc_A, s=105, c=C_TEAL, edgecolors=C_DARK, lw=1.0, zorder=6)
    ax2.scatter(*esc_B, s=105, c=C_RED, edgecolors="white", lw=1.0, zorder=6)
    ax2.scatter(*esc_C, s=90,  c=C_NAVY, edgecolors="white", lw=1.0, zorder=6)

    ax2.annotate("Escuela A (barlovento)\nExposición ≈ 0\n" + r"($\cos\theta < 0$)",
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

    ax2.text(-3.22, 0.25, "Cono a sotavento (Ec. 3.6):\n" + r"$\max\{0,\cos\theta\}^{10}\ /\ d^{1.5}$",
             fontsize=8.6, color=C_DARK,
             bbox=dict(boxstyle="round,pad=0.38", fc="#fffdf7", ec=C_AMBER, lw=0.95), zorder=7)

    cbar = plt.colorbar(cf, ax=ax2, fraction=0.044, pad=0.03, ticks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cbar.set_label("Exposición relativa (adimensional, 0–1)", fontsize=8.6)
    cbar.ax.tick_params(labelsize=8.2)
    ax2.set_title("B. Dispersión direccional (AERMOD + cono de viento)", fontsize=10.3, fontweight="bold", color=C_DARK, pad=8)

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_defensa_cono_viento_vs_radios.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_defensa_cono_viento_vs_radios.png")


# =====================================================================
# FIGURA 3 (TESIS - CAP. 3.1.1): EMISFACT + CAPA LÍMITE AERMET (PULIDA)
# =====================================================================
def crear_fig3_emisfact_capa_limite():
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
                    filas.append((hr, z_eff))
    df_pbl = pd.DataFrame(filas, columns=["hr", "z_eff"]).dropna()
    pbl_stats = df_pbl.groupby("hr")["z_eff"].agg(
        med="median",
        p25=lambda s: np.percentile(s, 25),
        p75=lambda s: np.percentile(s, 75),
    ).reset_index()

    x_blk = np.array([2.5, 6.5, 10.5, 14.5, 18.5, 22.5, 26.5])
    # Paleta totalmente desacoplada de la atmósfera (azul marino) y de los fondos neutros
    perfiles_b1 = {
        "Fundición y metalurgia":  ([0.64, 0.96, 1.24, 1.25, 1.12, 0.79], "#c0392b", "-",  "o"),
        "Calderas industriales":   ([0.68, 0.98, 1.21, 1.22, 1.09, 0.82], "#2e7d32", "--", "s"),
        "Hornos de vidrio y min.": ([0.94, 0.98, 1.04, 1.05, 1.02, 0.97], "#d95f02", (0, (3, 1.5)), "^"),
        "Turbinas de gas (CFE)":   ([0.81, 0.92, 1.02, 1.08, 1.19, 0.98], "#7b2cbf", "-.", "D"),
    }

    h_fine = np.linspace(1, 24, 240)
    h_eval = np.where(h_fine < 2.5, h_fine + 24.0, h_fine)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.4, 7.8), dpi=300, sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.08], "hspace": 0.30}
    )

    # Fondos neutros suaves y líneas divisorias de turnos
    for ax in (ax1, ax2):
        ax.axvspan(1, 7,   color="#eef2f6", alpha=0.65, zorder=0)
        ax.axvspan(7, 14,  color="#f7fafc", alpha=0.80, zorder=0)
        ax.axvspan(14, 20, color="#faf6f0", alpha=0.80, zorder=0)
        ax.axvspan(20, 24, color="#eef2f6", alpha=0.65, zorder=0)
        for xv in (7, 14, 20):
            ax.axvline(xv, color="#94a3b8", ls=":", lw=1.0, zorder=1)
        ax.grid(axis="y", linestyle=":", alpha=0.45)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Panel A: Factores EMISFACT
    ax1.axhline(1.0, color="#7f8c8d", lw=1.2, ls=":", alpha=0.9, label="Emisión constante 24/7 (factor = 1.0)")
    for lbl, (vals, col, ls, mk) in perfiles_b1.items():
        y_per = np.array(vals + [vals[0]])
        cs = CubicSpline(x_blk, y_per, bc_type="periodic")
        ax1.plot(h_fine, cs(h_eval), color=col, ls=ls, lw=2.15, label=lbl, zorder=3)
        ax1.scatter(x_blk[:-1], vals, color=col, marker=mk, s=28, zorder=4)

    ax1.set_ylim(0.55, 1.48)
    ax1.set_ylabel("Factor horario EMISFACT ($f_{k,h}$)", fontsize=9.5, fontweight="bold")
    ax1.set_title("A. Perfiles horarios de operación industrial (EMISFACT, Tabla B.1) y jornadas escolares",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=8)
    ax1.legend(loc="lower center", ncol=3, fontsize=8.1, framealpha=0.96, edgecolor="#cbd5e0")

    # Encabezados de franjas bien arriba de la curva roja
    ax1.text(4.0,  1.44, "Madrugada\n(inversión)", ha="center", va="top", fontsize=7.9, color="#64748b", style="italic")
    ax1.text(10.5, 1.44, "Turno Matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.3, fontweight="bold", color="#334155")
    ax1.text(17.0, 1.44, "Turno Vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.3, fontweight="bold", color="#334155")
    ax1.text(22.0, 1.44, "Noche", ha="center", va="top", fontsize=7.9, color="#64748b", style="italic")

    # Panel B: Capa límite atmosférica (azul exclusivo)
    C_ATM = "#1f4e79"
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color=C_ATM, alpha=0.20, label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=C_ATM, lw=2.4, marker="o", ms=4,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8,  "med"].iloc[0])
    z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])

    # Cajas bien separadas de la leyenda y del título
    ax2.annotate(f"Entrada matutina (07–08 h):\ncapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8), xytext=(1.8, 1020), fontsize=8.1, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#475569", lw=0.95),
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.15), zorder=5)
    ax2.annotate(f"Cierre vespertino (18–20 h):\ndescenso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19), xytext=(14.9, 1740), fontsize=8.1, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#475569", lw=0.95),
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.15), zorder=5)

    ax2.set_xlim(1, 24)
    ax2.set_ylim(0, 2180)
    ax2.set_xticks(range(1, 25, 2))
    ax2.set_xticklabels([f"{h:02d}:00" for h in range(1, 25, 2)], fontsize=8.5)
    ax2.set_xlabel("Hora local (convención hour-ending de AERMOD)", fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("Altura de capa de mezcla $Z_i$ (m)", fontsize=9.5, fontweight="bold")
    ax2.set_title("B. Ciclo diurno de la altura de la capa límite planetaria en la ZMVM (AERMET, estación AICM)",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax2.legend(loc="upper left", fontsize=8.3, framealpha=0.96, edgecolor="#cbd5e0")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cap3_emisfact_capa_limite.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_emisfact_capa_limite.png")


# =====================================================================
# FIGURA 4 (TESIS - CAP. 3.1.4): ROSA DE VIENTOS (GRADIENTE + ESCALA 0–20%)
# =====================================================================
def crear_fig4_rosa_vientos():
    fechas_planea = {
        2015: datetime.date(2015, 6, 17),
        2017: datetime.date(2017, 6, 14),
        2019: datetime.date(2019, 6, 11),
    }

    wd_anual, wd_30d = {}, {}
    for yr, f_ex in fechas_planea.items():
        w_all, w_30 = [], []
        with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
            for line in f.readlines()[1:]:
                p = line.split()
                if len(p) >= 22:
                    mo, dy, hr = int(p[1]), int(p[2]), int(p[4])
                    ws, wd = float(p[15]), float(p[16])
                    if 0 < ws < 50 and 0 <= wd <= 360:
                        w_all.append(wd)
                        try:
                            dt = datetime.date(yr, mo, dy)
                            dias = (f_ex - dt).days
                            if 0 <= dias <= 30 and dt.weekday() < 5 and 7 <= hr <= 19:
                                w_30.append(wd)
                        except ValueError:
                            pass
        wd_anual[yr], wd_30d[yr] = np.array(w_all), np.array(w_30)

    n_bins = 16
    edges_deg = np.arange(0, 360, 360 / n_bins)
    angles = np.deg2rad(edges_deg)
    angles_closed = np.append(angles, angles[0])

    def freq_16(wd_arr):
        bins = np.floor(((wd_arr + (180 / n_bins)) % 360) / (360 / n_bins)).astype(int)
        counts = np.bincount(bins, minlength=n_bins)
        pct = 100.0 * counts / counts.sum()
        return np.append(pct, pct[0])

    # Gradiente secuencial cronológico azul -> índigo -> púrpura profundo
    colores_yr = {
        2015: ("#3898ec", "-",  "o"),
        2017: ("#635bff", "--", "s"),
        2019: ("#581c87", "-.", "^"),
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 6.0), dpi=300,
                                   subplot_kw={"projection": "polar"})

    for ax, data_dict, titulo, subnota in [
        (ax1, wd_anual,
         "A. Promedio anual completo (8,760 h/año)",
         "Alta persistencia interanual\n" + r"$\rightarrow$ IV anual débil ($\mathrm{DE_{within}} = 0.051$, $F_1 = 2.64$)"),
        (ax2, wd_30d,
         "B. Ventana crítica: 30 días previos a PLANEA (07–19 h)",
         "Variación direccional exógena entre años\n" + r"$\rightarrow$ Primera etapa física relevante ($F_1 = 9.2$ a $12.6$)"),
    ]:
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 45), ["N", "NE", "E", "SE", "S", "SO", "O", "NO"],
                          fontsize=9.5, fontweight="bold", color=C_DARK)

        for yr in [2015, 2017, 2019]:
            f_pct = freq_16(data_dict[yr])
            col, ls, mk = colores_yr[yr]
            ax.plot(angles_closed, f_pct, color=col, ls=ls, lw=2.15, marker=mk, ms=4.3, label=str(yr))
            ax.fill(angles_closed, f_pct, color=col, alpha=0.08)

        # Escala radial idéntica (0% a 20%) y etiquetas en cuadrante NO (despejado)
        ax.set_ylim(0, 20)
        ax.set_yticks([5, 10, 15, 20])
        ax.set_yticklabels(["5%", "10%", "15%", "20%"], fontsize=8.0, color="#4a5568")
        ax.set_rlabel_position(315)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title(titulo, fontsize=10.5, fontweight="bold", color=C_DARK, pad=18)
        ax.text(0.5, -0.15, subnota, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.4, color=C_DARK,
                bbox=dict(boxstyle="round,pad=0.38", fc=C_LIGHT, ec="#95a5a6", lw=0.85))

    # Señalar dinámicamente el lóbulo dominante real en el Panel A
    avg_anual = np.mean([freq_16(wd_anual[y])[:-1] for y in [2015, 2017, 2019]], axis=0)
    idx_pk = int(np.argmax(avg_anual))
    ang_pk = angles[idx_pk]
    rad_pk = avg_anual[idx_pk]
    ax1.annotate("Corredor industrial\nNE / ENE (viento dominante)",
                 xy=(ang_pk, rad_pk), xytext=(np.deg2rad(52), 24.5),
                 fontsize=8.1, fontweight="bold", color="#581c87",
                 annotation_clip=False,
                 arrowprops=dict(arrowstyle="->", color="#581c87", lw=1.25))

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, [f"Levantamiento {l}" for l in labels], loc="upper center",
               bbox_to_anchor=(0.5, 0.99), ncol=3, fontsize=9.0, frameon=True, edgecolor="#cbd5e0")
    fig.suptitle("Distribución Direccional del Viento en la Cuenca de México (AICM, WMO 76679): Estabilidad Anual vs. Variación Pre-PLANEA",
                 fontsize=11.4, fontweight="bold", color=C_DARK, y=1.05)

    plt.tight_layout(rect=[0, 0.04, 1, 0.94])
    plt.savefig(f"{OUT_DIR}/fig_cap3_rosa_vientos_anual_vs_30d.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_rosa_vientos_anual_vs_30d.png")


# =====================================================================
# FIGURA 5 (TESIS - CAP. 3.2): FOREST PLOT PILAR 1 (TWFE, PULIDA)
# =====================================================================
def crear_fig5_forest_pilar1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 6.2), dpi=300)

    items_A = [
        ("Promedio general\n(Todas, Tabla 3.1)",                             6.695,  9.417,   5.603,  8.080),
        ("Baja o media marg.\n" + r"(Todas, $\beta_1$)",                     9.871,  9.580,   8.100,  8.147),
        ("Baja o media marg.\n" + r"(Públicas, $\beta_1$)",                  2.543,  8.856,   2.947,  5.170),
        ("Alta marginación\n" + r"(Todas, efecto total $\hat{\beta}_1+\hat{\beta}_2$)",    -89.406, 46.358, -69.995, 52.143),
        ("Alta marginación\n" + r"(Públicas, efecto total $\hat{\beta}_1+\hat{\beta}_2$)", -95.756, 42.562, -53.568, 51.655),
    ]

    items_B = [
        ("(1) Especificación central\n(clúster RECID)",       -98.299, 43.271, -56.514, 51.794),
        ("(2) Errores agrupados\npor municipio",              -98.299, 32.783, -56.514, 43.936),
        ("(3) Efectos fijos\nmunicipio × año",                -88.888, 44.721, -58.274, 57.205),
        ("(4) Sin controles\nmicroclimáticos",                -98.620, 43.028, -54.289, 51.274),
        ("(5) Emisión constante\n24/7 (sin EMISFACT)",       -107.208, 46.641, -59.699, 55.027),
    ]

    def plot_forest(ax, items, title, xlabel, xlim):
        y_pos = np.arange(len(items))[::-1]
        ax.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
        ax.grid(axis="x", linestyle=":", alpha=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for idx, (lbl, b_l, se_l, b_m, se_m) in enumerate(items):
            y = y_pos[idx]
            ax.plot([b_l - 1.96*se_l, b_l + 1.96*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.4, zorder=3)
            ax.plot([b_l - 1.645*se_l, b_l + 1.645*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.2, zorder=4)
            ax.scatter([b_l], [y + 0.16], color=C_NAVY, s=58, zorder=5,
                       label="Lenguaje y Comunicación" if idx == 0 else None)

            # Evitar choque con la línea punteada en x = 0
            x_txt = b_l + 5.5 if -4 <= b_l <= 14 else b_l
            ha_txt = "left" if -4 <= b_l <= 14 else "center"
            ax.text(x_txt, y + 0.30, f"{b_l:.1f}", ha=ha_txt, va="bottom",
                    fontsize=7.9, fontweight="bold", color=C_NAVY,
                    bbox=dict(boxstyle="square,pad=0.06", fc="white", ec="none", alpha=0.85), zorder=6)

            ax.plot([b_m - 1.96*se_m, b_m + 1.96*se_m], [y - 0.16, y - 0.16], color=C_GRAY, lw=1.3, zorder=3)
            ax.plot([b_m - 1.645*se_m, b_m + 1.645*se_m], [y - 0.16, y - 0.16], color=C_GRAY, lw=2.8, zorder=4)
            ax.scatter([b_m], [y - 0.16], color=C_GRAY, marker="s", s=46, zorder=5,
                       label="Matemáticas" if idx == 0 else None)

        ax.set_yticks(y_pos)
        ax.set_yticklabels([x[0] for x in items], fontsize=8.4)
        ax.set_ylim(-0.6, len(items) - 0.3)
        ax.set_xlim(xlim)
        ax.set_xlabel(xlabel, fontsize=9.0, fontweight="bold")
        ax.set_title(title, fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)

    plot_forest(ax1, items_A,
                "A. Efecto promedio vs. heterogeneidad por marginación",
                r"Puntos PLANEA por $+1\ \mu\mathrm{g/m}^3$ anual", (-210, 65))
    plot_forest(ax2, items_B,
                "B. Robustez de la interacción (Alta Marg., públicas)",
                r"Interacción $\hat{\beta}_2$ por $+1\ \mu\mathrm{g/m}^3$ anual", (-220, 75))

    ax1.axhspan(-0.52, 1.50, color=C_NAVY, alpha=0.055, zorder=0)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.98),
               ncol=2, fontsize=9.0, frameon=True, edgecolor="#cbd5e0")
    fig.suptitle("Pilar 1 (TWFE Anual): Efecto Regresivo Concentrado en Lenguaje y Estabilidad ante Especificaciones",
                 fontsize=11.5, fontweight="bold", color=C_DARK, y=1.04)
    fig.text(0.5, -0.01, "Nota: Los marcadores muestran el coeficiente puntual; la barra gruesa indica el intervalo de confianza al 90% y la barra delgada al 95%.",
             ha="center", va="top", fontsize=8.2, color="#4a5568", style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.93])
    plt.savefig(f"{OUT_DIR}/fig_cap3_forest_pilar1_twfe.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_forest_pilar1_twfe.png")


# =====================================================================
# FIGURA 6 (TESIS - CAP. 3.2): FOREST PLOT PILAR 2 (POSTFILE, SIN CHOQUES)
# =====================================================================
def crear_fig6_forest_pilar2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 6.4), dpi=300)

    items_RF = [
        ("Todas públicas\n(30 d previos)",               -4.870, 1.928,  -1.432, 2.388),
        ("Baja o media marg.\n(30 d previos)",           -3.809, 2.195,  -1.067, 2.538),
        ("Alta marginación\n(30 d previos)",            -10.700, 4.823,  -4.910, 3.783),
        ("Alta marginación\n(30 d, Mun. × Año)",        -18.435, 7.819, -15.447, 6.888),
        ("Alta marginación\n(15 d previos)",             -6.931, 4.823,  -0.069, 5.003),
        ("Placebo: Alta marg.\n(30 d posteriores)",     -10.429, 8.186,  -6.846, 9.236),
    ]

    items_CMP = [
        ("Todas públicas\n" + r"(30 d, $F_1 = 8.9$)",               -1.03/100,   3.93/100,   -172.20/100,  89.71/100),
        ("Baja o media marg.\n" + r"(30 d, $F_1 = 7.2$)",           -0.33/100,   3.71/100,   -133.71/100, 101.33/100),
        ("Alta marginación\n" + r"(30 d, $F_1 = 9.2$)",            -41.59/100,  36.38/100,   -450.38/100, 163.98/100),
        ("Alta marginación\n" + r"(30 d, Mun.$\times$Año, $F_1 = 12.6$)", 10.19/100, 56.37/100, -1098.43/100, 504.96/100),
        ("Alta marginación\n" + r"(15 d, $F_1 = 15.2$)",           -46.82/100,  39.75/100,   -216.13/100, 138.63/100),
    ]

    # --- Panel A: Forma Reducida (leyenda en upper left, totalmente despejado) ---
    yA = np.arange(len(items_RF))[::-1]
    ax1.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
    ax1.grid(axis="x", linestyle=":", alpha=0.5)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.axhspan(-0.52, 0.50, color="#f8e6e8", alpha=0.55, zorder=0)

    for idx, (lbl, bl, sel, bm, sem) in enumerate(items_RF):
        y = yA[idx]
        ax1.plot([bl - 1.96*sel, bl + 1.96*sel], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.4, zorder=3)
        ax1.plot([bl - 1.645*sel, bl + 1.645*sel], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.2, zorder=4)
        ax1.scatter([bl], [y + 0.16], color=C_NAVY, s=55, zorder=5,
                    label="Lenguaje y Comunicación" if idx == 0 else None)
        ax1.text(bl, y + 0.30, f"{bl:.1f}", ha="center", va="bottom",
                 fontsize=7.8, fontweight="bold", color=C_NAVY)

        ax1.plot([bm - 1.96*sem, bm + 1.96*sem], [y - 0.16, y - 0.16], color=C_GRAY, lw=1.3, zorder=3)
        ax1.plot([bm - 1.645*sem, bm + 1.645*sem], [y - 0.16, y - 0.16], color=C_GRAY, lw=2.8, zorder=4)
        ax1.scatter([bm], [y - 0.16], color=C_GRAY, marker="s", s=44, zorder=5,
                    label="Matemáticas" if idx == 0 else None)

    ax1.set_yticks(yA)
    ax1.set_yticklabels([x[0] for x in items_RF], fontsize=8.3)
    ax1.set_ylim(-0.62, len(items_RF) - 0.28)
    ax1.set_xlim(-36, 14)
    ax1.set_xlabel("Puntos PLANEA por +1 DE de viento desfavorable", fontsize=8.9, fontweight="bold")
    ax1.set_title("A. Forma reducida: efecto directo del choque de viento", fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)
    ax1.legend(loc="upper left", fontsize=8.3, framealpha=0.96, edgecolor="#cbd5e0")

    # --- Panel B: TWFE físico vs. 2SLS físico (leyenda en upper left, nota en lower left) ---
    yB = np.arange(len(items_CMP))[::-1]
    ax2.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
    ax2.grid(axis="x", linestyle=":", alpha=0.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.axhspan(0.50, 2.50, color=C_LIGHT, alpha=0.85, zorder=0)

    for idx, (lbl, btw, setw, biv, seiv) in enumerate(items_CMP):
        y = yB[idx]
        ax2.plot([btw - 1.96*setw, btw + 1.96*setw], [y + 0.16, y + 0.16], color=C_GRAY, lw=1.4, zorder=3)
        ax2.plot([btw - 1.645*setw, btw + 1.645*setw], [y + 0.16, y + 0.16], color=C_GRAY, lw=3.0, zorder=4)
        ax2.scatter([btw], [y + 0.16], color=C_GRAY, marker="s", s=46, zorder=5,
                    label="TWFE físico (misma muestra POSTFILE)" if idx == 0 else None)

        ax2.plot([biv - 1.96*seiv, biv + 1.96*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=1.5, zorder=3)
        ax2.plot([biv - 1.645*seiv, biv + 1.645*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=3.3, zorder=4)
        ax2.scatter([biv], [y - 0.16], color=C_RED, s=58, zorder=5,
                    label=r"2SLS físico (viento exógeno $Q_{2015}$)" if idx == 0 else None)
        ax2.text(biv, y - 0.34, f"{biv:.2f}", ha="center", va="top",
                 fontsize=7.9, fontweight="bold", color=C_RED)

    ax2.set_yticks(yB)
    ax2.set_yticklabels([x[0] for x in items_CMP], fontsize=8.3)
    ax2.set_ylim(-0.68, len(items_CMP) - 0.32)
    ax2.set_xlim(-22.5, 3.8)
    ax2.set_xlabel(r"Puntos en Lenguaje por $+0.01\ \mu\mathrm{g/m}^3$ en turno escolar", fontsize=8.9, fontweight="bold")
    ax2.set_title("B. Atenuación TWFE vs. 2SLS físico en Lenguaje (POSTFILE)", fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)
    ax2.legend(loc="upper left", fontsize=8.2, framealpha=0.96, edgecolor="#cbd5e0")

    ax2.text(0.02, 0.03,
             r"Nota: Placebo 2SLS ($F_1 = 1.1$)" + "\nes nulo ($p = 0.406$) y se omite\npor amplitud del intervalo.",
             transform=ax2.transAxes, ha="left", va="bottom", fontsize=7.6, color="#4a5568",
             bbox=dict(boxstyle="round,pad=0.32", fc="white", ec="#cbd5e0", lw=0.85), zorder=6)

    fig.suptitle("Pilar 2 (AERMOD POSTFILE por Turno): Identificación Causal por Viento Exógeno y Atenuación del TWFE",
                 fontsize=11.4, fontweight="bold", color=C_DARK, y=1.01)
    fig.text(0.5, -0.01, "Nota: Los marcadores muestran el coeficiente puntual; la barra gruesa indica el intervalo de confianza al 90% y la barra delgada al 95%.",
             ha="center", va="top", fontsize=8.2, color="#4a5568", style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.savefig(f"{OUT_DIR}/fig_cap3_forest_pilar2_postfile.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_forest_pilar2_postfile.png")


if __name__ == "__main__":
    crear_fig1_pipeline()
    crear_fig2_cono_vs_radios()
    crear_fig3_emisfact_capa_limite()
    crear_fig4_rosa_vientos()
    crear_fig5_forest_pilar1()
    crear_fig6_forest_pilar2()
    print(f"\n[LISTO] Las 6 figuras pulidas se guardaron en: {OUT_DIR}")
