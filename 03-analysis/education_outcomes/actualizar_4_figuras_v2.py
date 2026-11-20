import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
C_SLATE  = "#334155"
C_LIGHT  = "#f4f8fb"


# =====================================================================
# 1. PIPELINE: PALETA NEUTRA ARQUITECTÓNICA + ESCALA ÓPTIMA PARA PDF
# =====================================================================
def crear_fig1_pipeline():
    # Lienzo más compacto (11.2 x 7.5) para que la fuente se lea más grande al escalar a \textwidth
    fig, ax = plt.subplots(figsize=(11.2, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc="#ffffff", ec=C_SLATE, title_color=C_DARK, lw=1.25):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.45,rounding_size=1.3",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
        )
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 1.7, title, ha="center", va="top",
                fontsize=8.8, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w/2, y + (h - 2.5)/2, body, ha="center", va="center",
                fontsize=7.8, color=C_DARK, linespacing=1.28, zorder=4)

    def arrow(x1, y1, x2, y2, color="#64748b", lw=1.3):
        a = FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
            color=color, linewidth=lw, zorder=2
        )
        ax.add_patch(a)

    capas = [
        (88.5, "1. INSUMOS\nPÚBLICOS"),
        (67.5, "2. PREPROCESO\nY PUENTE FÍSICO"),
        (46.0, "3. DISPERSIÓN\nATMOSFÉRICA"),
        (23.5, "4. IDENTIFICACIÓN\nECONOMÉTRICA"),
        (5.8,  "5. POLÍTICA\nPÚBLICA"),
    ]
    for yc, lbl in capas:
        ax.text(5.8, yc, lbl, ha="center", va="center", fontsize=7.8,
                fontweight="bold", color="#475569")

    # CAPA 1: Tono neutro uniforme (sin competir con ramas, años ni turnos)
    box(13.0, 82.0, 19.6, 13.2, "RETC / COA (SEMARNAT)",
        "723 plantas (2015–2019)\n"
        r"$\mathrm{CO_2}$ como trazador" + "\n"
        "→ 285 fuentes activas",
        fc="#f8fafc", ec="#64748b", title_color=C_DARK)
    box(34.4, 82.0, 19.6, 13.2, "Meteorología (NOAA)",
        "ISD superficie + IGRA\n"
        "Estación AICM (WMO 76679)\n"
        "8,760 h/año (2015–2019)",
        fc="#f8fafc", ec="#64748b", title_color=C_DARK)
    box(55.8, 82.0, 19.6, 13.2, "Relieve (SRTM 30 m)",
        "4 mosaicos GeoTIFF\n"
        "Cuenca de México y sierras\n"
        "UTM 14N (EPSG:32614)",
        fc="#f8fafc", ec="#64748b", title_color=C_DARK)
    box(77.2, 82.0, 21.0, 13.2, "PLANEA / SIGED (SEP)",
        "3° Secundaria (2015, 17, 19)\n"
        "3,833 CCT → 3,172 edificios\n"
        "2,392 en Cuenca (9,459 obs.)",
        fc="#f8fafc", ec="#64748b", title_color=C_DARK)

    # CAPA 2: Blanco limpio con borde grafito
    box(13.0, 61.0, 27.0, 13.2, "Auditoría RETC y Puente AP-42",
        "Depuración e imputación 2018\n"
        r"Conversión $\mathrm{CO_2 \rightarrow PM_{2.5}}$ (6 familias)" + "\n"
        "Chimeneas + EMISFACT (LBNL/CENACE)",
        fc="#ffffff", ec=C_SLATE, title_color=C_DARK)
    box(41.8, 61.0, 21.6, 13.2, "AERMET (Etapas 1–3)",
        r"Flujo de calor, $u_*$, longitud $L$," + "\n"
        r"capas límite ($Z_{ic}, Z_{im}$)" + "\n"
        r"→ .sfc/.pfl + controles $\mathbf{W}_{rt}$",
        fc="#ffffff", ec=C_SLATE, title_color=C_DARK)
    box(65.2, 61.0, 33.0, 13.2, "AERMAP y Armonización Escolar",
        r"Elevación ($Z_{\mathrm{elev}}$) y colina ($Z_{\mathrm{hill}}$)" + "\n"
        "Enlace CCT ↔ RECID y turnos fijos\n"
        "Puntajes estandarizados (media 500, DE 100)",
        fc="#ffffff", ec=C_SLATE, title_color=C_DARK)

    arrow(22.8, 81.6, 25.5, 74.7)
    arrow(44.2, 81.6, 52.6, 74.7)
    arrow(65.6, 81.6, 75.0, 74.7)
    arrow(87.7, 81.6, 86.0, 74.7)

    # CAPA 3: Contenedor AERMOD neutro + sub-bloques alineados a Pilar 1 y Pilar 2
    cont_aermod = FancyBboxPatch(
        (13.0, 38.5), 85.2, 15.2, boxstyle="round,pad=0.45,rounding_size=1.5",
        facecolor="#f1f5f9", edgecolor=C_SLATE, linewidth=1.4, linestyle="--", zorder=1
    )
    ax.add_patch(cont_aermod)
    ax.text(55.6, 52.5, r"MODELO REGULATORIO AERMOD (concentraciones de $\mathrm{PM_{2.5}}$ industrial a $z = 1.5\ \mathrm{m}$)",
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=C_DARK, zorder=4)

    box(15.2, 39.8, 38.4, 10.6, "Corrida Anual (EMISFACT + SRCGROUP)",
        "Promedio anual (2015, 2017, 2019) por inmueble\n"
        "Desagregación por 5 ramas tecnológicas AP-42",
        fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.15)
    box(57.4, 39.8, 38.4, 10.6, "Corrida Horaria POSTFILE (95 d pre/post PLANEA)",
        "Resolución 1 h (28 abr – 31 jul) filtrada al horario\n"
        "exacto de cada turno escolar",
        fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.15)

    arrow(26.5, 60.5, 34.4, 54.0)
    arrow(52.6, 60.5, 55.6, 54.0)
    arrow(81.7, 60.5, 76.6, 54.0)

    # CAPA 4: Dos pilares (únicos acentos cromáticos: Navy = Pilar 1, Carmesí = Pilar 2)
    box(13.0, 16.0, 40.6, 15.2, "Pilar 1: Panel Anual TWFE (pyfixest)",
        r"EF unidad ($\alpha_i$) + año ($\gamma_t$) / Mun.$\times$Año + $\mathbf{W}_{rt}$" + "\n"
        "• Efecto promedio metropolitano (MCO y TWFE)\n"
        "• Heterogeneidad por rama AP-42 y marginación\n"
        "• 5 especificaciones de robustez (RECID / Mun.)",
        fc="#f7fbff", ec=C_NAVY, title_color=C_NAVY, lw=1.45)
    box(57.6, 16.0, 40.6, 15.2, "Pilar 2: Identificación Causal 2SLS y Forma Reducida",
        r"Exposición física POSTFILE por turno (30 d, $\mu\mathrm{g/m}^3$)" + "\n"
        r"• Instrumento: alineación de viento con $Q_{2015}$ fija" + "\n"
        "• Contraste simétrico TWFE vs. 2SLS (atenuación)\n"
        "• Pruebas de mecanismo: 24 h vs. turno y placebo",
        fc="#fff8f8", ec=C_RED, title_color=C_RED, lw=1.45)

    arrow(34.4, 39.3, 33.3, 31.7, color=C_NAVY)
    arrow(76.6, 39.3, 77.9, 31.7, color=C_RED)

    # CAPA 5: Cierre neutro oscuro (sin spoilers)
    box(13.0, 1.2, 85.2, 9.6, "Transferencia a Política Pública (ProAire ZMVM / SEP / SEDEMA)",
        "• Cartografía de hipervulnerabilidad escolar: focalización de mitigación de calidad del aire en aulas\n"
        "• Priorización regulatoria e inspección dirigida por rama tecnológica AP-42",
        fc="#edf2f7", ec=C_DARK, title_color=C_DARK, lw=1.4)

    arrow(33.3, 15.5, 42.0, 11.3, color=C_SLATE)
    arrow(77.9, 15.5, 69.0, 11.3, color=C_SLATE)

    ax.set_title("Arquitectura de Integración de Datos, Modelación Física (AERMOD) e Identificación Econométrica",
                 fontsize=11.0, fontweight="bold", color=C_DARK, pad=6)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cap2_pipeline_arquitectura.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap2_pipeline_arquitectura.png")


