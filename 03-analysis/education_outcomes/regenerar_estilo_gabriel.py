import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
from matplotlib.ticker import AutoMinorLocator
from scipy.interpolate import CubicSpline

BASE       = "/Users/gabrielevangelista/thesis-cdmx-air"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
OUT_DIR    = f"{BASE}/figuras_tesis/finales"
os.makedirs(OUT_DIR, exist_ok=True)

# Estilo científico Gabriel (Tesis_V4.pdf): Serif, lienzo blanco puro, ejes limpios
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

C_NAVY   = "#005a9c"   # Lenguaje / Pilar 1 TWFE
C_RED    = "#b2182b"   # Fundición / Pilar 2 2SLS
C_VERM   = "#e8590c"   # Vidrio y minerales (alto impacto térmico/emisiones)
C_PURP   = "#6d28d9"   # Turbinas de gas CFE
C_STEEL  = "#2b8cbe"   # Calderas industriales (manufactura ligera)
C_ATM    = "#1e3a5f"   # Capa límite atmosférica
C_DARK   = "#1a202c"
C_MUTED  = "#64748b"
C_MATH   = "#8c96a0"   # Matemáticas (contraste neutro)


# =====================================================================
# FIGURA 3 (TESIS - CAP. 3.1.1): EMISFACT + CAPA LÍMITE (ESTILO SERIF)
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
    # Paleta narrativa: 2 ramas cálidas = 56 fuentes prioritarias; morado = CFE; azul acero = calderas ligeras
    perfiles_b1 = {
        "Fundición y metalurgia":   ([0.64, 0.96, 1.24, 1.25, 1.12, 0.79], C_RED),
        "Hornos de vidrio y min.":  ([0.94, 0.98, 1.04, 1.05, 1.02, 0.97], C_VERM),
        "Turbinas de gas (CFE)":    ([0.81, 0.92, 1.02, 1.08, 1.19, 0.98], C_PURP),
        "Calderas industriales":    ([0.68, 0.98, 1.21, 1.22, 1.09, 0.82], C_STEEL),
    }

    hrs_24 = np.arange(1, 25, dtype=float)
    hrs_eval = np.where(hrs_24 < 2.5, hrs_24 + 24.0, hrs_24)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.0, 7.6), dpi=300, sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.06], "hspace": 0.30}
    )
    fig.patch.set_facecolor("white")

    # Franjas neutras ultra-limpias (solo diferencian horario lectivo sin meter colores extra)
    for ax in (ax1, ax2):
        ax.set_facecolor("white")
        ax.axvspan(7, 14,  color="#f1f5f9", alpha=0.85, zorder=0)
        ax.axvspan(14, 20, color="#e9eef5", alpha=0.75, zorder=0)
        for xv in (7, 14, 20):
            ax.axvline(xv, color="#94a3b8", ls=":", lw=0.95, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    # --- Panel A: Perfiles EMISFACT (24 círculos huecos, líneas sólidas parejas) ---
    ax1.axhline(1.0, color="#64748b", lw=1.0, ls=":", zorder=2)
    ax1.text(24.25, 1.0, "Constante\n24/7 (1.0)", va="center", ha="left",
             fontsize=8.0, color="#475569", style="italic", clip_on=False)

    for lbl, (vals, col) in perfiles_b1.items():
        y_per = np.array(vals + [vals[0]])
        cs = CubicSpline(x_blk, y_per, bc_type="periodic")
        y_24 = cs(hrs_eval)
        ax1.plot(hrs_24, y_24, color=col, ls="-", lw=1.95,
                 marker="o", ms=4.3, mfc="white", mec=col, mew=1.55,
                 label=lbl, zorder=3)

    ax1.set_ylim(0.55, 1.46)
    ax1.set_yticks([0.6, 0.8, 1.0, 1.2, 1.4])
    ax1.set_ylabel(r"Factor horario EMISFACT ($f_{k,h}$)", fontsize=10.0)
    ax1.set_title("A. Perfiles horarios de operación industrial (EMISFACT, Tabla B.1) y jornadas escolares",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=10)

    # Leyenda limpia sin recuadro ubicada en el espacio abierto central inferior
    ax1.legend(loc="lower center", bbox_to_anchor=(0.56, 0.03), ncol=2,
               fontsize=8.8, frameon=False, columnspacing=1.8, handlelength=2.2)

    # Encabezados tipográficos de régimen horario (sin colores invasivos)
    ax1.text(4.0,  1.425, "Madrugada\n(inversión)", ha="center", va="top", fontsize=8.2, color=C_MUTED, style="italic")
    ax1.text(10.5, 1.425, "Turno Matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.5, fontweight="bold", color=C_DARK)
    ax1.text(17.0, 1.425, "Turno Vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.5, fontweight="bold", color=C_DARK)
    ax1.text(22.0, 1.425, "Noche", ha="center", va="top", fontsize=8.2, color=C_MUTED, style="italic")

    # --- Panel B: Altura de capa de mezcla real (AERMET) ---
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color=C_ATM, alpha=0.14, edgecolor="none", label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=C_ATM, ls="-", lw=2.0,
             marker="o", ms=4.4, mfc="white", mec=C_ATM, mew=1.55,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8,  "med"].iloc[0])
    z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])

    # Anotaciones directas con línea guía fina (estilo Tesis_V4, sin cajas pesadas)
    ax2.annotate(f"Entrada matutina (07–08 h)\nCapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8 + 30), xytext=(2.1, 1080), fontsize=8.5, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.0, shrinkA=4, shrinkB=4),
                 zorder=5)
    ax2.annotate(f"Cierre vespertino (18–20 h)\nDescenso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19 + 30), xytext=(14.4, 1780), fontsize=8.5, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.0, shrinkA=4, shrinkB=4),
                 zorder=5)

    ax2.set_xlim(1, 24)
    ax2.set_ylim(0, 2150)
    ax2.set_yticks([0, 500, 1000, 1500, 2000])
    ax2.set_xticks(range(1, 25, 2))
    ax2.set_xticklabels([f"{h:02d}:00" for h in range(1, 25, 2)], fontsize=8.8)
    ax2.set_xlabel("Hora local (convención hour-ending de AERMOD)", fontsize=10.0)
    ax2.set_ylabel(r"Altura de capa de mezcla $Z_i$ [m]", fontsize=10.0)
    ax2.set_title("B. Ciclo diurno de la altura de la capa límite planetaria en la ZMVM (AERMET, estación AICM)",
                  fontsize=10.6, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax2.legend(loc="upper left", fontsize=8.8, frameon=False)

    plt.subplots_adjust(right=0.90)
    plt.savefig(f"{OUT_DIR}/fig_cap3_emisfact_capa_limite.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_emisfact_capa_limite.png")


# =====================================================================
# FIGURA 4 (TESIS - CAP. 3.1.4): ROSA DE VIENTOS (SERIF, HUECOS, LIMPIA)
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

    # Gradiente azul -> índigo -> morado profundo (Tesis_V4), línea sólida + círculos huecos
    colores_yr = {2015: "#2b9bf0", 2017: "#5b4bff", 2019: "#581c87"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.8), dpi=300,
                                   subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor("white")

    for ax, data_dict, titulo, l1, l2 in [
        (ax1, wd_anual,
         "A. Promedio anual completo (8,760 h/año)",
         "Alta persistencia interanual",
         r"IV anual débil ($\mathrm{DE_{within}} = 0.051$, $F_1 = 2.64$)"),
        (ax2, wd_30d,
         "B. Ventana crítica: 30 días previos a PLANEA (07–19 h)",
         "Variación direccional exógena entre años",
         r"Primera etapa física relevante ($F_1 = 9.2$ a $12.6$)"),
    ]:
        ax.set_facecolor("white")
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 45), ["N", "NE", "E", "SE", "S", "SO", "O", "NO"],
                          fontsize=9.5, fontweight="bold", color=C_DARK)

        for yr in [2015, 2017, 2019]:
            f_pct = freq_16(data_dict[yr])
            col = colores_yr[yr]
            ax.plot(angles_closed, f_pct, color=col, ls="-", lw=1.9,
                    marker="o", ms=4.2, mfc="white", mec=col, mew=1.45, label=str(yr))
            ax.fill(angles_closed, f_pct, color=col, alpha=0.06)

        ax.set_ylim(0, 20)
        ax.set_yticks([5, 10, 15, 20])
        ax.set_yticklabels(["5%", "10%", "15%", "20%"], fontsize=8.0, color=C_MUTED)
        # 292.5° (ONO): completamente libre de las etiquetas O y NO
        ax.set_rlabel_position(292.5)
        ax.spines["polar"].set_color("#94a3b8")
        ax.spines["polar"].set_linewidth(0.85)
        ax.grid(True, linestyle=":", alpha=0.55, color="#cbd5e0")
        ax.set_title(titulo, fontsize=10.4, fontweight="bold", color=C_DARK, pad=18)

        # Pie limpio sin recuadro
        ax.text(0.5, -0.14, l1, transform=ax.transAxes, ha="center", va="top",
                fontsize=9.0, fontweight="bold", color=C_DARK)
        ax.text(0.5, -0.20, l2, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.6, color="#475569")

    # Señalar lóbulo dominante NE / ENE con línea guía limpia
    avg_anual = np.mean([freq_16(wd_anual[y])[:-1] for y in [2015, 2017, 2019]], axis=0)
    idx_pk = int(np.argmax(avg_anual))
    ax1.annotate("Corredor industrial\nNE / ENE (origen dominante)",
                 xy=(angles[idx_pk], avg_anual[idx_pk] + 0.5),
                 xytext=(np.deg2rad(50), 25.0),
                 fontsize=8.4, color="#581c87", fontweight="bold",
                 annotation_clip=False,
                 arrowprops=dict(arrowstyle="->", color="#581c87", lw=1.05))

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, [f"Levantamiento {l}" for l in labels], loc="upper center",
               bbox_to_anchor=(0.5, 0.975), ncol=3, fontsize=9.2, frameon=False)
    fig.suptitle("Distribución Direccional del Viento en la Cuenca de México (AICM, WMO 76679)",
                 fontsize=11.6, fontweight="bold", color=C_DARK, y=1.035)

    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    plt.savefig(f"{OUT_DIR}/fig_cap3_rosa_vientos_anual_vs_30d.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_rosa_vientos_anual_vs_30d.png")


