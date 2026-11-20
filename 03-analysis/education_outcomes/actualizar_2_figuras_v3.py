import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle
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

C_NAVY   = "#005a9c"   # Pilar 1 (TWFE) y Lenguaje
C_RED    = "#b2182b"   # Pilar 2 (2SLS POSTFILE)
C_DARK   = "#1a252f"
C_LINE   = "#4a72a8"   # Acero azulado limpio estilo Tesis_V4
C_PILL1  = "#e6eefb"   # Píldora motor AERMOD
C_PILL2  = "#d0def8"   # Píldora entregable final
C_TEAL   = "#1b9e77"   # Turno Matutino
C_AMBER  = "#d95f02"   # Turno Vespertino


# =====================================================================
# 1. PIPELINE CON GRAMÁTICA DE FORMAS Y COLOR NARRATIVO (SIN PYFIXEST)
# =====================================================================
def crear_fig1_pipeline():
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

    def rect_box(x, y, w, h, title, body, fc="#ffffff", ec=C_LINE, title_color=C_DARK, lw=1.25, accent_top=None):
        p = Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3)
        ax.add_patch(p)
        if accent_top is not None:
            bar = Rectangle((x, y + h - 0.85), w, 0.85, facecolor=accent_top, edgecolor="none", zorder=4)
            ax.add_patch(bar)
        ax.text(x + w/2, y + h - (2.1 if accent_top else 1.7), title, ha="center", va="top",
                fontsize=8.7, fontweight="bold", color=title_color, zorder=5)
        ax.text(x + w/2, y + (h - (2.9 if accent_top else 2.5))/2, body, ha="center", va="center",
                fontsize=7.75, color="#2d3748", linespacing=1.28, zorder=5)

    def pill_box(x, y, w, h, title, body, fc=C_PILL2, ec=C_LINE, title_color=C_DARK, lw=1.4):
        p = FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.35,rounding_size=3.2",
            facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
        )
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 1.6, title, ha="center", va="top",
                fontsize=8.8, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w/2, y + (h - 2.4)/2, body, ha="center", va="center",
                fontsize=7.8, color=C_DARK, linespacing=1.30, zorder=4)

    def arrow(x1, y1, x2, y2, color=C_LINE, lw=1.3):
        a = FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
            color=color, linewidth=lw, zorder=2
        )
        ax.add_patch(a)

    # Etiquetas laterales de capa
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

    # CAPA 1: Paralelogramos (Insumos)
    parallelogram(12.5, 83.2, 20.4, 12.6, "RETC / COA (SEMARNAT)",
                  "723 plantas (2015–2019)\n" + r"$\mathrm{CO_2}$ como trazador" + "\n→ 285 fuentes activas")
    parallelogram(34.2, 83.2, 20.4, 12.6, "Meteorología (NOAA)",
                  "ISD superficie + IGRA\nAICM (WMO 76679)\n8,760 h/año (2015–2019)")
    parallelogram(55.9, 83.2, 20.4, 12.6, "Relieve (SRTM 30 m)",
                  "4 mosaicos GeoTIFF\nCuenca de México\nUTM 14N (EPSG:32614)")
    parallelogram(77.6, 83.2, 21.0, 12.6, "PLANEA / SIGED (SEP)",
                  "3° Sec. (2015, 2017, 2019)\n3,833 CCT → 3,172 edificios\n2,392 Cuenca (9,459 obs.)")

    # CAPA 2: Rectángulos blancos (Preprocesamiento)
    rect_box(13.0, 63.0, 27.2, 13.0, "Auditoría RETC y Puente AP-42",
             "Depuración e imputación 2018\n"
             r"Conversión $\mathrm{CO_2 \rightarrow PM_{2.5}}$ (6 familias)" + "\n"
             "Chimeneas + EMISFACT (LBNL/CENACE)")
    rect_box(42.0, 63.0, 21.6, 13.0, "AERMET (Etapas 1–3)",
             r"Flujo de calor, $u_*$, longitud $L$," + "\n"
             r"capas límite ($Z_{ic}, Z_{im}$)" + "\n"
             r"→ .sfc/.pfl + controles $\mathbf{W}_{rt}$")
    rect_box(65.4, 63.0, 32.8, 13.0, "AERMAP y Armonización Escolar",
             r"Elevación ($Z_{\mathrm{elev}}$) y colina ($Z_{\mathrm{hill}}$)" + "\n"
             "Enlace CCT ↔ RECID y turnos fijos\n"
             "Puntajes estandarizados (media 500, DE 100)")

    arrow(22.7, 83.0, 25.8, 76.2)
    arrow(44.4, 83.0, 52.8, 76.2)
    arrow(66.1, 83.0, 75.5, 76.2)
    arrow(88.1, 83.0, 86.2, 76.2)

    # CAPA 3: Contenedor Píldora AERMOD (suave azul-índigo) + 2 salidas narrativas
    cont_aermod = FancyBboxPatch(
        (13.0, 41.0), 85.2, 15.2, boxstyle="round,pad=0.35,rounding_size=2.4",
        facecolor=C_PILL1, edgecolor=C_LINE, linewidth=1.35, zorder=1
    )
    ax.add_patch(cont_aermod)
    ax.text(55.6, 54.8, r"MODELO REGULATORIO AERMOD (concentraciones de $\mathrm{PM_{2.5}}$ industrial a $z = 1.5\ \mathrm{m}$)",
            ha="center", va="center", fontsize=8.45, fontweight="bold", color="#243b6b", zorder=4)

    rect_box(15.2, 42.2, 38.4, 10.6, "Corrida Anual (EMISFACT + SRCGROUP)",
             "Promedio anual (2015, 2017, 2019) por inmueble\n"
             "Desagregación por 5 ramas tecnológicas AP-42",
             fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.15, accent_top=C_NAVY)
    rect_box(57.4, 42.2, 38.4, 10.6, "Corrida Horaria POSTFILE (95 d pre/post PLANEA)",
             "Resolución 1 h (28 abr – 31 jul) filtrada al horario\n"
             "exacto de cada turno escolar",
             fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.15, accent_top=C_RED)

    arrow(26.6, 62.8, 34.4, 56.6)
    arrow(52.8, 62.8, 55.6, 56.6)
    arrow(81.8, 62.8, 76.6, 56.6)

    # CAPA 4: Dos Pilares Econométricos (SIN pyfixest, acento superior limpio)
    rect_box(13.0, 19.0, 40.6, 15.2, "Pilar 1: Panel Anual (TWFE)",
             r"EF unidad ($\alpha_i$) + año ($\gamma_t$) / Mun.$\times$Año + $\mathbf{W}_{rt}$" + "\n"
             "• Efecto promedio metropolitano (MCO y TWFE)\n"
             "• Heterogeneidad por rama AP-42 y marginación\n"
             "• 5 especificaciones de robustez (RECID / Mun.)",
             fc="#ffffff", ec=C_NAVY, title_color=C_NAVY, lw=1.3, accent_top=C_NAVY)
    rect_box(57.6, 19.0, 40.6, 15.2, "Pilar 2: Identificación Causal (2SLS y Forma Reducida)",
             r"Exposición física POSTFILE por turno (30 d, $\mu\mathrm{g/m}^3$)" + "\n"
             r"• Instrumento: alineación de viento con $Q_{2015}$ fija" + "\n"
             "• Contraste simétrico TWFE vs. 2SLS (atenuación)\n"
             "• Pruebas de mecanismo: 24 h vs. turno y placebo",
             fc="#ffffff", ec=C_RED, title_color=C_RED, lw=1.3, accent_top=C_RED)

    arrow(34.4, 42.0, 33.3, 34.4, color=C_NAVY)
    arrow(76.6, 42.0, 77.9, 34.4, color=C_RED)

    # CAPA 5: Píldora entregable final (tono azul-índigo progresivo más profundo)
    pill_box(13.0, 4.8, 85.2, 9.2, "Transferencia a Política Pública (ProAire ZMVM / SEP / SEDEMA)",
             "• Cartografía de hipervulnerabilidad escolar: focalización de mitigación de calidad del aire en aulas\n"
             "• Priorización regulatoria e inspección dirigida por rama tecnológica AP-42",
             fc=C_PILL2, ec="#3a5ba0", title_color="#1d3557", lw=1.35)

    arrow(33.3, 18.8, 42.0, 14.5, color=C_LINE)
    arrow(77.9, 18.8, 69.0, 14.5, color=C_LINE)

    # Mini-leyenda de formas al pie (estilo INPUT | PROCESS | RESULT de Tesis_V4)
    y_leg = 0.6
    # Paralelogramo
    ax.add_patch(Polygon([(29.0, y_leg), (31.8, y_leg), (32.3, y_leg+1.9), (29.5, y_leg+1.9)],
                         closed=True, fc="#f5f8fe", ec=C_LINE, lw=1.0))
    ax.text(33.0, y_leg+0.95, "Insumo de datos", va="center", fontsize=7.6, color="#4a5568")
    # Rectángulo
    ax.add_patch(Rectangle((46.0, y_leg), 3.0, 1.9, fc="#ffffff", ec=C_LINE, lw=1.0))
    ax.text(49.8, y_leg+0.95, "Proceso / estimación", va="center", fontsize=7.6, color="#4a5568")
    # Píldora
    ax.add_patch(FancyBboxPatch((65.5, y_leg+0.1), 3.0, 1.7, boxstyle="round,pad=0.1,rounding_size=0.8",
                                fc=C_PILL2, ec="#3a5ba0", lw=1.0))
    ax.text(69.4, y_leg+0.95, "Motor físico / entregable", va="center", fontsize=7.6, color="#4a5568")

    ax.set_title("Arquitectura de Integración de Datos, Modelación Física (AERMOD) e Identificación Econométrica",
                 fontsize=11.0, fontweight="bold", color=C_DARK, pad=6)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_cap2_pipeline_arquitectura.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap2_pipeline_arquitectura.png")


