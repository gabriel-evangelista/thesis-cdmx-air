import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle
from matplotlib.ticker import AutoMinorLocator
from scipy.interpolate import CubicSpline

BASE       = "/Users/gabrielevangelista/thesis-cdmx-air"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
OUT_DIR    = f"{BASE}/figuras_tesis/finales"
os.makedirs(OUT_DIR, exist_ok=True)

C_NAVY     = "#005a9c"
C_RED      = "#b2182b"
C_DARK     = "#1a202c"
C_LINE     = "#4a72a8"
C_PILL1    = "#e6eefb"
C_PILL2    = "#d0def8"
C_MUTED    = "#64748b"
C_MATH     = "#8c96a0"
C_TWFE_BAR = "#6baed6"


# =====================================================================
# FIGURA 2.1: PIPELINE DE ARQUITECTURA (SIN JERGAS NI METÁFORAS)
# =====================================================================
def crear_fig21_pipeline():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "mathtext.fontset": "dejavusans",
        "font.size": 10,
    })

    fig, ax = plt.subplots(figsize=(11.4, 7.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def parallelogram(x, y, w, h, title, body, slant=1.4, fc="#f5f8fe", ec=C_LINE):
        verts = [(x, y), (x + w - slant, y), (x + w, y + h), (x + slant, y + h)]
        p = Polygon(verts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.25, zorder=3)
        ax.add_patch(p)
        ax.text(x + w/2 + 0.15, y + h - 1.8, title, ha="center", va="top",
                fontsize=8.4, fontweight="bold", color=C_DARK, zorder=4)
        ax.text(x + w/2, y + (h - 2.6)/2, body, ha="center", va="center",
                fontsize=7.45, color="#2d3748", linespacing=1.28, zorder=4)

    def rect_box(x, y, w, h, title, body, fc="#ffffff", ec=C_LINE, title_color=C_DARK,
                 lw=1.25, accent_top=None, title_fs=8.5):
        p = Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
        ax.add_patch(p)
        if accent_top is not None:
            bar = Rectangle((x, y + h - 0.85), w, 0.85, facecolor=accent_top, edgecolor="none", zorder=4)
            ax.add_patch(bar)
        ax.text(x + w/2, y + h - (2.1 if accent_top else 1.7), title, ha="center", va="top",
                fontsize=title_fs, fontweight="bold", color=title_color, zorder=5)
        ax.text(x + w/2, y + (h - (2.9 if accent_top else 2.5))/2, body, ha="center", va="center",
                fontsize=7.65, color="#2d3748", linespacing=1.28, zorder=5)

    def pill_box(x, y, w, h, title, body, fc=C_PILL2, ec=C_LINE, title_color=C_DARK, lw=1.4):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.35,rounding_size=3.2",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
        )
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 1.6, title, ha="center", va="top",
                fontsize=8.7, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w/2, y + (h - 2.4)/2, body, ha="center", va="center",
                fontsize=7.75, color=C_DARK, linespacing=1.30, zorder=4)

    def arrow(x1, y1, x2, y2, color=C_LINE, lw=1.3):
        a = FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
            color=color, linewidth=lw, zorder=2
        )
        ax.add_patch(a)

    capas = [
        (89.5, "1. INSUMOS\nPÚBLICOS"),
        (69.5, "2. PREPROCESO\nY PUENTE FÍSICO"),
        (48.5, "3. DISPERSIÓN\nATMOSFÉRICA"),
        (26.5, "4. IDENTIFICACIÓN\nECONOMÉTRICA"),
        (9.5,  "5. POLÍTICA\nPÚBLICA"),
    ]
    for yc, lbl in capas:
        ax.text(5.8, yc, lbl, ha="center", va="center", fontsize=7.7,
                fontweight="bold", color="#4a5568")

    # CAPA 1: Insumos
    parallelogram(12.5, 83.2, 20.4, 12.6, "RETC / COA (SEMARNAT)",
                  "723 plantas (2015–2019)\n" + r"$\mathrm{CO_2}$ como trazador" + "\n→ 285 fuentes activas")
    parallelogram(34.2, 83.2, 20.4, 12.6, "Meteorología (NOAA)",
                  "ISD superficie + IGRA\nAICM (WMO 76679)\n8,760 h/año (2015–2019)")
    parallelogram(55.9, 83.2, 20.4, 12.6, "Relieve (SRTM 30 m)",
                  "4 mosaicos GeoTIFF\nCuenca de México\nUTM 14N (EPSG:32614)")
    parallelogram(77.6, 83.2, 21.0, 12.6, "PLANEA / SIGED (SEP)",
                  "3° Sec. (2015, 2017, 2019)\n3,833 CCT → 3,172 edificios\n2,392 Cuenca (9,459 obs.)")

    # CAPA 2: Preprocesamiento
    rect_box(13.0, 63.0, 27.2, 13.0, "Auditoría RETC y puente AP-42",
             "Depuración e imputación 2018\n"
             r"Conversión $\mathrm{CO_2 \rightarrow PM_{2.5}}$ (6 familias)" + "\n"
             "Chimeneas y perfiles horarios (LBNL/CENACE)")
    rect_box(42.0, 63.0, 21.6, 13.0, "AERMET (etapas 1–3)",
             r"Flujo de calor, $u_*$, longitud $L$," + "\n"
             r"capas límite ($Z_{ic}, Z_{im}$)" + "\n"
             r"→ .sfc/.pfl + controles $\mathbf{W}_{rt}$")
    rect_box(65.4, 63.0, 32.8, 13.0, "AERMAP y armonización escolar",
             r"Elevación ($Z_{\mathrm{elev}}$) y colina ($Z_{\mathrm{hill}}$)" + "\n"
             "Enlace CCT ↔ RECID y turnos fijos\n"
             "Puntajes estandarizados (media 500, DE 100)")

    arrow(22.7, 83.0, 25.8, 76.2)
    arrow(44.4, 83.0, 52.8, 76.2)
    arrow(66.1, 83.0, 75.5, 76.2)
    arrow(88.1, 83.0, 86.2, 76.2)

    # CAPA 3: Modelo regulatorio AERMOD
    cont_aermod = FancyBboxPatch(
        (13.0, 41.0), 85.2, 15.2, boxstyle="round,pad=0.35,rounding_size=2.4",
        facecolor=C_PILL1, edgecolor=C_LINE, linewidth=1.35, zorder=1
    )
    ax.add_patch(cont_aermod)
    ax.text(55.6, 54.8, r"MODELO REGULATORIO AERMOD (concentraciones de $\mathrm{PM_{2.5}}$ industrial a $z = 1.5\ \mathrm{m}$)",
            ha="center", va="center", fontsize=8.45, fontweight="bold", color="#243b6b", zorder=4)

    rect_box(15.2, 42.2, 38.4, 10.6, "Corrida anual (perfiles horarios de emisión y grupos por rama)",
             "Promedio anual (2015, 2017, 2019) por inmueble\n"
             "Desagregación por 5 ramas tecnológicas AP-42",
             fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.15, accent_top=C_NAVY, title_fs=7.15)
    rect_box(57.4, 42.2, 38.4, 10.6, "Corrida horaria (95 días alrededor de PLANEA)",
             "Resolución 1 h (28 abr – 31 jul) filtrada al horario\n"
             "exacto de cada turno escolar",
             fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.15, accent_top=C_RED, title_fs=7.9)

    arrow(26.6, 62.8, 34.4, 56.6)
    arrow(52.8, 62.8, 55.6, 56.6)
    arrow(81.8, 62.8, 76.6, 56.6)

    # CAPA 4: Estrategias econométricas
    rect_box(13.0, 19.0, 40.6, 15.2, "Estrategia TWFE: panel anual",
             r"EF unidad ($\alpha_i$) + año ($\gamma_t$) / Mun.$\times$Año + $\mathbf{W}_{rt}$" + "\n"
             "• Efecto promedio metropolitano (MCO y TWFE)\n"
             "• Heterogeneidad por marginación y rama AP-42\n"
             "• 5 especificaciones de robustez (RECID / Mun.)",
             fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.3, accent_top=C_NAVY, title_fs=8.6)
    rect_box(57.6, 19.0, 40.6, 15.2, "Estrategia IV: forma reducida y 2SLS",
             r"Exposición horaria por turno (30 d, $\mu\mathrm{g/m}^3$)" + "\n"
             r"• Instrumento: alineación de viento con $Q_{2015}$ fija" + "\n"
             "• Contraste directo TWFE vs. 2SLS (atenuación)\n"
             "• Pruebas de mecanismo: 24 h vs. turno y placebo",
             fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.3, accent_top=C_RED, title_fs=8.6)

    arrow(34.4, 42.0, 33.3, 34.4, color=C_NAVY)
    arrow(76.6, 42.0, 77.9, 34.4, color=C_RED)

    # CAPA 5: Política pública
    pill_box(13.0, 4.8, 85.2, 9.2, "Transferencia a política pública (ProAire ZMVM / SEP / SEDEMA)",
             "• Cartografía de recintos prioritarios: focalización de mitigación de calidad del aire en aulas\n"
             "• Priorización regulatoria e inspección dirigida por rama tecnológica AP-42",
             fc=C_PILL2, ec="#3a5ba0", title_color="#1d3557", lw=1.35)

    arrow(33.3, 18.8, 42.0, 14.5, color=C_LINE)
    arrow(77.9, 18.8, 69.0, 14.5, color=C_LINE)

    # Mini-leyenda de formas
    y_leg = 0.6
    ax.add_patch(Polygon([(29.0, y_leg), (31.8, y_leg), (32.3, y_leg+1.9), (29.5, y_leg+1.9)],
                         closed=True, fc="#f5f8fe", ec=C_LINE, lw=1.0))
    ax.text(33.0, y_leg+0.95, "Insumo de datos", va="center", fontsize=7.6, color="#4a5568")
    ax.add_patch(Rectangle((46.0, y_leg), 3.0, 1.9, fc="#ffffff", ec=C_LINE, lw=1.0))
    ax.text(49.8, y_leg+0.95, "Proceso / estimación", va="center", fontsize=7.6, color="#4a5568")
    ax.add_patch(FancyBboxPatch((65.5, y_leg+0.1), 3.0, 1.7, boxstyle="round,pad=0.1,rounding_size=0.8",
                                fc=C_PILL2, ec="#3a5ba0", lw=1.0))
    ax.text(69.4, y_leg+0.95, "Modelo físico / entregable", va="center", fontsize=7.6, color="#4a5568")

    ax.set_title("Arquitectura de integración de datos, modelación física (AERMOD) e identificación econométrica",
                 fontsize=10.8, fontweight="bold", color=C_DARK, pad=6)
    plt.tight_layout()
    out_path = f"{OUT_DIR}/fig_cap2_pipeline_arquitectura.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out_path}")