# =====================================================================
# FIGURA 5 (TESIS - CAP. 3.2): FOREST PLOT PILAR 1 (ESTILO SERIF LIMPIO)
# =====================================================================
def crear_fig5_forest_pilar1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 6.0), dpi=300)
    fig.patch.set_facecolor("white")

    items_A = [
        ("Promedio general\n(Todas, Tabla 3.1)",                                              6.695,  9.417,   5.603,  8.080),
        ("Baja o media marg.\n" + r"(Todas, $\beta_1$)",                                      9.871,  9.580,   8.100,  8.147),
        ("Baja o media marg.\n" + r"(Públicas, $\beta_1$)",                                   2.543,  8.856,   2.947,  5.170),
        ("Alta marginación\n" + r"(Todas, total $\hat{\beta}_1+\hat{\beta}_2$)",            -89.406, 46.358, -69.995, 52.143),
        ("Alta marginación\n" + r"(Públicas, total $\hat{\beta}_1+\hat{\beta}_2$)",         -95.756, 42.562, -53.568, 51.655),
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
        ax.set_facecolor("white")
        ax.axvline(0, color=C_DARK, lw=1.0, ls="--", zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        for idx, (lbl, b_l, se_l, b_m, se_m) in enumerate(items):
            y = y_pos[idx]
            # Lenguaje (azul marino sólido)
            ax.plot([b_l - 1.96*se_l, b_l + 1.96*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=1.25, zorder=3)
            ax.plot([b_l - 1.645*se_l, b_l + 1.645*se_l], [y + 0.16, y + 0.16], color=C_NAVY, lw=3.0, zorder=4)
            ax.scatter([b_l], [y + 0.16], color=C_NAVY, marker="o", s=54, zorder=5,
                       label="Lenguaje y Comunicación" if idx == 0 else None)

            x_txt = b_l + 6.0 if -4 <= b_l <= 14 else b_l
            ha_txt = "left" if -4 <= b_l <= 14 else "center"
            ax.text(x_txt, y + 0.29, f"{b_l:.1f}", ha=ha_txt, va="bottom",
                    fontsize=8.2, fontweight="bold", color=C_NAVY, zorder=6)

            # Matemáticas (cuadrado hueco gris frío, retrocede visualmente)
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
        ax.set_title(title, fontsize=10.3, fontweight="bold", color=C_DARK, loc="left", pad=10)

    plot_forest(ax1, items_A,
                "A. Efecto promedio vs. heterogeneidad por marginación",
                r"Puntos PLANEA por $+1\ \mu\mathrm{g/m}^3$ anual", (-210, 65))
    plot_forest(ax2, items_B,
                "B. Robustez de la interacción (Alta Marg., públicas)",
                r"Interacción $\hat{\beta}_2$ por $+1\ \mu\mathrm{g/m}^3$ anual", (-220, 75))

    # Destacar bloque de alta marginación con tinte casi imperceptible
    ax1.axhspan(-0.52, 1.50, color="#eff6ff", alpha=0.85, zorder=0)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.975),
               ncol=2, fontsize=9.2, frameon=False)
    fig.suptitle("Pilar 1 (TWFE Anual): Efecto Regresivo en Lenguaje y Estabilidad ante Especificaciones",
                 fontsize=11.5, fontweight="bold", color=C_DARK, y=1.035)
    fig.text(0.5, -0.01, "Nota: Marcadores muestran el coeficiente puntual; la barra gruesa indica el IC al 90% y la barra delgada el IC al 95%.",
             ha="center", va="top", fontsize=8.4, color=C_MUTED, style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.92])
    plt.savefig(f"{OUT_DIR}/fig_cap3_forest_pilar1_twfe.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_forest_pilar1_twfe.png")


