import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

BASE    = "/Users/gabrielevangelista/thesis-cdmx-air"
OUT_DIR = f"{BASE}/figuras_tesis/finales"
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

C_NAVY     = "#005a9c"
C_RED      = "#b2182b"
C_DARK     = "#1a202c"
C_MUTED    = "#64748b"
C_MATH     = "#8c96a0"
C_TWFE_BAR = "#6baed6"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.4, 6.3), dpi=300)
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
    ("Placebo: Alta marg.\n" + r"(30 d post., $F_1 = 1.1$)",         None,        None,        None,         None),
]

y_pos = np.arange(6)[::-1]

# --- Panel A: Forma Reducida ---
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

# --- Panel B: TWFE físico vs. 2SLS físico ---
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
                label="TWFE físico — Lenguaje (POSTFILE)" if idx == 0 else None)

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
ax2.set_xlabel(r"Puntos en Lenguaje por $+0.01\ \mu\mathrm{g/m}^3$ en turno ($\approx 29\%$ de la media)", fontsize=9.1)
ax2.set_title("B. Atenuación TWFE vs. 2SLS físico en Lenguaje (POSTFILE)",
              fontsize=10.2, fontweight="bold", color=C_DARK, loc="left", pad=10)
ax2.legend(loc="upper left", fontsize=8.5, frameon=False)

fig.suptitle("Pilar 2 (AERMOD POSTFILE por turno): forma reducida y comparación TWFE–2SLS",
             fontsize=11.4, fontweight="bold", color=C_DARK, y=1.01)
fig.text(0.5, -0.01, "Nota: Marcadores muestran el coeficiente puntual; la barra gruesa indica el IC de Wald al 90% y la barra delgada al 95%.",
         ha="center", va="top", fontsize=8.4, color=C_MUTED, style="italic")

plt.tight_layout(rect=[0, 0.02, 1, 0.96])
out_path = f"{OUT_DIR}/fig_cap3_forest_pilar2_postfile.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"[OK] {out_path}")
