"""
Recorre todos los CSV de 'Dem Pron Balance SEN MDA Dia de Operacion' (2019-2021),
extrae las filas de Sistema='SIN' y Area='CEN', y genera:
1. Serie horaria multianual limpia (cenace_sin_cen_hourly_2019_2021.csv)
2. Año tipo promedio de 8,760 horas (cenace_sin_cen_typical_8760.csv)
3. Resumen estadístico y percentiles para definir el umbral de despacho de CFE.
"""
import glob, os, re
import pandas as pd
import numpy as np

# Ajusta esta ruta si tu carpeta de CENACE está en otro directorio
BASE = "/Users/gabrielevangelista/thesis-cdmx-air/02-data/raw/demanda"
SEARCH_PATHS = [
    f"{BASE}/**/Dem Pron Balance SEN MDA Dia de Operacion",
    "/Users/gabrielevangelista/**/Dem Pron Balance SEN MDA Dia de Operacion"
]

cenace_dir = None
for pattern in SEARCH_PATHS:
    matches = glob.glob(pattern, recursive=True)
    if matches:
        cenace_dir = matches[0]
        break

if not cenace_dir:
    raise FileNotFoundError("No se encontró la carpeta 'Dem Pron Balance SEN MDA Dia de Operacion'. Ajusta cenace_dir.")

print(f"Leyendo archivos desde: {cenace_dir}")
csv_files = sorted(glob.glob(os.path.join(cenace_dir, "*.csv")))
print(f"Total de archivos CSV encontrados: {len(csv_files)}")

records = []
for fn in csv_files:
    bname = os.path.basename(fn)
    m = re.search(r"Operacion\s+(\d{4}-\d{2}-\d{2})", bname)
    if not m:
        continue
    op_date = m.group(1)

    with open(fn, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if '"SIN"' in line and '"CEN"' in line:
                parts = [p.strip().strip('"') for p in line.split(",")]
                if len(parts) >= 4 and parts[0] == "SIN" and parts[1] == "CEN":
                    try:
                        hr = int(parts[2])
                        mwh = float(parts[3])
                        if 1 <= hr <= 24:
                            records.append((op_date, hr, mwh, bname))
                    except ValueError:
                        continue

df = pd.DataFrame(records, columns=["date", "hour", "mwh", "filename"])
# Si hay dos versiones del mismo día, conservar la última versión (orden alfabético por timestamp vYYYY...)
df = df.sort_values("filename").drop_duplicates(subset=["date", "hour"], keep="last").copy()
df["dt"] = pd.to_datetime(df["date"])
df = df[(df["dt"].dt.year >= 2019) & (df["dt"].dt.year <= 2021)].sort_values(["date", "hour"]).reset_index(drop=True)

df["year"] = df["dt"].dt.year
df["month"] = df["dt"].dt.month
df["day"] = df["dt"].dt.day
df["dow"] = df["dt"].dt.dayofweek
df["day_type"] = df["dow"].map(lambda d: "1_Weekday" if d < 5 else ("2_Saturday" if d == 5 else "3_Sunday"))

OUT_DIR = f"{BASE}/02-data/processed/cenace_cfe"
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Guardar serie multianual completa
full_out = f"{OUT_DIR}/cenace_sin_cen_2019_2021_full.csv"
df.to_csv(full_out, index=False)

# 2. Construir año promedio estándar de 8,760 horas (excluyendo 29 de febrero)
df_no_leap = df[~((df["month"] == 2) & (df["day"] == 29))].copy()
typical_8760 = (
    df_no_leap.groupby(["month", "day", "hour"], as_index=False)
    .agg(mwh_mean=("mwh", "mean"), mwh_max=("mwh", "max"), mwh_min=("mwh", "min"), n_years=("year", "nunique"))
)
typical_out = f"{OUT_DIR}/cenace_sin_cen_typical_8760.csv"
typical_8760.to_csv(typical_out, index=False)

# 3. Construir tabla MHRDOW promedio (Mes x Tipo de Día x Hora = 864 celdas)
mhrdow_cen = (
    df.groupby(["day_type", "month", "hour"], as_index=False)
    .agg(mwh_mean=("mwh", "mean"), mwh_p90=("mwh", lambda x: np.percentile(x, 90)), mwh_max=("mwh", "max"))
)
mhrdow_out = f"{OUT_DIR}/cenace_sin_cen_mhrdow_864.csv"
mhrdow_cen.to_csv(mhrdow_out, index=False)

print("\n=== RESUMEN DE EXTRACCIÓN CENACE (SIN - CEN, 2019-2021) ===")
print(f"Días únicos procesados: {df['date'].nunique()} | Horas totales: {len(df)}")
print(df.groupby("year")["mwh"].agg(["count", "min", "mean", "median", "max"]))

print("\n=== DISTRIBUCIÓN DE DEMANDA EN EL AÑO PROMEDIO (8,760 HORAS) ===")
print(f"Horas en año tipo: {len(typical_8760)}")
qs = np.percentile(typical_8760["mwh_mean"], [0, 10, 25, 50, 75, 85, 90, 95, 98, 100])
for p, val in zip([0, 10, 25, 50, 75, 85, 90, 95, 98, 100], qs):
    print(f"  Percentil {p:3d}%: {val:8.2f} MWh")

print("\n=== TOP 10 HORAS PROMEDIO DEL DÍA EN EL ÁREA CENTRAL (MWh) ===")
hr_prof = typical_8760.groupby("hour")["mwh_mean"].agg(["mean", "max"]).sort_values("mean", ascending=False)
print(hr_prof.head(10).to_string())
print(f"\n[OK] Archivos guardados en: {OUT_DIR}")