# =====================================================================
# FIGURA 6 (TESIS - CAP. 3.2): FOREST PLOT PILAR 2 (SERIF + SIMETRÍA)
# =====================================================================
def crear_fig6_forest_pilar2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.2), dpi=300)
    fig.patch.set_facecolor("white")

    items_RF = [
        ("Todas públicas\n(30 d previos)",               -4.870, 1.928,  -1.432, 2.388),
        ("Baja o media marg.\n(30 d previos)",           -3.809, 2.195,  -1.067, 2.538),
        ("Alta marginación\n(30 d previos)",            -10.700, 4.823,  -4.910, 3.783),
        ("Alta marginación\n(30 d, Mun. × Año)",        -18.435, 7.819, -15.447, 6.888),
        ("Alta marginación\n(15 d previos)",             -6.931, 4.823,  -0.069, 5.003),
        ("Placebo: Alta marg.\n(30 d posteriores)",     -10.429, 8.186,  -6.846, 9.236),
    ]

    items_CMP = [
        ("Todas públicas\n" + r"(30 d, $F_1 = 8.9$)",                    -1.03/100,   3.93/100,   -172.20/100,  89.71/100),
        ("Baja o media marg.\n" + r"(30 d, $F_1 = 7.2$)",                -0.33/100,   3.71/100,   -133.71/100, 101.33/100),
        ("Alta marginación\n" + r"(30 d, $F_1 = 9.2$)",                 -41.59/100,  36.38/100,   -450.38/100, 163.98/100),
        ("Alta marginación\n" + r"(30 d, Mun.$\times$Año, $F_1 = 12.6$)", 10.19/100, 56.37/100,  -1098.43/100, 504.96/100),
        ("Alta marginación\n" + r"(15 d, $F_1 = 15.2$)",                -46.82/100,  39.75/100,   -216.13/100, 138.63/100),
    ]

    # --- Panel A: Forma Reducida ---
    yA = np.arange(len(items_RF))[::-1]
    ax1.set_facecolor("white")
    ax1.axvline(0, color=C_DARK, lw=1.0, ls="--", zorder=1)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax1.axhspan(-0.52, 0.50, color="#fdf2f2", alpha=0.85, zorder=0)

    for idx, (lbl, bl, sel, bm, sem) in enumerate(items_RF):
        y = yA[idx]
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

    ax1.set_yticks(yA)
    ax1.set_yticklabels([x[0] for x in items_RF], fontsize=8.5)
    ax1.set_ylim(-0.62, len(items_RF) - 0.28)
    ax1.set_xlim(-36, 14)
    ax1.set_xlabel("Puntos PLANEA por +1 DE de viento desfavorable", fontsize=9.3)
    ax1.set_title("A. Forma reducida: efecto directo del choque de viento",
                  fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax1.legend(loc="upper left", fontsize=8.6, frameon=False)

    # --- Panel B: TWFE físico (hueco azul) vs. 2SLS físico (diamante carmesí) ---
    C_TWFE_BAR = "#6baed6"
    yB = np.arange(len(items_CMP))[::-1]
    ax2.set_facecolor("white")
    ax2.axvline(0, color=C_DARK, lw=1.0, ls="--", zorder=1)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax2.axhspan(0.50, 2.50, color="#f8fafc", alpha=0.95, zorder=0)

    for idx, (lbl, btw, setw, biv, seiv) in enumerate(items_CMP):
        y = yB[idx]
        ax2.plot([btw - 1.96*setw, btw + 1.96*setw], [y + 0.16, y + 0.16], color=C_TWFE_BAR, lw=1.3, zorder=3)
        ax2.plot([btw - 1.645*setw, btw + 1.645*setw], [y + 0.16, y + 0.16], color=C_TWFE_BAR, lw=2.8, zorder=4)
        ax2.scatter([btw], [y + 0.16], facecolor="white", edgecolor=C_NAVY, linewidth=1.75,
                    marker="o", s=52, zorder=5,
                    label="TWFE físico — Lenguaje (POSTFILE)" if idx == 0 else None)

        ax2.plot([biv - 1.96*seiv, biv + 1.96*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=1.35, zorder=3)
        ax2.plot([biv - 1.645*seiv, biv + 1.645*seiv], [y - 0.16, y - 0.16], color=C_RED, lw=3.1, zorder=4)
        ax2.scatter([biv], [y - 0.16], color=C_RED, marker="D", s=46, zorder=5,
                    label=r"2SLS físico — Lenguaje (viento $Q_{2015}$)" if idx == 0 else None)
        ax2.text(biv, y - 0.34, f"{biv:.2f}", ha="center", va="top",
                 fontsize=8.1, fontweight="bold", color=C_RED)

    ax2.set_yticks(yB)
    ax2.set_yticklabels([x[0] for x in items_CMP], fontsize=8.5)
    ax2.set_ylim(-0.68, len(items_CMP) - 0.32)
    ax2.set_xlim(-22.5, 3.8)
    ax2.set_xlabel(r"Puntos en Lenguaje por $+0.01\ \mu\mathrm{g/m}^3$ en turno ($\approx 29\%$ de la media)", fontsize=9.1)
    ax2.set_title("B. Atenuación TWFE vs. 2SLS físico en Lenguaje (POSTFILE)",
                  fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)
    ax2.legend(loc="upper left", fontsize=8.5, frameon=False)

    ax2.text(0.02, 0.03,
             r"Nota: Placebo 2SLS ($F_1 = 1.1$) es nulo ($p = 0.406$)" + "\ny se omite por amplitud del intervalo.",
             transform=ax2.transAxes, ha="left", va="bottom", fontsize=7.8,
             color=C_MUTED, style="italic")

    fig.suptitle("Pilar 2 (AERMOD POSTFILE por Turno): Identificación Causal por Viento Exógeno y Atenuación del TWFE",
                 fontsize=11.4, fontweight="bold", color=C_DARK, y=1.01)
    fig.text(0.5, -0.01, "Nota: Marcadores muestran el coeficiente puntual; la barra gruesa indica el IC al 90% y la barra delgada el IC al 95%.",
             ha="center", va="top", fontsize=8.4, color=C_MUTED, style="italic")

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    plt.savefig(f"{OUT_DIR}/fig_cap3_forest_pilar2_postfile.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_cap3_forest_pilar2_postfile.png")


# =====================================================================
# FIGURA 2 (DEFENSA): CONO DE VIENTO vs. RADIOS (ESTILO SERIF LIMPIO)
# =====================================================================
def crear_fig2_cono_vs_radios():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 5.7), dpi=300)
    fig.patch.set_facecolor("white")

    grid = np.linspace(-3.4, 3.4, 320)
    X, Y = np.meshgrid(grid, grid)
    R = np.maximum(np.sqrt(X**2 + Y**2), 0.18)

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
        ax.set_facecolor("white")
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-3.4, 3.4)
        ax.set_aspect("equal")
        ax.set_xlabel("Distancia Este–Oeste desde la fuente [km]", fontsize=9.5)
        ax.set_ylabel("Distancia Norte–Sur desde la fuente [km]", fontsize=9.5)
        ax.axhline(0, color="#e2e8f0", lw=0.8, zorder=1)
        ax.axvline(0, color="#e2e8f0", lw=0.8, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Panel A: Radios concéntricos
    ax1.add_patch(plt.Circle((0, 0), 3.0, facecolor="#eff6ff", edgecolor=C_NAVY, alpha=0.45, lw=1.2, ls="--", zorder=1))
    ax1.add_patch(plt.Circle((0, 0), 1.0, facecolor="#fef3c7", edgecolor=C_VERM, alpha=0.50, lw=1.4, ls="--", zorder=2))
    ax1.contourf(X, Y, pluma_plot, levels=np.linspace(0.04, 1.0, 12), cmap="Reds", alpha=0.26, zorder=2)

    ax1.scatter([0], [0], marker="^", s=145, c=C_DARK, edgecolors="white", lw=0.9, zorder=6)
    ax1.scatter(*esc_A, s=95, facecolor="white", edgecolor="#16a34a", lw=2.0, zorder=6)
    ax1.scatter(*esc_B, s=95, c=C_RED, edgecolors="white", lw=0.9, zorder=6)
    ax1.scatter(*esc_C, s=85, facecolor="white", edgecolor=C_NAVY, lw=2.0, zorder=6)

    ax1.annotate("Tratamiento ingenuo\n(r ≤ 1 km)", xy=(0.12, -0.98), xytext=(1.1, -1.8),
                 fontsize=8.3, fontweight="bold", color="#9a3412",
                 arrowprops=dict(arrowstyle="->", color=C_VERM, lw=1.0))
    ax1.annotate("Control ingenuo\n(1 < r ≤ 3 km)", xy=(2.1, -2.0), xytext=(1.05, -3.15),
                 fontsize=8.3, fontweight="bold", color=C_NAVY,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.0))
    ax1.annotate("Escuela A (0.8 km, barlovento)\nError Tipo I: aire limpio,\nclasificada como 'tratada'",
                 xy=esc_A, xytext=(0.45, 2.05), fontsize=8.1, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.05), zorder=7)
    ax1.annotate("Escuela B (2.2 km, sotavento)\nControl contaminado:\nrecibe la pluma de lleno",
                 xy=esc_B, xytext=(-3.25, -0.35), fontsize=8.1, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.05), zorder=7)
    ax1.set_title("A. Radios concéntricos tradicionales (sesgo por viento)",
                  fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)

    # Panel B: Cono direccional
    cf = ax2.contourf(X, Y, pluma_plot, levels=np.linspace(0.0, 1.0, 21),
                      vmin=0.0, vmax=1.0, cmap="YlOrRd", alpha=0.82, zorder=2)
    ax2.contour(X, Y, pluma_norm, levels=[0.08], colors=C_RED, linewidths=1.0, linestyles="--", zorder=3)
    ax2.add_patch(plt.Circle((0, 0), 1.0, fill=False, edgecolor="#cbd5e0", lw=0.85, ls=":", zorder=2))
    ax2.add_patch(plt.Circle((0, 0), 3.0, fill=False, edgecolor="#cbd5e0", lw=0.85, ls=":", zorder=2))

    ax2.add_patch(FancyArrowPatch((0, 0), (-2.55, -2.55), arrowstyle="-|>",
                                  mutation_scale=15, color=C_DARK, lw=1.9, zorder=5))
    ax2.text(-2.72, -3.02, r"Vector de viento $\vec{w}$" + "\n(NE → SO)", fontsize=8.4,
             fontweight="bold", color=C_DARK, ha="center")

    ax2.plot([0, -2.25], [0, -1.35], color=C_NAVY, lw=1.15, ls="-.", zorder=5)
    ax2.add_patch(patches.Arc((0, 0), 2.1, 2.1, angle=0, theta1=211.0, theta2=225.0,
                              color=C_NAVY, lw=1.5, zorder=6))
    ax2.text(-1.26, -0.96, r"$\theta$", fontsize=10.5, fontweight="bold", color=C_NAVY, zorder=7)

    ax2.scatter([0], [0], marker="^", s=145, c=C_DARK, edgecolors="white", lw=0.9, zorder=6)
    ax2.scatter(*esc_A, s=95, facecolor="white", edgecolor="#16a34a", lw=2.0, zorder=6)
    ax2.scatter(*esc_B, s=95, c=C_RED, edgecolors="white", lw=0.9, zorder=6)
    ax2.scatter(*esc_C, s=85, facecolor="white", edgecolor=C_NAVY, lw=2.0, zorder=6)

    ax2.annotate("Escuela A (barlovento)\nExposición ≈ 0 (" + r"$\cos\theta < 0$" + ")",
                 xy=esc_A, xytext=(0.55, 2.15), fontsize=8.1, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.05), zorder=7)
    ax2.annotate("Escuela B (sotavento)\nAlta exposición capturada\npor AERMOD e IV",
                 xy=esc_B, xytext=(0.45, -2.55), fontsize=8.1, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.05), zorder=7)
    ax2.annotate("Escuela C (lateral)\nControl limpio\n(fuera del cono)",
                 xy=esc_C, xytext=(-3.25, 2.25), fontsize=8.1, color=C_DARK,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.05), zorder=7)

    ax2.text(-3.22, 0.35, "Cono a sotavento (Ec. 3.6):\n" + r"$\max\{0,\cos\theta\}^{10}\ /\ d^{1.5}$",
             fontsize=8.6, color=C_DARK, zorder=7)

    cbar = plt.colorbar(cf, ax=ax2, fraction=0.044, pad=0.03, ticks=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    cbar.set_label("Exposición relativa [adimensional, 0–1]", fontsize=8.8)
    cbar.ax.tick_params(labelsize=8.2)
    cbar.outline.set_linewidth(0.8)
    ax2.set_title("B. Dispersión direccional (AERMOD + cono de viento)",
                  fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/fig_defensa_cono_viento_vs_radios.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("[OK] fig_defensa_cono_viento_vs_radios.png")


if __name__ == "__main__":
    crear_fig3_emisfact_capa_limite()
    crear_fig4_rosa_vientos()
    crear_fig5_forest_pilar1()
    crear_fig6_forest_pilar2()
    crear_fig2_cono_vs_radios()
    print(f"\n[LISTO] Figuras regeneradas con estilo editorial en: {OUT_DIR}")
