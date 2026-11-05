"""
Convierte las series anuales normalizadas (8,760 horas, suma = 1.0)
al formato EMISFACT MHRDOW de AERMOD (864 factores con media = 1.0).
"""
import glob, os
import pandas as pd
import numpy as np

# Ajusta esta ruta a la carpeta donde están tus 5 archivos CSV de curvas industriales
CURVES_DIR = "/Users/gabrielevangelista/thesis-cdmx-air/02-data/raw/industrial_curves"
OUT_DIR = "/Users/gabrielevangelista/thesis-cdmx-air/02-data/processed/emisfact_mhrdow"
os.makedirs(OUT_DIR, exist_ok=True)

# Calendario base de 8,760 horas (año estándar no bisiesto, ej. 2017)
DT_INDEX = pd.date_range("2017-01-01 00:00:00", periods=8760, freq="h")

def convert_curve_to_mhrdow(csv_path, sector_tag):
    vals = []
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "," in line:
                parts = line.strip().split(",")
                try:
                    vals.append(float(parts[1]))
                except ValueError:
                    continue

    if len(vals) != 8760:
        raise ValueError(f"El archivo {csv_path} tiene {len(vals)} filas en lugar de 8760.")

    df = pd.DataFrame({"dt": DT_INDEX, "frac": vals})
    # Escalar para que la media anual sea exactamente 1.0 (conservación de masa en AERMOD)
    df["scalar"] = (df["frac"] / df["frac"].sum()) * 8760.0
    df["month"] = df["dt"].dt.month
    df["hour"] = df["dt"].dt.hour + 1  # 1..24 para AERMOD
    # Tipo de día AERMOD: 1 = Lunes-Viernes (0..4), 2 = Sábado (5), 3 = Domingo (6)
    df["day_type"] = df["dt"].dt.dayofweek.map(lambda d: 1 if d < 5 else (2 if d == 5 else 3))

    # Calcular promedio por (day_type, month, hour) -> 3 x 12 x 24 = 864 celdas
    pivot = df.groupby(["day_type", "month", "hour"])["scalar"].mean().unstack("hour")

    # Exportar CSV de auditoría (864 valores) y bloque de texto MHRDOW para AERMOD
    out_csv = os.path.join(OUT_DIR, f"mhrdow_{sector_tag}.csv")
    pivot.to_csv(out_csv)

    out_emi = os.path.join(OUT_DIR, f"emisfact_{sector_tag}.emi")
    day_labels = {1: "WEEKDAYS (LUN-VIE)", 2: "SATURDAYS (SAB)", 3: "SUNDAYS (DOM)"}
    with open(out_emi, "w", encoding="utf-8") as f:
        f.write(f"** Perfil EMISFACT MHRDOW (864 factores) para rama: {sector_tag}\n")
        for dt_code in [1, 2, 3]:
            f.write(f"** --- {day_labels[dt_code]} ---\n")
            for m in range(1, 13):
                hrs = [pivot.loc[(dt_code, m), h] for h in range(1, 25)]
                # Escribir en 3 líneas de 8 horas por cada mes para máxima legibilidad en Fortran
                for i in range(0, 24, 8):
                    chunk = "  ".join(f"{v:8.5f}" for v in hrs[i:i+8])
                    f.write(f"SO EMISFACT  {sector_tag:<12s}  MHRDOW  {chunk}\n")

    print(f"[OK] {sector_tag:<18s} | Media={df['scalar'].mean():.4f} | Min={pivot.min().min():.4f} | Max={pivot.max().max():.4f} -> {out_emi}")

if __name__ == "__main__":
    for path in sorted(glob.glob(os.path.join(CURVES_DIR, "*.csv"))):
        name = os.path.basename(path).replace("_year_normalization.csv", "").replace(".csv", "").upper()
        convert_curve_to_mhrdow(path, name[:12])