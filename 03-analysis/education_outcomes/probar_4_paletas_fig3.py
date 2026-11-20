import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy.interpolate import CubicSpline

BASE       = "/Users/gabrielevangelista/thesis-cdmx-air"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
OUT_DIR    = f"{BASE}/figuras_tesis/pruebas_paleta"
os.makedirs(OUT_DIR, exist_ok=True)

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

# Leer capa límite real una sola vez
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
curvas_vals = {
    "Fundición y metalurgia":       [0.64, 0.96, 1.24, 1.25, 1.12, 0.79],
    "Vidrio, min. y secado quím.":  [0.94, 0.98, 1.04, 1.05, 1.02, 0.97],
    "Turbinas de gas (CFE)":        [0.81, 0.92, 1.02, 1.08, 1.19, 0.98],
    "Calderas industriales":        [0.68, 0.98, 1.21, 1.22, 1.09, 0.82],
}
hrs_24 = np.arange(1, 25, dtype=float)
hrs_eval = np.where(hrs_24 < 2.5, hrs_24 + 24.0, hrs_24)

PALETAS = {
    "opcionA_editorial": {
        "nombre": "Opción A — Editorial (Azul + Acento Cálido)",
        "curvas": {
            "Fundición y metalurgia":       "#b2182b",
            "Vidrio, min. y secado quím.":  "#e08214",
            "Turbinas de gas (CFE)":        "#2166ac",
            "Calderas industriales":        "#67a9cf",
        },
        "atm": "#2166ac",
    },
    "opcionB_okabe_ito": {
        "nombre": "Opción B — Okabe-Ito (Estándar Científico)",
        "curvas": {
            "Fundición y metalurgia":       "#d55e00",
            "Vidrio, min. y secado quím.":  "#e69f00",
            "Turbinas de gas (CFE)":        "#0072b2",
            "Calderas industriales":        "#009e73",
        },
        "atm": "#0072b2",
    },
    "opcionC_paul_tol": {
        "nombre": "Opción C — Paul Tol Muted",
        "curvas": {
            "Fundición y metalurgia":       "#882255",
            "Vidrio, min. y secado quím.":  "#cc6677",
            "Turbinas de gas (CFE)":        "#332288",
            "Calderas industriales":        "#44aa99",
        },
        "atm": "#332288",
    },
    "opcionD_sobria_azules": {
        "nombre": "Opción D — Sobria (Azules + Carmesí)",
        "curvas": {
            "Fundición y metalurgia":       "#b2182b",
            "Vidrio, min. y secado quím.":  "#08306b",
            "Turbinas de gas (CFE)":        "#2171b5",
            "Calderas industriales":        "#6baed6",
        },
        "atm": "#252525",
    },
}

z_h8  = float(pbl_stats.loc[pbl_stats["hr"] == 8,  "med"].iloc[0])
z_h19 = float(pbl_stats.loc[pbl_stats["hr"] == 19, "med"].iloc[0])

for key, cfg in PALETAS.items():
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11.0, 7.6), dpi=300, sharex=True,
        gridspec_kw={"height_ratios": [1.0, 1.06], "hspace": 0.30}
    )
    fig.patch.set_facecolor("white")

    # Fondos neutros ultra-limpios (no compiten con ninguna paleta)
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

    for lbl, vals in curvas_vals.items():
        col = cfg["curvas"][lbl]
        cs = CubicSpline(x_blk, np.array(vals + [vals[0]]), bc_type="periodic")
        ax1.plot(hrs_24, cs(hrs_eval), color=col, ls="-", lw=2.0,
                 marker="o", ms=4.3, mfc="white", mec=col, mew=1.55,
                 label=lbl, zorder=3)

    ax1.set_ylim(0.55, 1.46)
    ax1.set_yticks([0.6, 0.8, 1.0, 1.2, 1.4])
    ax1.set_ylabel(r"Factor horario EMISFACT ($f_{k,h}$)", fontsize=10.0)
    ax1.set_title("A. Perfiles horarios de operación industrial (EMISFACT, Tabla B.1) y jornadas escolares",
                  fontsize=10.6, fontweight="bold", color="#1a202c", loc="left", pad=10)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.56, 0.03), ncol=2,
               fontsize=8.7, frameon=False, columnspacing=1.6, handlelength=2.2)

    ax1.text(4.0,  1.425, "Madrugada\n(inversión)", ha="center", va="top", fontsize=8.2, color="#64748b", style="italic")
    ax1.text(10.5, 1.425, "Turno Matutino\n(07:00–14:00 h)", ha="center", va="top", fontsize=8.5, fontweight="bold", color="#1a202c")
    ax1.text(17.0, 1.425, "Turno Vespertino\n(13:00–20:00 h)", ha="center", va="top", fontsize=8.5, fontweight="bold", color="#1a202c")
    ax1.text(22.0, 1.425, "Noche", ha="center", va="top", fontsize=8.2, color="#64748b", style="italic")

    # Panel B
    c_atm = cfg["atm"]
    ax2.fill_between(pbl_stats["hr"], pbl_stats["p25"], pbl_stats["p75"],
                     color=c_atm, alpha=0.14, edgecolor="none", label="Rango intercuartílico (P25–P75)")
    ax2.plot(pbl_stats["hr"], pbl_stats["med"], color=c_atm, ls="-", lw=2.0,
             marker="o", ms=4.4, mfc="white", mec=c_atm, mew=1.55,
             label="Mediana horaria (AERMET 2015, 2017 y 2019)")

    ax2.annotate(f"Entrada matutina (07–08 h)\nCapa baja (~{z_h8:.0f} m) + arranque\nde fundiciones y calderas",
                 xy=(8, z_h8 + 30), xytext=(2.1, 1080), fontsize=8.5, color="#1a202c",
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.0, shrinkA=4, shrinkB=4), zorder=5)
    ax2.annotate(f"Cierre vespertino (18–20 h)\nDescenso térmico (~{z_h19:.0f} m) con\npico de turbinas y operación activa",
                 xy=(19, z_h19 + 30), xytext=(14.4, 1780), fontsize=8.5, color="#1a202c",
                 arrowprops=dict(arrowstyle="->", color="#475569", lw=1.0, shrinkA=4, shrinkB=4), zorder=5)

    ax2.set_xlim(1, 24)
    ax2.set_ylim(0, 2150)
    ax2.set_yticks([0, 500, 1000, 1500, 2000])
    ax2.set_xticks(range(1, 25, 2))
    ax2.set_xticklabels([f"{h:02d}:00" for h in range(1, 25, 2)], fontsize=8.8)
    ax2.set_xlabel("Hora local (convención hour-ending de AERMOD)", fontsize=10.0)
    ax2.set_ylabel(r"Altura de capa de mezcla $Z_i$ [m]", fontsize=10.0)
    ax2.set_title("B. Ciclo diurno de la altura de la capa límite planetaria en la ZMVM (AERMET, estación AICM)",
                  fontsize=10.6, fontweight="bold", color="#1a202c", loc="left", pad=10)
    ax2.legend(loc="upper left", fontsize=8.8, frameon=False)

    plt.subplots_adjust(right=0.90)
    out_path = f"{OUT_DIR}/fig3_{key}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out_path}")
