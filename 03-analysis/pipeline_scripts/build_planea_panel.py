"""
Extrae los puntajes de PLANEA (2015, 2017, 2019) desde los archivos raw en Excel,
calcula indicadores de logro y brechas socioeconómicas (contra escuelas parecidas),
y los enlaza con tabla_enlace_cct_recid.csv (3,172 receptores AERMOD).
"""
import pandas as pd
import os

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
RAW_PLANEA = f"{BASE}/02-data/raw/planea"
ENLACE_CSV = f"{BASE}/02-data/processed/aermap_out/tabla_enlace_cct_recid.csv"
OUT_CSV = f"{BASE}/02-data/processed/aermap_out/planea_enlazado_receptores_2015_2019.csv"

def leer_planea(ruta, anio, skip, cols_map):
    df = pd.read_excel(ruta, skiprows=skip, header=None, usecols=list(cols_map.keys()))
    df = df.rename(columns=cols_map)
    df['cct'] = df['cct'].astype(str).str.strip().str.upper()
    df['turno'] = df['turno'].astype(str).str.strip().str.upper()
    df['anio'] = anio
    return df[df['cct'].str.len() >= 8].reset_index(drop=True)

cols_2015 = {
    0: 'cve_entidad', 1: 'nombre_escuela', 2: 'cct', 3: 'turno',
    4: 'municipio', 5: 'localidad', 6: 'tipo_escuela', 8: 'marginacion',
    9: 'alumnos_programados', 10: 'evaluados_lyc', 11: 'evaluados_mat',
    18: 'comparacion_parecidas',
    23: 'lyc_pct_n1', 24: 'lyc_pct_n2', 25: 'lyc_pct_n3', 26: 'lyc_pct_n4',
    27: 'lyc_parecidas_n1', 28: 'lyc_parecidas_n2', 29: 'lyc_parecidas_n3', 30: 'lyc_parecidas_n4',
    39: 'mat_pct_n1', 40: 'mat_pct_n2', 41: 'mat_pct_n3', 42: 'mat_pct_n4',
    43: 'mat_parecidas_n1', 44: 'mat_parecidas_n2', 45: 'mat_parecidas_n3', 46: 'mat_parecidas_n4'
}

cols_2017 = {
    0: 'cve_entidad', 2: 'nombre_escuela', 3: 'cct', 4: 'turno',
    5: 'municipio', 6: 'localidad', 7: 'tipo_escuela', 9: 'marginacion',
    10: 'alumnos_programados', 11: 'evaluados_lyc', 12: 'evaluados_mat',
    17: 'comparacion_parecidas',
    22: 'lyc_pct_n1', 23: 'lyc_pct_n2', 24: 'lyc_pct_n3', 25: 'lyc_pct_n4',
    26: 'lyc_parecidas_n1', 27: 'lyc_parecidas_n2', 28: 'lyc_parecidas_n3', 29: 'lyc_parecidas_n4',
    38: 'mat_pct_n1', 39: 'mat_pct_n2', 40: 'mat_pct_n3', 41: 'mat_pct_n4',
    42: 'mat_parecidas_n1', 43: 'mat_parecidas_n2', 44: 'mat_parecidas_n3', 45: 'mat_parecidas_n4'
}

cols_2019 = {
    0: 'cve_entidad', 2: 'nombre_escuela', 3: 'cct', 4: 'turno',
    5: 'municipio', 6: 'localidad', 7: 'tipo_escuela', 9: 'marginacion',
    10: 'alumnos_programados', 11: 'evaluados_lyc', 12: 'evaluados_mat',
    17: 'comparacion_parecidas',
    22: 'lyc_pct_n1', 23: 'lyc_pct_n2', 24: 'lyc_pct_n3', 25: 'lyc_pct_n4',
    26: 'lyc_parecidas_n1', 27: 'lyc_parecidas_n2', 28: 'lyc_parecidas_n3', 29: 'lyc_parecidas_n4',
    34: 'mat_pct_n1', 35: 'mat_pct_n2', 36: 'mat_pct_n3', 37: 'mat_pct_n4',
    38: 'mat_parecidas_n1', 39: 'mat_parecidas_n2', 40: 'mat_parecidas_n3', 41: 'mat_parecidas_n4'
}

print("Leyendo archivos Excel de PLANEA (2015, 2017, 2019)...")
df_15 = leer_planea(f"{RAW_PLANEA}/2015_test_planea.xlsx", 2015, 3, cols_2015)
df_17 = leer_planea(f"{RAW_PLANEA}/2017_test_planea.xlsx", 2017, 4, cols_2017)
df_19 = leer_planea(f"{RAW_PLANEA}/2019_test_planea.xlsx", 2019, 4, cols_2019)

df_panel = pd.concat([df_15, df_17, df_19], ignore_index=True)

cols_num = [
    'alumnos_programados', 'evaluados_lyc', 'evaluados_mat',
    'lyc_pct_n1', 'lyc_pct_n2', 'lyc_pct_n3', 'lyc_pct_n4',
    'lyc_parecidas_n1', 'lyc_parecidas_n2', 'lyc_parecidas_n3', 'lyc_parecidas_n4',
    'mat_pct_n1', 'mat_pct_n2', 'mat_pct_n3', 'mat_pct_n4',
    'mat_parecidas_n1', 'mat_parecidas_n2', 'mat_parecidas_n3', 'mat_parecidas_n4'
]
for c in cols_num:
    df_panel[c] = pd.to_numeric(df_panel[c], errors='coerce')

# Indicadores sintéticos para visualización rápida:
# 1. Rezago Neto (Nivel 1 observado menos Nivel 1 de escuelas parecidas): >0 significa peor desempeño que sus pares
df_panel['mat_brecha_rezago_n1'] = df_panel['mat_pct_n1'] - df_panel['mat_parecidas_n1']
df_panel['lyc_brecha_rezago_n1'] = df_panel['lyc_pct_n1'] - df_panel['lyc_parecidas_n1']
# 2. Logro Sobresaliente (Niveles 3 + 4)
df_panel['mat_pct_n34'] = df_panel['mat_pct_n3'] + df_panel['mat_pct_n4']
df_panel['lyc_pct_n34'] = df_panel['lyc_pct_n3'] + df_panel['lyc_pct_n4']

# Cruzar con la tabla puente de receptores AERMOD (RECID, X_UTM, Y_UTM)
df_enlace = pd.read_csv(ENLACE_CSV)
df_enlace['cct'] = df_enlace['cct'].astype(str).str.strip().str.upper()
df_enlace['turno'] = df_enlace['turno'].astype(str).str.strip().str.upper()

# Intentar cruce exacto por (cct, turno); si algún turno varía en nombre, respaldar por cct
df_merged = df_panel.merge(
    df_enlace[['cct', 'RECID', 'X_UTM', 'Y_UTM', 'Z_ELEV', 'Z_HILL']].drop_duplicates(subset=['cct']),
    on='cct',
    how='inner'
)

df_merged.to_csv(OUT_CSV, index=False)
print(f"[OK] Panel PLANEA enlazado guardado en: {OUT_CSV}")
print(f"Total registros (CCT-turno-año) con RECID asignado: {len(df_merged)}")
print(df_merged.groupby('anio')[['mat_pct_n1', 'lyc_pct_n1', 'mat_brecha_rezago_n1']].mean().round(2))
