"""
Convierte la matriz promedio MHRDOW del CENACE a dos perfiles EMISFACT para AERMOD:
1. CFE_BASE: Proporcional a la demanda absoluta total.
2. CFE_PUNTA: Proporcional solo a la demanda excedente del P75 (Plantas pico).
"""
import pandas as pd
import numpy as np

# Rutas de entrada y salida
IN_CSV = "/Users/gabrielevangelista/thesis-cdmx-air/02-data/processed/cenace_cfe/cenace_sin_cen_mhrdow_864.csv"
OUT_BASE = "/Users/gabrielevangelista/thesis-cdmx-air/02-data/processed/cenace_cfe/emisfact_cfe_base.emi"
OUT_PUNTA = "/Users/gabrielevangelista/thesis-cdmx-air/02-data/processed/cenace_cfe/emisfact_cfe_punta.emi"

# Leer la matriz 864 calculada previamente
df = pd.read_csv(IN_CSV)

# Extraer el string numérico del day_type ("1_Weekday" -> 1)
df["dt_code"] = df["day_type"].str[0].astype(int)

# Umbral del Percentil 75% reportado
UMBRAL_P75 = 7003.53

# 1. Perfil A: CFE BASE (Proporcional a la demanda total mwh_mean)
suma_base = df["mwh_mean"].sum()
df["factor_base"] = (df["mwh_mean"] / suma_base) * 864.0

# 2. Perfil B: CFE PUNTA (Solo opera cuando mwh_mean > UMBRAL_P75)
df["mwh_excedente"] = np.where(df["mwh_mean"] > UMBRAL_P75, df["mwh_mean"] - UMBRAL_P75, 0.0)
suma_punta = df["mwh_excedente"].sum()

if suma_punta > 0:
    df["factor_punta"] = (df["mwh_excedente"] / suma_punta) * 864.0
else:
    df["factor_punta"] = 0.0

def write_emisfact(df, col_factor, source_id, out_file):
    day_labels = {1: "WEEKDAYS (LUN-VIE)", 2: "SATURDAYS (SAB)", 3: "SUNDAYS (DOM)"}
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"** Perfil EMISFACT MHRDOW (864 factores) para: {source_id}\n")
        f.write(f"** Media del factor: {df[col_factor].mean():.4f} | Máximo: {df[col_factor].max():.4f}\n")
        
        for dt_code in [1, 2, 3]:
            f.write(f"\n** --- {day_labels[dt_code]} ---\n")
            sub = df[df["dt_code"] == dt_code].sort_values(["month", "hour"])
            
            for m in range(1, 13):
                hrs = sub[sub["month"] == m][col_factor].tolist()
                if len(hrs) != 24:
                    print(f"Advertencia: Faltan horas en Mes {m}, Tipo {dt_code}")
                    hrs += [0.0] * (24 - len(hrs))
                
                # Escribir en 3 líneas de 8 horas
                for i in range(0, 24, 8):
                    chunk = "  ".join(f"{v:8.5f}" for v in hrs[i:i+8])
                    f.write(f"SO EMISFACT  {source_id:<12s}  MHRDOW  {chunk}\n")

write_emisfact(df, "factor_base", "CFE_BASE", OUT_BASE)
write_emisfact(df, "factor_punta", "CFE_PUNTA", OUT_PUNTA)

print(f"[OK] Perfil CFE_BASE generado en: {OUT_BASE}")
print(f"     Max factor base: {df['factor_base'].max():.2f}")
print(f"[OK] Perfil CFE_PUNTA generado en: {OUT_PUNTA}")
print(f"     Max factor punta: {df['factor_punta'].max():.2f}")
print(f"     Horas activas (factor > 0): {(df['factor_punta'] > 0).sum()} de 864 celdas MHRDOW.")