# =====================================================================
# 3. EMISFACT + CAPA LÍMITE: TURNOS VERDE/NARANJA + 24 PUNTOS PAREJOS
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
    # Colores totalmente ajenos a verde (matutino), naranja (vespertino) y azul atmósfera
    perfiles_b1 = {
        "Fundición y metalurgia":  ([0.64, 0.96, 1.24, 1.25, 1.12, 0.79], "#b2182b"),
        "Calderas industriales":   ([0.68, 0.98, 1.21, 1.22, 1.09, 0.82], "#7f4f24"),
        "Hornos de vidrio y min.": ([0.94, 0.98, 1.04, 1.05, 1.02, 0.97], "#c29200"),
        "Turbinas de gas (CFE)":   ([0.81, 0.92, 1.02, 1.08, 1.19, 0.98], "#7b2cbf"),
    }

    hrs_24 = np.arange(1, 25, dtype=float)
    hrs_eval = np.where(hrs_24 < 2.5, hrs_24 + 24.0, hrs_24)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.4, 7.8), dpi=300, sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.08], "hspace": 0.30}
    )

    # Fondos con Matutino verde y Vespertino naranja
    for ax in (ax1, ax2):
        ax.axvspan(1, 7,   color="#34495e", alpha=0.055, zorder=0)
        ax.axvspan(7, 14,  color=C_TEAL,    alpha=0.10,  zorder=0)
        ax.axvspan(14, 20, color=C_AMBER,   alpha=0.10,  zorder=0)
        ax.axvspan(20, 24, color="#34495e", alpha=0.055, zorder=0)
        for xv in (7, 14, 20):
            ax.axvline(xv, color="#94a3b8", ls=":", lw=0.95, zorder=1)
        ax.grid(axis="y", linestyle=":", alpha=0.45)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Panel A: Todas las curvas con línea sólida pareja y los 24 puntos horarios
    ax1.axhline(1.0, color="#7f8c8d", lw=1.2, ls="--", alpha=0.85,
                label="Emisión constante 24/7 (factor = 1.0)", zorder=2)
    for lbl, (vals, col) in perfiles_b1.items():
        y_per = np.array(vals + [vals[0]])
        cs = CubicSpline(x_blk, y_per, bc_type="periodic")
        y_24 = cs(hrs_eval)
        ax1.plot(hrs_24, y_24, color=col, ls="-", lw=2.0, marker="o", ms=3.5, label=lbl, zorder=3)

    ax1.set_ylim(0.55, 1.48)
    ax1.set_ylabel("Factor horario EMISFACT ($f_{k,h}$)", fontsize=9.5, fontweight="bold")
    ax1.set_title("A. Perfiles horarios de operación industrial (EMISFACT, Tabla B.1) y jornadas escolares",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=8)
    ax1.legend(loc="lower center", ncol=3, fontsize=8.1, framealpha=0.96, edgecolor="#cbd5e0")

    ax1.text(4.0,  1.44, "Madrugada\n(inversión)", ha="center", va="top", fontsize=7.9, color="#64748b", style="italic")
    ax1.text(10.5, 1.44, "Turno Matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.3, fontweight="bold", color="#116b50")
    ax1.text(17.0, 1.44, "Turno Vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.3, fontweight="bold", color="#9a3412")
    ax1.text(22.0, 1.44, "Noche", ha="center", va="top", fontsize=7.9, color="#64748b", style="italic")

    # Panel B: Capa límite (azul pizarra exclusivo) + callouts verde y naranja
    C_ATM = "#1b4965"
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color=C_ATM, alpha=0.20, label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=C_ATM, ls="-", lw=2.2, marker="o", ms=3.8,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8,  "med"].iloc[0])
    z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])

    ax2.annotate(f"Entrada matutina (07–08 h):\ncapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8), xytext=(1.8, 1020), fontsize=8.1, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_TEAL, lw=1.15),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.25), zorder=5)
    ax2.annotate(f"Cierre vespertino (18–20 h):\ndescenso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19), xytext=(14.9, 1740), fontsize=8.1, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_AMBER, lw=1.15),
                 arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.25), zorder=5)

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
# 4. ROSA DE VIENTOS: MISMA LÍNEA SÓLIDA Y CÍRCULOS, SOLO CAMBIA EL COLOR
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

    # Gradiente azul -> índigo -> morado, misma línea sólida y círculos en los 3 años
    colores_yr = {2015: "#3898ec", 2017: "#635bff", 2019: "#581c87"}

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
            col = colores_yr[yr]
            ax.plot(angles_closed, f_pct, color=col, ls="-", lw=2.0, marker="o", ms=3.8, label=str(yr))
            ax.fill(angles_closed, f_pct, color=col, alpha=0.07)

        ax.set_ylim(0, 20)
        ax.set_yticks([5, 10, 15, 20])
        ax.set_yticklabels(["5%", "10%", "15%", "20%"], fontsize=8.0, color="#4a5568")
        ax.set_rlabel_position(315)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title(titulo, fontsize=10.5, fontweight="bold", color=C_DARK, pad=18)
        ax.text(0.5, -0.15, subnota, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.4, color=C_DARK,
                bbox=dict(boxstyle="round,pad=0.38", fc=C_LIGHT, ec="#95a5a6", lw=0.85))

    avg_anual = np.mean([freq_16(wd_anual[y])[:-1] for y in [2015, 2017, 2019]], axis=0)
    idx_pk = int(np.argmax(avg_anual))
    ax1.annotate("Corredor industrial\nNE / ENE (viento dominante)",
                 xy=(angles[idx_pk], avg_anual[idx_pk]), xytext=(np.deg2rad(52), 24.5),
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
# 6. FOREST PILAR 2: TWFE COMO CÍRCULO HUECO AZUL + 2SLS DIAMANTE CARMESÍ
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

    # --- Panel A: Forma Reducida (Lenguaje = círculo azul, Matemáticas = cuadrado gris) ---
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

    # --- Panel B: Lenguaje TWFE (círculo hueco azul) vs. 2SLS (diamante carmesí) ---
    C_TWFE_BAR = "#5b8fb9"
    yB = np.arange(len(items_CMP))[::-1]
    ax2.axvline(0, color=C_DARK, lw=1.1, ls="--", zorder=1)
    ax2.grid(axis="x", linestyle=":", alpha=0.5)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.axhspan(0.50, 2.50, color=C_LIGHT, alpha=0.85, zorder=0)

    for idx, (lbl, btw, setw, biv, seiv) in enumerate(items_CMP):
        y = yB[idx]
        # TWFE físico (círculo hueco azul marino: mismo azul de Lenguaje, distinto de Matemáticas)
        ax2.plot([btw - 1.96*setw, btw + 1.96*setw], [y + 0.16, y + 0.16], color=C_TWFE_BAR, lw=1.4, zorder=3)
        ax2.plot([btw - 1.645*setw, btw + 1.645*setw], [y + 0.16, y + 0.16], color=C_TWFE_BAR, lw=3.0, zorder=4)
        ax2.scatter([btw], [y + 0.16], facecolor="white", edgecolor=C_NAVY, linewidth=1.8,
                    marker="o", s=54, zorder=5,
                    label="TWFE físico — Lenguaje (POSTFILE)" if idx == 0 else None)

        # 2SLS físico (diamante sólido carmesí)
        ax2.plot([biv - 1.96*seiv, biv + 1.96*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=1.5, zorder=3)
        ax2.plot([biv - 1.645*seiv, biv + 1.645*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=3.3, zorder=4)
        ax2.scatter([biv], [y - 0.16], color=C_RED, marker="D", s=50, zorder=5,
                    label=r"2SLS físico — Lenguaje (viento $Q_{2015}$)" if idx == 0 else None)
        ax2.text(biv, y - 0.34, f"{biv:.2f}", ha="center", va="top",
                 fontsize=7.9, fontweight="bold", color=C_RED)

    ax2.set_yticks(yB)
    ax2.set_yticklabels([x[0] for x in items_CMP], fontsize=8.3)
    ax2.set_ylim(-0.68, len(items_CMP) - 0.32)
    ax2.set_xlim(-22.5, 3.8)
    ax2.set_xlabel(r"Puntos en Lenguaje por $+0.01\ \mu\mathrm{g/m}^3$ en turno ($\approx 29\%$ de la media)", fontsize=8.7, fontweight="bold")
    ax2.set_title("B. Atenuación TWFE vs. 2SLS físico en Lenguaje (POSTFILE)", fontsize=10.2, fontweight="bold", color=C_DARK, pad=10)
    ax2.legend(loc="upper left", fontsize=8.1, framealpha=0.96, edgecolor="#cbd5e0")

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
    crear_fig3_emisfact_capa_limite()
    crear_fig4_rosa_vientos()
    crear_fig6_forest_pilar2()
    print(f"\n[LISTO] Las 4 figuras actualizadas se guardaron en: {OUT_DIR}")