# =====================================================================
# 3. EMISFACT + CAPA LÍMITE: PALETA LIMPIA SIN CAFÉ NI MOSTAZA
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
    # Paleta científica limpia (estilo Tesis_V4 + Fig 2.1): cero café, cero mostaza, cero verde
    perfiles_b1 = {
        "Fundición y metalurgia":  ([0.64, 0.96, 1.24, 1.25, 1.12, 0.79], "#c92a2a"),  # Carmesí (Fig 2.1)
        "Calderas industriales":   ([0.68, 0.98, 1.21, 1.22, 1.09, 0.82], "#2b6cb0"),  # Azul acero (Fig 2.1)
        "Turbinas de gas (CFE)":   ([0.81, 0.92, 1.02, 1.08, 1.19, 0.98], "#6c5ce7"),  # Índigo/violeta (Tesis_V4)
        "Hornos de vidrio y min.": ([0.94, 0.98, 1.04, 1.05, 1.02, 0.97], "#00a6d6"),  # Cian/cielo (Tesis_V4)
    }

    hrs_24 = np.arange(1, 25, dtype=float)
    hrs_eval = np.where(hrs_24 < 2.5, hrs_24 + 24.0, hrs_24)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.4, 7.8), dpi=300, sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.08], "hspace": 0.30}
    )

    # Franjas limpias: noche casi blanca para que respire, Matutino verde fresco, Vespertino naranja suave
    for ax in (ax1, ax2):
        ax.axvspan(1, 7,   color="#f8fafc", alpha=1.0,  zorder=0)
        ax.axvspan(7, 14,  color="#2ecc71", alpha=0.085, zorder=0)
        ax.axvspan(14, 20, color="#f39c12", alpha=0.085, zorder=0)
        ax.axvspan(20, 24, color="#f8fafc", alpha=1.0,  zorder=0)
        for xv in (7, 14, 20):
            ax.axvline(xv, color="#94a3b8", ls=":", lw=0.95, zorder=1)
        ax.grid(axis="y", linestyle=":", alpha=0.45, color="#cbd5e0")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Panel A: Líneas sólidas parejas con 24 círculos huecos (estilo Slide 34 de Tesis_V4)
    ax1.axhline(1.0, color="#94a3b8", lw=1.15, ls="--", alpha=0.9,
                label="Emisión constante 24/7 (factor = 1.0)", zorder=2)
    for lbl, (vals, col) in perfiles_b1.items():
        y_per = np.array(vals + [vals[0]])
        cs = CubicSpline(x_blk, y_per, bc_type="periodic")
        y_24 = cs(hrs_eval)
        ax1.plot(hrs_24, y_24, color=col, ls="-", lw=2.0,
                 marker="o", ms=4.2, mfc="white", mec=col, mew=1.45,
                 label=lbl, zorder=3)

    ax1.set_ylim(0.55, 1.48)
    ax1.set_ylabel("Factor horario EMISFACT ($f_{k,h}$)", fontsize=9.5, fontweight="bold")
    ax1.set_title("A. Perfiles horarios de operación industrial (EMISFACT, Tabla B.1) y jornadas escolares",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=8)
    ax1.legend(loc="lower center", ncol=3, fontsize=8.1, framealpha=0.96, edgecolor="#cbd5e0")

    ax1.text(4.0,  1.44, "Madrugada\n(inversión)", ha="center", va="top", fontsize=7.9, color="#64748b", style="italic")
    ax1.text(10.5, 1.44, "Turno Matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.3, fontweight="bold", color="#117a5b")
    ax1.text(17.0, 1.44, "Turno Vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.3, fontweight="bold", color="#b45309")
    ax1.text(22.0, 1.44, "Noche", ha="center", va="top", fontsize=7.9, color="#64748b", style="italic")

    # Panel B: Curva en grafito neutro (no compite con azules del Panel A) + callouts verde y naranja
    C_ATM = "#2d3748"
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color="#64748b", alpha=0.18, label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=C_ATM, ls="-", lw=2.1,
             marker="o", ms=4.3, mfc="white", mec=C_ATM, mew=1.5,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8,  "med"].iloc[0])
    z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])

    ax2.annotate(f"Entrada matutina (07–08 h):\ncapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8), xytext=(1.8, 1020), fontsize=8.1, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_TEAL, lw=1.25),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.3), zorder=5)
    ax2.annotate(f"Cierre vespertino (18–20 h):\ndescenso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19), xytext=(14.9, 1740), fontsize=8.1, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_AMBER, lw=1.25),
                 arrowprops=dict(arrowstyle="->", color=C_AMBER, lw=1.3), zorder=5)

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


if __name__ == "__main__":
    crear_fig1_pipeline()
    crear_fig3_emisfact_capa_limite()
    print(f"\n[LISTO] Figuras actualizadas en: {OUT_DIR}")
