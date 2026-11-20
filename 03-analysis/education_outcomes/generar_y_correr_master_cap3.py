import io, os, json, warnings, contextlib

CELLS = [
    ("markdown", "# Capítulo 3 — Notebook Maestro de Tablas Econométricas (ZMVM 2015–2019)\n\nReproduce en orden exacto las Tablas 3.1, 3.2, 3.3 y 3.4 (validación física horaria AERMOD `POSTFILE` por turno escolar)."),

    ("code", r'''# === CELDA 1: CARGA DEL PANEL ZMVM (SIN TOLUCA) Y ARMONIZACIÓN DE TURNOS ===
import os, warnings, datetime
import numpy as np
import pandas as pd
import pyfixest as pf

warnings.filterwarnings("ignore", category=UserWarning)

BASE         = "/Users/gabrielevangelista/thesis-cdmx-air"
AERMAP_OUT   = f"{BASE}/02-data/processed/aermap_out"
AERMET_OUT   = f"{BASE}/02-data/processed/aermet_out"
RUN_DIR_EMIS = f"{BASE}/03-analysis/run_aermod_emisfact"
RUN_DIR_BASE = f"{BASE}/03-analysis/run_aermod"
POST_DIR     = f"{BASE}/03-analysis/run_aermod_postfile_95d"

def get_stars(p):
    return "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.10 else ""))

def leer_plt_aermod(filepath):
    records = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("*"):
                continue
            p = s.split()
            if len(p) >= 5:
                try:
                    records.append({
                        "X_UTM": round(float(p[0]), 2),
                        "Y_UTM": round(float(p[1]), 2),
                        "CONC":  float(p[2]),
                        "ZELEV": float(p[3]),
                        "ZHILL": float(p[4]),
                    })
                except ValueError:
                    continue
    return pd.DataFrame(records)

# 1. Salidas anuales AERMOD con EMISFACT + corrida plana 24/7
anios_panel = [2015, 2017, 2019]
grupos_plt = {
    "FUNDICION_METAL": "fund",
    "HORNO_VIDRIO":    "vidr",
    "QUIMICA":         "quim",
    "TURBINAS_CFE":    "turb",
    "CALDERAS":        "cald",
}

lista_aermod = []
for yr in anios_panel:
    df_yr = leer_plt_aermod(f"{RUN_DIR_EMIS}/plot_emi_annual_all_{yr}.plt").rename(columns={"CONC": "PM25_ALL"})
    df_yr["anio"] = yr
    for nombre_col, sufijo in grupos_plt.items():
        df_g = leer_plt_aermod(f"{RUN_DIR_EMIS}/plot_emi_annual_{sufijo}_{yr}.plt")[["X_UTM", "Y_UTM", "CONC"]].rename(columns={"CONC": f"PM25_{nombre_col}"})
        df_yr = df_yr.merge(df_g, on=["X_UTM", "Y_UTM"], how="left")
    f_base = f"{RUN_DIR_BASE}/plot_annual_all_{yr}.plt"
    if os.path.exists(f_base):
        df_b = leer_plt_aermod(f_base)[["X_UTM", "Y_UTM", "CONC"]].rename(columns={"CONC": "PM25_BASELINE_24_7"})
        df_yr = df_yr.merge(df_b, on=["X_UTM", "Y_UTM"], how="left")
    lista_aermod.append(df_yr)
df_aermod = pd.concat(lista_aermod, ignore_index=True)

# 2. Meteorología anual AERMET (.sfc)
met_anual = []
for yr in anios_panel:
    rows_sfc = []
    with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
        for line in f.readlines()[1:]:
            p = line.split()
            if len(p) >= 22:
                rows_sfc.append({
                    "mo": int(p[1]), "dy": int(p[2]), "hr": int(p[4]),
                    "zic": float(p[9]), "ws": float(p[15]),
                    "temp_k": float(p[18]), "pamt": float(p[21]),
                })
    df_sfc = pd.DataFrame(rows_sfc)
    df_sfc["ws_clean"] = df_sfc["ws"].replace([99.0, 999.0, -9.0], np.nan)
    df_sfc.loc[df_sfc["ws_clean"] > 50, "ws_clean"] = np.nan
    df_sfc["temp_c"] = df_sfc["temp_k"] - 273.15
    df_sfc.loc[(df_sfc["temp_k"] > 330) | (df_sfc["temp_k"] < 240), "temp_c"] = np.nan
    df_sfc["pamt_clean"] = df_sfc["pamt"].where((df_sfc["pamt"] >= 0) & (df_sfc["pamt"] < 200), 0.0)
    daily_t = df_sfc.groupby(["mo", "dy"])["temp_c"].agg(["max", "min"])
    met_anual.append({
        "anio": yr,
        "ws_mean": df_sfc["ws_clean"].mean(),
        "tmax_mean": daily_t["max"].mean(),
        "tmin_mean": daily_t["min"].mean(),
        "precip_sum": df_sfc["pamt_clean"].sum(),
    })
df_met = pd.DataFrame(met_anual)

# 3. Panel PLANEA filtrado a Cuenca de México (X_UTM >= 460 km)
df_planea = pd.read_csv(f"{AERMAP_OUT}/planea_enlazado_receptores_2015_2019.csv")
df_planea["X_UTM"] = df_planea["X_UTM"].round(2)
df_planea["Y_UTM"] = df_planea["Y_UTM"].round(2)
df_planea = df_planea[df_planea["X_UTM"] >= 460000].copy()

mat_raw = 1*df_planea["mat_pct_n1"] + 2*df_planea["mat_pct_n2"] + 3*df_planea["mat_pct_n3"] + 4*df_planea["mat_pct_n4"]
lyc_raw = 1*df_planea["lyc_pct_n1"] + 2*df_planea["lyc_pct_n2"] + 3*df_planea["lyc_pct_n3"] + 4*df_planea["lyc_pct_n4"]
df_planea["mat_std_500"] = 500.0 + 100.0 * (mat_raw - mat_raw.mean()) / mat_raw.std()
df_planea["lyc_std_500"] = 500.0 + 100.0 * (lyc_raw - lyc_raw.mean()) / lyc_raw.std()
df_planea["alta_marg"]   = df_planea["marginacion"].astype(str).str.upper().str.contains("ALTA|MUY ALTA", na=False).astype(float)
df_planea["mun_anio"]    = df_planea["municipio"].astype(str) + "_" + df_planea["anio"].astype(str)

df_reg = df_planea.merge(df_aermod, on=["X_UTM", "Y_UTM", "anio"], how="inner").merge(df_met, on="anio", how="left")

# 4. Armonización de turnos e identificador de unidad escolar
MAPA_TURNO = {
    "1": "MATUTINO", "2": "VESPERTINO", "3": "NOCTURNO", "4": "DISCONTINUO", "5": "TIEMPO COMPLETO",
    "AMPLIADO": "TIEMPO COMPLETO", "COMPLETO": "TIEMPO COMPLETO",
    "JORNADA AMPLIAD": "TIEMPO COMPLETO", "JORNADA AMPLIADA": "TIEMPO COMPLETO",
    "CONTINUO": "TIEMPO COMPLETO", "CONTINUO (TIEMPO COMPLETO)": "TIEMPO COMPLETO",
}
df_reg["turno_norm"] = df_reg["turno"].astype(str).str.upper().str.strip().replace(MAPA_TURNO)
filas_max = df_reg.groupby(["cct", "anio"]).size().groupby("cct").max()
cct_una_fila = set(filas_max[filas_max == 1].index)
df_reg["cct_una_fila"] = df_reg["cct"].isin(cct_una_fila)

def turno_modal(s):
    s_val = s[s != "DISCONTINUO"]
    return (s_val if len(s_val) else s).mode().iloc[0]

turno_cct = df_reg[df_reg["cct_una_fila"]].groupby("cct")["turno_norm"].agg(turno_modal)
df_reg["turno"] = np.where(df_reg["cct_una_fila"], df_reg["cct"].map(turno_cct), df_reg["turno_norm"])
df_reg["id_cct_clean"] = np.where(df_reg["cct_una_fila"], df_reg["cct"].astype(str), df_reg["cct"].astype(str) + "_" + df_reg["turno"].astype(str))

# 5. Controles microclimáticos y transformaciones
z_std  = (df_reg["ZELEV"] - df_reg["ZELEV"].mean()) / df_reg["ZELEV"].std()
zh_std = (df_reg["ZHILL"] - df_reg["ZHILL"].mean()) / df_reg["ZHILL"].std()
df_reg["W_temp_z"]  = df_reg["tmax_mean"] * z_std
df_reg["W_temp_z2"] = (df_reg["tmax_mean"] ** 2) * (z_std ** 2)
df_reg["W_wind_zh"] = df_reg["ws_mean"] * zh_std
df_reg["W_prec_z"]  = (df_reg["precip_sum"] / 100.0) * z_std

df_reg["PM25_x_AltaMarg"] = df_reg["PM25_ALL"] * df_reg["alta_marg"]
df_reg["PM25_x_NoMarg"]   = df_reg["PM25_ALL"] * (1.0 - df_reg["alta_marg"])
df_reg["BASE_x_AltaMarg"] = df_reg["PM25_BASELINE_24_7"] * df_reg["alta_marg"]
df_reg["arcsinh_PM25"]    = np.arcsinh(df_reg["PM25_ALL"] * 100.0)
df_reg["log_PM25"]        = np.log(df_reg["PM25_ALL"] + 0.001)

controles_W = "W_temp_z + W_temp_z2 + W_wind_zh + W_prec_z"
FE = "id_cct_clean + anio"
VC = {"CRV1": "RECID"}

df_pub = df_reg[~df_reg["tipo_escuela"].astype(str).str.upper().str.contains("PRIVAD|PARTICULAR", na=False)].copy()

print(f"[OK] Panel ZMVM listo: N_todas = {len(df_reg):,} | N_publicas = {len(df_pub):,} | CCT = {df_reg['cct'].nunique():,} | RECID = {df_reg['RECID'].nunique():,}")
'''),

    ("code", r'''# === CELDA 2: TABLA 3.1 — ESPECIFICACIÓN CENTRAL (MCO Y TWFE) ===
specs_31 = [
    ("(1) MCO",            "PM25_ALL | anio"),
    ("(2) TWFE base",      "PM25_ALL | id_cct_clean + anio"),
    ("(3) TWFE + met",     f"PM25_ALL + {controles_W} | id_cct_clean + anio"),
    ("(4) TWFE + mun*yr",  f"PM25_ALL + {controles_W} | id_cct_clean + mun_anio"),
]

print("=== TABLA 3.1: ESPECIFICACIÓN CENTRAL (MCO Y TWFE) ===")
for panel, y_std, y_n1 in [("PANEL A: MATEMÁTICAS", "mat_std_500", "mat_pct_n1"),
                           ("PANEL B: LENGUAJE",    "lyc_std_500", "lyc_pct_n1")]:
    print(f"\n{panel}")
    for lbl, rhs in specs_31:
        m = pf.feols(f"{y_std} ~ {rhs}", data=df_reg, vcov=VC)
        r2w = getattr(m, "_r2_within", None)
        r2s = f"{r2w:.4f}" if r2w is not None else "  --  "
        b, se, p = m.coef()["PM25_ALL"], m.se()["PM25_ALL"], m.pvalue()["PM25_ALL"]
        print(f"  {lbl:18s} | Beta = {b:8.3f}{get_stars(p):3s} ({se:6.3f}, p={p:.4f}) | R2w={r2s} | N={m._N:,}")
    m5 = pf.feols(f"{y_n1} ~ PM25_ALL + {controles_W} | {FE}", data=df_reg, vcov=VC)
    b, se, p = m5.coef()["PM25_ALL"], m5.se()["PM25_ALL"], m5.pvalue()["PM25_ALL"]
    print(f"  (5) Nivel I (%)    | Beta = {b:8.3f}{get_stars(p):3s} ({se:6.3f}, p={p:.4f}) | R2w={m5._r2_within:.4f} | N={m5._N:,}")
'''),

    ("code", r'''# === CELDA 3: TABLA 3.2 — HETEROGENEIDAD POR RAMA AP-42 Y POR MARGINACIÓN ===
ramas = ["PM25_FUNDICION_METAL", "PM25_HORNO_VIDRIO", "PM25_QUIMICA", "PM25_TURBINAS_CFE", "PM25_CALDERAS"]
ramas_str = " + ".join(ramas)

print("=== TABLA 3.2: HETEROGENEIDAD POR RAMAS AP-42 Y MARGINACIÓN (6 COLUMNAS) ===")
for asig, y in [("MATEMÁTICAS (Cols 1-3)", "mat_std_500"), ("LENGUAJE (Cols 4-6)", "lyc_std_500")]:
    print(f"\n--- {asig} ---")
    m_ram = pf.feols(f"{y} ~ {ramas_str} + {controles_W} | {FE}", data=df_reg, vcov=VC)
    print(f"  [Col Ramas | N={m_ram._N:,}, R2w={m_ram._r2_within:.4f}]")
    for r in ramas:
        b, se, p = m_ram.coef()[r], m_ram.se()[r], m_ram.pvalue()[r]
        print(f"    {r:22s}: {b:9.3f}{get_stars(p):3s} ({se:7.3f}, p={p:.4f})")

    for sub_lbl, d in [("Todas", df_reg), ("Públicas", df_pub)]:
        m_int = pf.feols(f"{y} ~ PM25_ALL + PM25_x_AltaMarg + {controles_W} | {FE}", data=d, vcov=VC)
        m_tot = pf.feols(f"{y} ~ PM25_x_NoMarg + PM25_x_AltaMarg + {controles_W} | {FE}", data=d, vcov=VC)
        print(f"  [Col Marg {sub_lbl:8s} | N={m_int._N:,}, R2w={m_int._r2_within:.4f}]")
        for lbl_v, mod, v in [
            ("PM25_ALL (base)",           m_int, "PM25_ALL"),
            ("PM25 x AltaMarg (interac)", m_int, "PM25_x_AltaMarg"),
            ("Efecto TOTAL AltaMarg",     m_tot, "PM25_x_AltaMarg"),
        ]:
            b, se, p = mod.coef()[v], mod.se()[v], mod.pvalue()[v]
            print(f"    {lbl_v:26s}: {b:9.3f}{get_stars(p):3s} ({se:7.3f}, p={p:.4f})")
'''),

    ("code", r'''# === CELDA 4: TABLA 3.3 — ROBUSTEZ DE LA INTERACCIÓN DE MARGINACIÓN (SECUNDARIAS PÚBLICAS) ===
print("=== TABLA 3.3 (PANEL A): ROBUSTEZ INTERACCIÓN MARGINACIÓN (AERMOD ANUAL) ===")
for asig, y in [("Lenguaje", "lyc_std_500"), ("Matemáticas", "mat_std_500")]:
    print(f"\n{asig}:")
    specs_rob = [
        ("(1) Central (RECID)",        f"{y} ~ PM25_ALL + PM25_x_AltaMarg + {controles_W} | {FE}",                   VC,                      "PM25_x_AltaMarg"),
        ("(2) Cluster municipio",      f"{y} ~ PM25_ALL + PM25_x_AltaMarg + {controles_W} | {FE}",                   {"CRV1": "municipio"},   "PM25_x_AltaMarg"),
        ("(3) EF municipio x año",     f"{y} ~ PM25_ALL + PM25_x_AltaMarg + {controles_W} | id_cct_clean + mun_anio", VC,                      "PM25_x_AltaMarg"),
        ("(4) Sin controles W",        f"{y} ~ PM25_ALL + PM25_x_AltaMarg | {FE}",                                   VC,                      "PM25_x_AltaMarg"),
        ("(5) Emisión constante 24/7", f"{y} ~ PM25_BASELINE_24_7 + BASE_x_AltaMarg + {controles_W} | {FE}",         VC,                      "BASE_x_AltaMarg"),
    ]
    for lbl, fml, vcov_s, v in specs_rob:
        m = pf.feols(fml, data=df_pub, vcov=vcov_s)
        b, se, p = m.coef()[v], m.se()[v], m.pvalue()[v]
        print(f"  {lbl:28s} | {b:8.3f}{get_stars(p):3s} ({se:6.3f}, p={p:.4f}) | N={m._N:,}")

print("\n=== PRUEBAS ADICIONALES EFECTO PROMEDIO (TODAS Y PÚBLICAS) ===")
for asig, y in [("Lenguaje", "lyc_std_500"), ("Matemáticas", "mat_std_500")]:
    for lbl, d, v in [
        ("log_PM25 (todas)",     df_reg, "log_PM25"),
        ("arcsinh_PM25 (todas)", df_reg, "arcsinh_PM25"),
        ("24/7 plana (todas)",   df_reg, "PM25_BASELINE_24_7"),
        ("PM25_ALL (públicas)",  df_pub, "PM25_ALL"),
    ]:
        m = pf.feols(f"{y} ~ {v} + {controles_W} | {FE}", data=d, vcov=VC)
        print(f"  {asig:11s} | {lbl:21s} | {m.coef()[v]:8.3f} ({m.se()[v]:6.3f}, p={m.pvalue()[v]:.4f})")
'''),

    ("code", r'''# === CELDA 5: CONSTRUCCIÓN DEL INSTRUMENTO EXÓGENO DE VIENTO (30D, 15D, POST30, ENE-MAY) ===
fechas_planea_dt = {
    2015: datetime.date(2015, 6, 17),
    2017: datetime.date(2017, 6, 14),
    2019: datetime.date(2019, 6, 11),
}

df_src = pd.read_csv(f"{AERMAP_OUT}/catalogo_285_fuentes_aermod_ap42.csv")
Xs, Ys, Q_2015 = df_src["X_UTM"].values, df_src["Y_UTM"].values, df_src["Q_GS_2015"].values

rec_unicos = df_reg[["RECID", "X_UTM", "Y_UTM"]].drop_duplicates().reset_index(drop=True)
dx_km = (rec_unicos["X_UTM"].values[:, None] - Xs[None, :]) / 1000.0
dy_km = (rec_unicos["Y_UTM"].values[:, None] - Ys[None, :]) / 1000.0
dist_km = np.maximum(np.sqrt(dx_km**2 + dy_km**2), 0.25)
ux, uy = dx_km / dist_km, dy_km / dist_km
aten_dist = 1.0 / (dist_km ** 1.5)

f_emisfact_24 = np.array([
    0.65, 0.62, 0.60, 0.60, 0.63, 0.72,
    0.88, 1.05, 1.18, 1.25, 1.28, 1.30,
    1.28, 1.25, 1.26, 1.28, 1.26, 1.22,
    1.15, 1.05, 0.92, 0.82, 0.75, 0.68,
])

VENTANAS = {"30D": (0, 30), "15D": (0, 15), "POST30": (-30, -1)}
TURNOS_IV = {"MAT": (7, 13), "VESP": (13, 19)}

def leer_horas_sfc(yr):
    f_exam = fechas_planea_dt[yr]
    filas = []
    with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
        for line in f.readlines()[1:]:
            p = line.split()
            if len(p) < 22:
                continue
            mo, dy, hr = int(p[1]), int(p[2]), int(p[4])
            zic, zim = float(p[9]), float(p[10])
            ws, wd = float(p[15]), float(p[16])
            if not (0 < ws < 50 and 0 <= wd <= 360):
                continue
            try:
                fecha = datetime.date(yr, mo, dy)
            except ValueError:
                continue
            z_mix = max([v for v in [zic, zim, 150.0] if 0 < v < 5000])
            trap = f_emisfact_24[(hr - 1) % 24] / (max(ws, 0.5) * np.sqrt(z_mix / 500.0))
            filas.append((mo, (f_exam - fecha).days, fecha.weekday(), hr, wd, trap))
    return pd.DataFrame(filas, columns=["mo", "dias_antes", "dow", "hr", "wd", "trap"])

def indice_cono(sub, Q):
    out = np.zeros(len(rec_unicos))
    if len(sub) == 0:
        return out
    wd_rad = np.deg2rad(sub["wd"].values)
    wx_u, wy_u = -np.sin(wd_rad), -np.cos(wd_rad)
    sectores = np.floor(sub["wd"].values / 10.0).astype(int) % 36
    trap = sub["trap"].values
    for sec in range(36):
        m = (sectores == sec)
        if not np.any(m):
            continue
        wx_m, wy_m = np.mean(wx_u[m]), np.mean(wy_u[m])
        norm = max(np.sqrt(wx_m**2 + wy_m**2), 1e-6)
        cono = np.maximum(0.0, ux * (wx_m / norm) + uy * (wy_m / norm)) ** 10
        out += np.sum(cono * (aten_dist * Q[None, :]), axis=1) * (np.sum(trap[m]) / len(sub))
    return out

registros_v = []
for yr in fechas_planea_dt:
    Q_yr = df_src[f"Q_GS_{yr}"].values
    df_h = leer_horas_sfc(yr)
    df_h = df_h[(df_h["dow"] < 5) & (df_h["hr"].between(7, 19))]
    res = rec_unicos[["RECID"]].copy()
    res["anio"] = yr
    # Ventanas 30D, 15D y POST30
    for w_nom, (d_ini, d_fin) in VENTANAS.items():
        for t_nom, (h1, h2) in TURNOS_IV.items():
            sub = df_h[df_h["dias_antes"].between(d_ini, d_fin) & df_h["hr"].between(h1, h2)]
            res[f"IVRAW_{w_nom}_{t_nom}"] = indice_cono(sub, Q_2015)
            res[f"EXP_{w_nom}_{t_nom}"]   = indice_cono(sub, Q_yr)
    # Semestre lectivo Ene-May (para Tabla 3.3 Panel B)
    sub_em = df_h[df_h["mo"].between(1, 5)]
    res["EXP_ENEMAY_ALL"] = indice_cono(sub_em, Q_yr)
    for t_nom, (h1, h2) in TURNOS_IV.items():
        res[f"EXP_ENEMAY_{t_nom}"] = indice_cono(sub_em[sub_em["hr"].between(h1, h2)], Q_yr)
    registros_v.append(res)

df_v = pd.concat(registros_v, ignore_index=True)

escala_30 = df_reg["PM25_ALL"].mean() / df_v["EXP_30D_MAT"].mean()
escala_em = df_reg["PM25_ALL"].mean() / df_v["EXP_ENEMAY_ALL"].mean()

for c in [c for c in df_v.columns if c.startswith("IVRAW_")]:
    df_v[c.replace("IVRAW_", "IV_")] = (df_v[c] - df_v[c].mean()) / df_v[c].std()
for w_nom in VENTANAS:
    for t_nom in TURNOS_IV:
        df_v[f"PM25_{w_nom}_{t_nom}"] = df_v[f"EXP_{w_nom}_{t_nom}"] * escala_30
df_v["PM25_LECTIVO"] = df_v["EXP_ENEMAY_ALL"] * escala_em
df_v["PM25_EM_MAT"]  = df_v["EXP_ENEMAY_MAT"] * escala_em
df_v["PM25_EM_VESP"] = df_v["EXP_ENEMAY_VESP"] * escala_em

cols_keep = [c for c in df_v.columns if c.startswith(("IV_", "PM25_"))]
df_reg = df_reg.merge(df_v[["RECID", "anio"] + cols_keep], on=["RECID", "anio"], how="left")

es_vesp = df_reg["turno"].astype(str).str.upper().str.contains("VESP|2").values
for w_nom in VENTANAS:
    df_reg[f"IV_{w_nom}"]   = np.where(es_vesp, df_reg[f"IV_{w_nom}_VESP"], df_reg[f"IV_{w_nom}_MAT"])
    df_reg[f"PM25_{w_nom}"] = np.where(es_vesp, df_reg[f"PM25_{w_nom}_VESP"], df_reg[f"PM25_{w_nom}_MAT"])
    df_reg[f"PM25_{w_nom}_x_Marg"] = df_reg[f"PM25_{w_nom}"] * df_reg["alta_marg"]
df_reg["PM25_EM_TURNO"]        = np.where(es_vesp, df_reg["PM25_EM_VESP"], df_reg["PM25_EM_MAT"])
df_reg["PM25_LECTIVO_x_Marg"]  = df_reg["PM25_LECTIVO"] * df_reg["alta_marg"]
df_reg["PM25_EM_TURNO_x_Marg"] = df_reg["PM25_EM_TURNO"] * df_reg["alta_marg"]

df_pub = df_reg[~df_reg["tipo_escuela"].astype(str).str.upper().str.contains("PRIVAD|PARTICULAR", na=False)].copy()

print("=== TABLA 3.3 (PANEL B): ROBUSTEZ INTERACCIÓN EN SEMESTRE LECTIVO ENE-MAY ===")
for lbl, v_base, v_int in [
    ("(6) Ene-May 07-19h",     "PM25_LECTIVO",  "PM25_LECTIVO_x_Marg"),
    ("(7) Ene-May por turno",  "PM25_EM_TURNO", "PM25_EM_TURNO_x_Marg"),
]:
    m_l = pf.feols(f"lyc_std_500 ~ {v_base} + {v_int} + {controles_W} | {FE}", data=df_pub, vcov=VC)
    m_m = pf.feols(f"mat_std_500 ~ {v_base} + {v_int} + {controles_W} | {FE}", data=df_pub, vcov=VC)
    print(f"  {lbl:22s} | LyC={m_l.coef()[v_int]:8.3f}{get_stars(m_l.pvalue()[v_int]):3s} ({m_l.se()[v_int]:6.3f}, p={m_l.pvalue()[v_int]:.4f}) | Mat={m_m.coef()[v_int]:8.3f} ({m_m.se()[v_int]:6.3f}, p={m_m.pvalue()[v_int]:.4f})")
'''),

    ("code", r'''# === CELDA 6: EXTRACCIÓN FÍSICA HORARIA POSTFILE (ug/m3) Y TABLA 3.4 DEFINITIVA ===
FECHAS_TS = {
    2015: pd.Timestamp("2015-06-17"),
    2017: pd.Timestamp("2017-06-14"),
    2019: pd.Timestamp("2019-06-11"),
}

# Convención hour-ending de AERMOD (HR=8 es 07:00-08:00)
HORAS_TURNO = {
    "MATUTINO":        set(range(8, 15)),   # 07:00 - 14:00
    "VESPERTINO":      set(range(14, 21)),  # 13:00 - 20:00
    "TIEMPO COMPLETO": set(range(9, 17)),   # 08:00 - 16:00
    "NOCTURNO":        set(range(18, 23)),  # 17:00 - 22:00
    "DISCONTINUO":     set(range(8, 20)),   # 07:00 - 19:00
}

def procesar_postfile(filepath, anio):
    df = pd.read_csv(
        filepath, sep=r"\s+", skiprows=8,
        usecols=[0, 1, 2, 8], names=["X_UTM", "Y_UTM", "CONC", "DATE"],
        dtype={"X_UTM": np.float64, "Y_UTM": np.float64, "CONC": np.float32, "DATE": np.int64},
    )
    df["X_UTM"] = df["X_UTM"].round(2)
    df["Y_UTM"] = df["Y_UTM"].round(2)
    df = df[df["X_UTM"] >= 460000].copy()

    hr  = (df["DATE"] % 100).astype(np.int8)
    ymd = df["DATE"] // 100
    fecha = pd.to_datetime({"year": (ymd // 10000) + 2000, "month": (ymd // 100) % 100, "day": ymd % 100})
    dias_rel = (fecha - FECHAS_TS[anio]).dt.days

    def agg_ventana(mask, sufijo):
        sub = df.loc[mask, ["X_UTM", "Y_UTM", "CONC"]].copy()
        sub["HR"] = hr[mask].values
        res = sub.groupby(["X_UTM", "Y_UTM"], as_index=False)["CONC"].mean().rename(columns={"CONC": f"24h_{sufijo}"})
        for t_lbl, hrs_set in HORAS_TURNO.items():
            gt = sub[sub["HR"].isin(hrs_set)].groupby(["X_UTM", "Y_UTM"], as_index=False)["CONC"].mean()
            res = res.merge(gt.rename(columns={"CONC": f"{t_lbl}_{sufijo}"}), on=["X_UTM", "Y_UTM"], how="left")
        return res

    out = agg_ventana((dias_rel >= -30) & (dias_rel <= -1), "30d_prev")
    out = out.merge(agg_ventana((dias_rel >= -15) & (dias_rel <= -1), "15d_prev"), on=["X_UTM", "Y_UTM"])
    out = out.merge(agg_ventana((dias_rel >= 1)   & (dias_rel <= 30), "30d_post"), on=["X_UTM", "Y_UTM"])
    out["anio"] = anio
    return out

df_real = pd.concat([
    procesar_postfile(f"{POST_DIR}/post_real_2015.plt", 2015),
    procesar_postfile(f"{POST_DIR}/post_real_2017.plt", 2017),
    procesar_postfile(f"{POST_DIR}/post_real_2019.plt", 2019),
], ignore_index=True)

df_fija = pd.concat([
    df_real[df_real["anio"] == 2015].copy(),
    procesar_postfile(f"{POST_DIR}/post_fija2015_2017.plt", 2017),
    procesar_postfile(f"{POST_DIR}/post_fija2015_2019.plt", 2019),
], ignore_index=True)

df_real = df_real.rename(columns={c: f"E_{c}" for c in df_real.columns if c not in ["X_UTM", "Y_UTM", "anio"]})
df_fija = df_fija.rename(columns={c: f"Z_{c}" for c in df_fija.columns if c not in ["X_UTM", "Y_UTM", "anio"]})

df_fis = df_pub.merge(df_real, on=["X_UTM", "Y_UTM", "anio"], how="inner").merge(df_fija, on=["X_UTM", "Y_UTM", "anio"], how="inner")

for pref in ["E", "Z"]:
    for vent in ["30d_prev", "15d_prev", "30d_post"]:
        col_dest = f"{pref}_turno_{vent}"
        df_fis[col_dest] = np.nan
        for t_lbl in HORAS_TURNO:
            m = df_fis["turno"] == t_lbl
            df_fis.loc[m, col_dest] = df_fis.loc[m, f"{pref}_{t_lbl}_{vent}"]

# Descriptivas de la exposición física por turno (30d previos)
sub_todas = df_fis
sub_vuln  = df_fis[df_fis["alta_marg"] == 1]
sub_novul = df_fis[df_fis["alta_marg"] == 0]

def within_sd(d, col):
    w = d[col] - d.groupby("id_cct_clean")[col].transform("mean") - d.groupby("anio")[col].transform("mean")
    return w.std()

print("=== DESCRIPTIVAS EXPOSICIÓN FÍSICA HORARIA AERMOD (30 DÍAS PREVIOS, ug/m3) ===")
for lbl, d in [("Todas públicas", sub_todas), ("Alta Marg.", sub_vuln), ("Baja/Media", sub_novul)]:
    s = d["E_turno_30d_prev"]
    q1, q5 = s.quantile(0.10), s.quantile(0.90)
    print(f"  {lbl:15s} | Media={s.mean():.4f} | DE_tot={s.std():.4f} | DE_within={within_sd(d, 'E_turno_30d_prev'):.4f} | P10={q1:.4f} | P90={q5:.4f} | N={len(d):,}")
print(f"  Corr(E_turno_30d_prev, E_turno_30d_post) = {df_fis['E_turno_30d_prev'].corr(df_fis['E_turno_30d_post']):.3f}")

def run_iv_row(lbl, d, y, e_col, z_col, fe_t="anio", vcov_s=VC):
    fs = pf.feols(f"{e_col} ~ {z_col} + {controles_W} | id_cct_clean + {fe_t}", data=d, vcov=vcov_s, collin_tol=1e-12)
    rf = pf.feols(f"{y} ~ {z_col} + {controles_W} | id_cct_clean + {fe_t}", data=d, vcov=vcov_s)
    iv = pf.feols(f"{y} ~ {controles_W} + [{e_col} ~ {z_col}] | id_cct_clean + {fe_t}", data=d, vcov=vcov_s, collin_tol=1e-12)
    f1 = fs.tstat()[z_col] ** 2
    br, ser, pr = rf.coef()[z_col], rf.se()[z_col], rf.pvalue()[z_col]
    bi, sei, pi = iv.coef()[e_col], iv.se()[e_col], iv.pvalue()[e_col]
    print(f"  {lbl:42s} | F1={f1:6.1f} | RF={br:8.3f}{get_stars(pr):3s} ({ser:6.3f}, p={pr:.4f}) | 2SLS={bi:9.2f}{get_stars(pi):3s} ({sei:6.2f}, p={pi:.4f}) | N={iv._N:,}")

print("\n=== TABLA 3.4 DEFINITIVA — PANEL A: LENGUAJE (AERMOD FÍSICO TURNO ~ VIENTO EXÓGENO IV) ===")
run_iv_row("(1) Todas públicas | 30d Turno ~ IV_30D",       sub_todas, "lyc_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     VC)
run_iv_row("(2) Alta Marg.     | 30d Turno ~ IV_30D",       sub_vuln,  "lyc_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     VC)
run_iv_row("(2b)Alta Marg.     | Cluster municipio",        sub_vuln,  "lyc_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     {"CRV1": "municipio"})
run_iv_row("(3) Alta Marg.     | EF Mun x Año",             sub_vuln,  "lyc_std_500", "E_turno_30d_prev", "IV_30D",    "mun_anio", VC)
run_iv_row("(4) Baja/Media     | 30d Turno ~ IV_30D",       sub_novul, "lyc_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     VC)
run_iv_row("(4b)Baja/Media     | EF Mun x Año",             sub_novul, "lyc_std_500", "E_turno_30d_prev", "IV_30D",    "mun_anio", VC)
run_iv_row("(5) Alta Marg.     | 15d Turno ~ IV_15D",       sub_vuln,  "lyc_std_500", "E_turno_15d_prev", "IV_15D",    "anio",     VC)
run_iv_row("(6) PLACEBO Todas  | 30d Post ~ IV_POST30",     sub_todas, "lyc_std_500", "E_turno_30d_post", "IV_POST30", "anio",     VC)
run_iv_row("(7) PLACEBO Vuln.  | 30d Post ~ IV_POST30",     sub_vuln,  "lyc_std_500", "E_turno_30d_post", "IV_POST30", "anio",     VC)
run_iv_row("(8) MECANISMO 24h  | Todas 24h ~ IV_30D",       sub_todas, "lyc_std_500", "E_24h_30d_prev",   "IV_30D",    "anio",     VC)
run_iv_row("(9) MECANISMO 24h  | Vuln. 24h ~ IV_30D",       sub_vuln,  "lyc_std_500", "E_24h_30d_prev",   "IV_30D",    "anio",     VC)

print("\n=== TABLA 3.4 DEFINITIVA — PANEL B: MATEMÁTICAS (AERMOD FÍSICO TURNO ~ VIENTO EXÓGENO IV) ===")
run_iv_row("(1) Todas públicas | 30d Turno ~ IV_30D",       sub_todas, "mat_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     VC)
run_iv_row("(2) Alta Marg.     | 30d Turno ~ IV_30D",       sub_vuln,  "mat_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     VC)
run_iv_row("(3) Alta Marg.     | EF Mun x Año",             sub_vuln,  "mat_std_500", "E_turno_30d_prev", "IV_30D",    "mun_anio", VC)
run_iv_row("(4) Baja/Media     | 30d Turno ~ IV_30D",       sub_novul, "mat_std_500", "E_turno_30d_prev", "IV_30D",    "anio",     VC)
run_iv_row("(7) PLACEBO Vuln.  | 30d Post ~ IV_POST30",     sub_vuln,  "mat_std_500", "E_turno_30d_post", "IV_POST30", "anio",     VC)

print("\n=== PRUEBAS DE MECANISMO Y PLACEBO FÍSICO CON EMISIONES CONGELADAS 2015 EN AERMOD (Z_fija) ===")
run_iv_row("Todas | 30d Turno ~ Z_turno_30d (LyC)",         sub_todas, "lyc_std_500", "E_turno_30d_prev", "Z_turno_30d_prev", "anio", VC)
run_iv_row("Todas | 30d 24h   ~ Z_24h_30d   (LyC)",         sub_todas, "lyc_std_500", "E_24h_30d_prev",   "Z_24h_30d_prev",   "anio", VC)
run_iv_row("Todas | 30d Post  ~ Z_post_30d  (LyC)",         sub_todas, "lyc_std_500", "E_turno_30d_post", "Z_turno_30d_post", "anio", VC)
run_iv_row("Vuln. | 30d Post  ~ Z_post_30d  (LyC)",         sub_vuln,  "lyc_std_500", "E_turno_30d_post", "Z_turno_30d_post", "anio", VC)

print("\n=== TABLA 3.3 (PANEL B EXTRA): TWFE FÍSICO 30D Y 15D EN HORARIO DE TURNO (ug/m3) ===")
for lbl, col_e in [("TWFE físico 30d turno", "E_turno_30d_prev"), ("TWFE físico 15d turno", "E_turno_15d_prev")]:
    df_fis["tmp_x_m"] = df_fis[col_e] * df_fis["alta_marg"]
    ml = pf.feols(f"lyc_std_500 ~ {col_e} + tmp_x_m + {controles_W} | {FE}", data=df_fis, vcov=VC)
    mm = pf.feols(f"mat_std_500 ~ {col_e} + tmp_x_m + {controles_W} | {FE}", data=df_fis, vcov=VC)
    print(f"  {lbl:24s} | LyC int={ml.coef()['tmp_x_m']:8.2f}{get_stars(ml.pvalue()['tmp_x_m']):3s} ({ml.se()['tmp_x_m']:6.2f}, p={ml.pvalue()['tmp_x_m']:.4f}) | Mat int={mm.coef()['tmp_x_m']:8.2f} ({mm.se()['tmp_x_m']:6.2f}, p={mm.pvalue()['tmp_x_m']:.4f})")
'''),
]

nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {"display_name": "Python (thesis-cdmx)", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

ns = {}
full_log = []
exec_count = 0

for ctype, src in CELLS:
    lines = [line + "\n" for line in src.splitlines()]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    if ctype == "markdown":
        nb["cells"].append({"cell_type": "markdown", "metadata": {}, "source": lines})
    else:
        exec_count += 1
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(src, f"<cell-{exec_count}>", "exec"), ns)
        out_txt = buf.getvalue()
        full_log.append(f"\n{'='*80}\n[CELDA {exec_count}]\n{'='*80}\n{out_txt}")
        out_lines = [l + "\n" for l in out_txt.splitlines()]
        outputs = [{"name": "stdout", "output_type": "stream", "text": out_lines}] if out_txt else []
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": exec_count,
            "metadata": {},
            "outputs": outputs,
            "source": lines,
        })

with open("04_master_tablas_cap3.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

report = "".join(full_log)
with open("resumen_master_cap3.txt", "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print("\n[GUARDADO] 04_master_tablas_cap3.ipynb y resumen_master_cap3.txt listos.")