# Activar estilo Serif para las figuras estadísticas (3.1, 3.3 y 3.4)
def set_serif_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "Georgia"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "axes.edgecolor": "#1a202c",
        "axes.linewidth": 0.9,
        "xtick.color": "#1a202c",
        "ytick.color": "#1a202c",
        "xtick.direction": "out",
        "ytick.direction": "out",
    })


# =====================================================================
# FIGURA 3.1: PERFILES HORARIOS (OPCIÓN D) Y CAPA LÍMITE
# =====================================================================
def crear_fig31_perfiles_capa_limite():
    set_serif_style()
    filas = []
    for yr in [2015, 2017, 2019]:
        with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
            for line in f.readlines()[1:]:
                p = line.split()
                if len(p) >= 22:
                    hr = int(p[4])
                    zic, zim = float(p[9]), float(p[10])
                    vals = [v for v in (zic, zim) if 0 < v < 5000]
                    if vals:
                        filas.append((hr, max(vals)))
    df_pbl = pd.DataFrame(filas, columns=["hr", "z_eff"])
    pbl_stats = df_pbl.groupby("hr")["z_eff"].agg(
        med="median",
        p25=lambda s: np.percentile(s, 25),
        p75=lambda s: np.percentile(s, 75),
    ).reset_index()

    x_blk = np.array([2.5, 6.5, 10.5, 14.5, 18.5, 22.5, 26.5])
    # Paleta ganadora Opción D (sobria en azules + carmesí)
    curvas_cfg = [
        ("Fundición y metalurgia",      [0.64, 0.96, 1.24, 1.25, 1.12, 0.79], "#b2182b"),
        ("Vidrio, min. y secado quím.", [0.94, 0.98, 1.04, 1.05, 1.02, 0.97], "#08306b"),
        ("Turbinas de gas (CFE)",       [0.81, 0.92, 1.02, 1.08, 1.19, 0.98], "#2171b5"),
        ("Calderas industriales",       [0.68, 0.98, 1.21, 1.22, 1.09, 0.82], "#6baed6"),
    ]
    c_atm = "#252525"

    hrs_24 = np.arange(1, 25, dtype=float)
    hrs_eval = np.where(hrs_24 < 2.5, hrs_24 + 24.0, hrs_24)
    z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8,  "med"].iloc[0])
    z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.0, 7.6), dpi=300, sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.06], "hspace": 0.30}
    )
    fig.patch.set_facecolor("white")

    for ax in (ax1, ax2):
        ax.set_facecolor("white")
        ax.axvspan(7, 14,  color="#f3f5f8", alpha=1.0, zorder=0)
        ax.axvspan(14, 20, color="#eaeef3", alpha=1.0, zorder=0)
        for xv in (7, 14, 20):
            ax.axvline(xv, color="#94a3b8", ls=":", lw=0.95, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    # Panel A
    ax1.axhline(1.0, color="#64748b", lw=1.0, ls=":", zorder=2)
    ax1.text(24.25, 1.0, "Constante\n24/7 (1.0)", va="center", ha="left",
             fontsize=8.0, color="#475569", style="italic", clip_on=False)

    for lbl, vals, col in curvas_cfg:
        cs = CubicSpline(x_blk, np.array(vals + [vals[0]]), bc_type="periodic")
        ax1.plot(hrs_24, cs(hrs_eval), color=col, ls="-", lw=2.0,
                 marker="o", ms=4.3, mfc="white", mec=col, mew=1.55,
                 label=lbl, zorder=3)

    ax1.set_ylim(0.55, 1.46)
    ax1.set_yticks([0.6, 0.8, 1.0, 1.2, 1.4])
    ax1.set_ylabel(r"Factor horario de emisión ($f_{k,h}$)", fontsize=10.0)
    ax1.set_title("A. Perfiles horarios de operación industrial (Tabla B.1) y jornadas escolares",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.56, 0.03), ncol=2,
               fontsize=8.7, frameon=False, columnspacing=1.6, handlelength=2.2)

    ax1.text(4.0,  1.425, "Madrugada\n(inversión)", ha="center", va="top", fontsize=8.2, color=C_MUTED, style="italic")
    ax1.text(10.5, 1.425, "Turno matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.5, fontweight="bold", color=C_DARK)
    ax1.text(17.0, 1.425, "Turno vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.5, fontweight="bold", color=C_DARK)
    ax1.text(22.0, 1.425, "Noche", ha="center", va="top", fontsize=8.2, color=C_MUTED, style="italic")

    # Panel B
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color=c_atm, alpha=0.14, edgecolor="none", label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=c_atm, ls="-", lw=2.0,
             marker="o", ms=4.4, mfc="white", mec=c_atm, mew=1.55,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    ax2.annotate(f"Entrada matutina (07–08 h)\nCapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8 + 30), xytext=(2.1, 1080), fontsize=8.5, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.0, shrinkA=4, shrinkB=4), zorder=5)
    ax2.annotate(f"Cierre vespertino (18–20 h)\nDescenso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19 + 30), xytext=(14.4, 1780), fontsize=8.5, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.0, shrinkA=4, shrinkB=4), zorder=5)

    ax2.set_xlim(1, 24)
    ax2.set_ylim(0, 2150)
    ax2.set_yticks([0, 500, 1000, 1500, 2000])
    ax2.set_xticks(range(1, 25, 2))
    ax2.set_xticklabels([f"{h:02d}:00" for h in range(1, 25, 2)], fontsize=8.8)
    ax2.set_xlabel("Hora local (fin del intervalo horario de AERMOD)", fontsize=10.0)
    ax2.set_ylabel(r"Altura de capa de mezcla $Z_i$ [m]", fontsize=10.0)
    ax2.set_title("B. Ciclo diurno de la altura de la capa límite planetaria en la ZMVM (AERMET, estación AICM)",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax2.legend(loc="upper left", fontsize=8.8, frameon=False)

    plt.subplots_adjust(right=0.90)
    out_path = f"{OUT_DIR}/fig_cap3_emisfact_capa_limite.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out_path}")


# =====================================================================
# FIGURA 3.3: FOREST PLOT ESTRATEGIA TWFE
# =====================================================================
def crear_fig33_forest_twfe():
    set_serif_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 6.0), dpi=300)
    fig.patch.set_facecolor("white")

    items_A = [
        ("Promedio general\n(Todas, Tabla 3.1)",                                           6.695,  9.417,   5.603,  8.080),
        ("Baja o media marg.\n" + r"(Todas, $\beta_1$)",                                   9.871,  9.580,   8.100,  8.147),
        ("Baja o media marg.\n" + r"(Públicas, $\beta_1$)",                                2.543,  8.856,   2.947,  5.170),
        ("Alta marginación\n" + r"(Todas, total $\hat{\beta}_1+\hat{\beta}_2$)",         -89.406, 46.358, -69.995, 52.143),
        ("Alta marginación\n" + r"(Públicas, total $\hat{\beta}_1+\hat{\beta}_2$)",      -95.756, 42.562, -53.568, 51.655),
    ]

    items_B = [
        ("(1) Especificación central\n(clúster RECID)",         -98.299, 43.271, -56.514, 51.794),
        ("(2) Errores agrupados\npor municipio",                -98.299, 32.783, -56.514, 43.936),
        ("(3) Efectos fijos\nmunicipio × año",                  -88.888, 44.721, -58.274, 57.205),
        ("(4) Sin controles\nmicroclimáticos",                  -98.620, 43.028, -54.289, 51.274),
        ("(5) Emisión constante\n24/7 (sin perfiles horarios)", -107.208, 46.641, -59.699, 55.027),
    ]

    def plot_forest(ax, items, title, xlabel, xlim):
        y_pos = np.arange(len(items))[::-1]
        ax.set_facecolor("white")
        ax.axvline(0, color=C_DARK, lw=1.0, ls="--", zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        for idx, (lbl, b_l, se_l, b_m, se_m) in enumerate(items):
            y = y_pos[idx]
            ax.plot([b_l - 1.96*se_l, b_l + 1.96*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.25, zorder=3)
            ax.plot([b_l - 1.645*se_l, b_l + 1.645*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.0, zorder=4)
            ax.scatter([b_l], [y + 0.16], color=C_NAVY, marker="o", s=54, zorder=5,
                       label="Lenguaje y Comunicación" if idx == 0 else None)

            x_txt = b_l + 6.0 if -4 <= b_l <= 14 else b_l
            ha_txt = "left" if -4 <= b_l <= 14 else "center"
            ax.text(x_txt, y + 0.29, f"{b_l:.1f}", ha=ha_txt, va="bottom",
                    fontsize=8.2, fontweight="bold", color=C_NAVY, zorder=6)

            ax.plot([b_m - 1.96*se_m, b_m + 1.96*se_m], [y - 0.16, y - 0.16], color=C_MATH, lw=1.15, zorder=3)
            ax.plot([b_m - 1.645*se_m, b_m + 1.645*se_m], [y - 0.16, y - 0.16], color=C_MATH, lw=2.4, zorder=4)
            ax.scatter([b_m], [y - 0.16], facecolor="white", edgecolor=C_MATH, linewidth=1.6,
                       marker="s", s=44, zorder=5,
                       label="Matemáticas" if idx == 0 else None)

        ax.set_yticks(y_pos)
        ax.set_yticklabels([x[0] for x in items], fontsize=8.6)
        ax.set_ylim(-0.6, len(items) - 0.3)
        ax.set_xlim(xlim)
        ax.set_xlabel(xlabel, fontsize=9.5)
        ax.set_title(title, fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)

    plot_forest(ax1, items_A,
                "A. Efecto promedio vs. heterogeneidad por marginación",
                r"Puntos PLANEA por $+1\ \mu\mathrm{g/m}^3$ anual", (-210, 65))
    plot_forest(ax2, items_B,
                "B. Robustez de la interacción (alta marg., públicas)",
                r"Interacción $\hat{\beta}_2$ por $+1\ \mu\mathrm{g/m}^3$ anual", (-220, 75))

    ax1.axhline(1.5, color="#cbd5e0", ls=":", lw=1.1, zorder=1)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.975),
               ncol=2, fontsize=9.2, frameon=False)
    fig.suptitle("Estrategia TWFE (exposición anual): efecto en Lenguaje por marginación y estabilidad ante especificaciones",
                 fontsize=10.9, fontweight="bold", color=C_DARK, y=1.035)
    fig.text(0.5, -0.01, "Nota: Marcadores muestran el coeficiente puntual; la barra gruesa indica el IC al 90% y la barra delgada al 95%.",
             ha="center", va="top", fontsize=8.4, color=C_MUTED, style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.92])
    out_path = f"{OUT_DIR}/fig_cap3_forest_pilar1_twfe.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out_path}")


# =====================================================================
# FIGURA 3.4: FOREST PLOT ESTRATEGIA IV
# =====================================================================
def crear_fig34_forest_iv():
    set_serif_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 6.3), dpi=300)
    fig.patch.set_facecolor("white")

    items_RF = [
        ("Todas públicas\n(30 d previos)",               -4.870, 1.928,  -1.432, 2.388),
        ("Baja o media marg.\n(30 d previos)",           -3.809, 2.195,  -1.067, 2.538),
        ("Alta marginación\n(30 d previos)",            -10.700, 4.823,  -4.910, 3.783),
        ("Alta marginación\n(30 d, Mun. × Año)",        -18.435, 7.819, -15.447, 6.888),
        ("Alta marginación\n(15 d previos)",             -6.931, 4.823,  -0.069, 5.003),
        ("Placebo: alta marg.\n(30 d posteriores)",     -10.429, 8.186,  -6.846, 9.236),
    ]

    items_CMP = [
        ("Todas públicas\n" + r"(30 d, $F_1 = 8.9$)",                    -1.03/100,   3.93/100,   -172.20/100,  89.71/100),
        ("Baja o media marg.\n" + r"(30 d, $F_1 = 7.2$)",                -0.33/100,   3.71/100,   -133.71/100, 101.33/100),
        ("Alta marginación\n" + r"(30 d, $F_1 = 9.2$)",                 -41.59/100,  36.38/100,   -450.38/100, 163.98/100),
        ("Alta marginación\n" + r"(30 d, Mun.$\times$Año, $F_1 = 12.6$)", 10.19/100, 56.37/100,  -1098.43/100, 504.96/100),
        ("Alta marginación\n" + r"(15 d, $F_1 = 15.2$)",                -46.82/100,  39.75/100,   -216.13/100, 138.63/100),
        ("Placebo: alta marg.\n" + r"(30 d post., $F_1 = 1.1$)",         None,        None,        None,         None),
    ]

    y_pos = np.arange(6)[::-1]

    # Panel A
    ax1.set_facecolor("white")
    ax1.axvline(0, color=C_DARK, lw=1.0, ls="--", zorder=1)
    ax1.axhline(0.5, color="#cbd5e0", ls=":", lw=1.1, zorder=1)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.xaxis.set_minor_locator(AutoMinorLocator(2))

    for idx, (lbl, bl, sel, bm, sem) in enumerate(items_RF):
        y = y_pos[idx]
        ax1.plot([bl - 1.96*sel, bl + 1.96*sel], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.25, zorder=3)
        ax1.plot([bl - 1.645*sel, bl + 1.645*sel], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.0, zorder=4)
        ax1.scatter([bl], [y + 0.16], color=C_NAVY, marker="o", s=52, zorder=5,
                    label="Lenguaje y Comunicación" if idx == 0 else None)
        ax1.text(bl, y + 0.29, f"{bl:.1f}", ha="center", va="bottom",
                 fontsize=8.1, fontweight="bold", color=C_NAVY)

        ax1.plot([bm - 1.96*sem, bm + 1.96*sem], [y - 0.16, y - 0.16], color=C_MATH, lw=1.15, zorder=3)
        ax1.plot([bm - 1.645*sem, bm + 1.645*sem], [y - 0.16, y - 0.16], color=C_MATH, lw=2.4, zorder=4)
        ax1.scatter([bm], [y - 0.16], facecolor="white", edgecolor=C_MATH, linewidth=1.6,
                    marker="s", s=42, zorder=5,
                    label="Matemáticas" if idx == 0 else None)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([x[0] for x in items_RF], fontsize=8.5)
    ax1.set_ylim(-0.62, 5.75)
    ax1.set_xlim(-36, 14)
    ax1.set_xlabel("Puntos PLANEA por +1 DE de viento desfavorable", fontsize=9.3)
    ax1.set_title("A. Forma reducida: efecto directo del choque de viento",
                  fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax1.legend(loc="upper left", fontsize=8.6, frameon=False)

    # Panel B
    ax2.set_facecolor("white")
    ax2.axvline(0, color=C_DARK, lw=1.0, ls="--", zorder=1)
    ax2.axhline(0.5, color="#cbd5e0", ls=":", lw=1.1, zorder=1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.xaxis.set_minor_locator(AutoMinorLocator(2))

    for idx, (lbl, btw, setw, biv, seiv) in enumerate(items_CMP):
        y = y_pos[idx]
        if btw is None:
            ax2.text(-11.0, y,
                     r"Placebo 2SLS no informativo ($F_1 = 1.1$);" + "\nomitido por amplitud del intervalo.",
                     ha="center", va="center", fontsize=8.2, color=C_MUTED, style="italic")
            continue

        ax2.plot([btw - 1.96*setw, btw + 1.96*setw], [y + 0.16, y + 0.16], color=C_TWFE_BAR, lw=1.3, zorder=3)
        ax2.plot([btw - 1.645*setw, btw + 1.645*setw], [y + 0.16, y + 0.16], color=C_TWFE_BAR, lw=2.8, zorder=4)
        ax2.scatter([btw], [y + 0.16], facecolor="white", edgecolor=C_NAVY, linewidth=1.75,
                    marker="o", s=52, zorder=5,
                    label="TWFE físico — Lenguaje" if idx == 0 else None)

        ax2.plot([biv - 1.96*seiv, biv + 1.96*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=1.35, zorder=3)
        ax2.plot([biv - 1.645*seiv, biv + 1.645*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=3.1, zorder=4)
        ax2.scatter([biv], [y - 0.16], color=C_RED, marker="D", s=46, zorder=5,
                    label=r"2SLS físico — Lenguaje (viento $Q_{2015}$)" if idx == 0 else None)
        ax2.text(biv, y - 0.34, f"{biv:.2f}", ha="center", va="top",
                 fontsize=8.1, fontweight="bold", color=C_RED)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([x[0] for x in items_CMP], fontsize=8.5)
    ax2.set_ylim(-0.62, 5.75)
    ax2.set_xlim(-22.5, 3.8)
    ax2.set_xlabel(r"Puntos en Lenguaje por $+0.01\ \mu\mathrm{g/m}^3$ en turno ($\approx 29\%$ de la media en alta marginación)", fontsize=8.4)
    ax2.set_title("B. Atenuación TWFE vs. 2SLS físico en Lenguaje",
                  fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax2.legend(loc="upper left", fontsize=8.5, frameon=False)

    fig.suptitle("Estrategia IV (concentraciones horarias de AERMOD por turno): forma reducida y comparación TWFE–2SLS",
                 fontsize=10.8, fontweight="bold", color=C_DARK, y=1.01)
    fig.text(0.5, -0.01, "Nota: Marcadores muestran el coeficiente puntual; la barra gruesa indica el IC de Wald al 90% y la barra delgada al 95%.",
             ha="center", va="top", fontsize=8.4, color=C_MUTED, style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    out_path = f"{OUT_DIR}/fig_cap3_forest_pilar2_postfile.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out_path}")


if __name__ == "__main__":
    crear_fig21_pipeline()
    crear_fig31_perfiles_capa_limite()
    crear_fig33_forest_twfe()
    crear_fig34_forest_iv()
    print(f"\n[LISTO] Las 4 figuras actualizadas se guardaron en: {OUT_DIR}")
