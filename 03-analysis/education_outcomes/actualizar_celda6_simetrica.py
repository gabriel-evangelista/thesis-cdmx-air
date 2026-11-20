import json, io, contextlib

NUEVA_CELDA_6 = r'''# === CELDA 6: MATRIZ SIMÉTRICA 2x2 (TWFE FÍSICO vs 2SLS FÍSICO POSTFILE) Y TABLA 3.4 ===
import numpy as np
import pandas as pd
import pyfixest as pf

# 1. Recuperar diagnóstico del IV Anual (justifica por qué el Pilar 2 migra a 30 días)
rec_unicos = df_reg[["RECID", "X_UTM", "Y_UTM"]].drop_duplicates().reset_index(drop=True)
dx_km = (rec_unicos["X_UTM"].values[:, None] - Xs[None, :]) / 1000.0
dy_km = (rec_unicos["Y_UTM"].values[:, None] - Ys[None, :]) / 1000.0
dist_km = np.maximum(np.sqrt(dx_km**2 + dy_km**2), 0.25)
ux, uy = dx_km / dist_km, dy_km / dist_km
peso_f = Q_2015[None, :] / (dist_km ** 1.5)

iv_anual_list = []
for yr in [2015, 2017, 2019]:
    wd_l, ws_l = [], []
    with open(f"{AERMET_OUT}/aer_{yr}.sfc", "r") as f:
        for line in f.readlines()[1:]:
            p = line.split()
            if len(p) >= 22 and 0 < float(p[15]) < 50 and 0 <= float(p[16]) <= 360:
                ws_l.append(float(p[15])); wd_l.append(float(p[16]))
    ws_a, wd_r = np.array(ws_l), np.deg2rad(np.array(wd_l))
    wx_u, wy_u, inv_u = -np.sin(wd_r), -np.cos(wd_r), 1.0 / np.maximum(ws_a, 0.5)
    sec_a = np.floor(np.array(wd_l) / 10.0).astype(int) % 36
    acc = np.zeros(len(rec_unicos))
    for s in range(36):
        m = (sec_a == s)
        if np.any(m):
            wx_m, wy_m = np.mean(wx_u[m]), np.mean(wy_u[m])
            nm = max(np.sqrt(wx_m**2 + wy_m**2), 1e-6)
            acc += np.sum(np.maximum(0.0, ux*(wx_m/nm) + uy*(wy_m/nm))**8 * peso_f, axis=1) * (np.sum(inv_u[m])/len(ws_a))
    iv_anual_list.append(pd.DataFrame({"RECID": rec_unicos["RECID"], "anio": yr, "IV_ANUAL_RAW": acc}))

df_iva = pd.concat(iv_anual_list, ignore_index=True)
df_iva["IV_ANUAL"] = (df_iva["IV_ANUAL_RAW"] - df_iva["IV_ANUAL_RAW"].mean()) / df_iva["IV_ANUAL_RAW"].std()
w_sd_anual = (df_iva["IV_ANUAL"] - df_iva.groupby("RECID")["IV_ANUAL"].transform("mean") - df_iva.groupby("anio")["IV_ANUAL"].transform("mean")).std()

df_pub_a = df_pub.merge(df_iva[["RECID", "anio", "IV_ANUAL"]], on=["RECID", "anio"], how="left")
fs_an = pf.feols(f"PM25_ALL ~ IV_ANUAL + {controles_W} | {FE}", data=df_pub_a, vcov=VC, collin_tol=1e-12)
iv_an = pf.feols(f"lyc_std_500 ~ {controles_W} + [PM25_ALL ~ IV_ANUAL] | {FE}", data=df_pub_a, vcov=VC, collin_tol=1e-12)

print("=== DIAGNÓSTICO DE MOTIVACIÓN PARA EL PILAR 2 (IV ANUAL vs 30 DÍAS) ===")
print(f"  IV Anual (8,760h): DE_within = {w_sd_anual:.5f} | F1 = {fs_an.tstat()['IV_ANUAL']**2:.2f} | 2SLS_LyC = {iv_an.coef()['PM25_ALL']:.2f} (SE = {iv_an.se()['PM25_ALL']:.2f})")

# 2. Procesar salidas físicas horarias POSTFILE (ug/m3)
FECHAS_TS = {2015: pd.Timestamp("2015-06-17"), 2017: pd.Timestamp("2017-06-14"), 2019: pd.Timestamp("2019-06-11")}
HORAS_TURNO = {
    "MATUTINO": set(range(8, 15)), "VESPERTINO": set(range(14, 21)),
    "TIEMPO COMPLETO": set(range(9, 17)), "NOCTURNO": set(range(18, 23)), "DISCONTINUO": set(range(8, 20)),
}

def procesar_postfile(filepath, anio):
    df = pd.read_csv(filepath, sep=r"\s+", skiprows=8, usecols=[0, 1, 2, 8], names=["X_UTM", "Y_UTM", "CONC", "DATE"],
                     dtype={"X_UTM": np.float64, "Y_UTM": np.float64, "CONC": np.float32, "DATE": np.int64})
    df["X_UTM"], df["Y_UTM"] = df["X_UTM"].round(2), df["Y_UTM"].round(2)
    df = df[df["X_UTM"] >= 460000].copy()
    hr, ymd = (df["DATE"] % 100).astype(np.int8), df["DATE"] // 100
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

df_real = pd.concat([procesar_postfile(f"{POST_DIR}/post_real_{yr}.plt", yr) for yr in [2015, 2017, 2019]], ignore_index=True)
df_real = df_real.rename(columns={c: f"E_{c}" for c in df_real.columns if c not in ["X_UTM", "Y_UTM", "anio"]})
df_fis = df_pub.merge(df_real, on=["X_UTM", "Y_UTM", "anio"], how="inner")

for vent in ["30d_prev", "15d_prev", "30d_post"]:
    col_dest = f"E_turno_{vent}"
    df_fis[col_dest] = np.nan
    for t_lbl in HORAS_TURNO:
        m = df_fis["turno"] == t_lbl
        df_fis.loc[m, col_dest] = df_fis.loc[m, f"E_{t_lbl}_{vent}"]

sub_todas = df_fis
sub_vuln  = df_fis[df_fis["alta_marg"] == 1]
sub_novul = df_fis[df_fis["alta_marg"] == 0]

# 3. TABLA 3.4 SIMÉTRICA: TWFE FÍSICO vs FORMA REDUCIDA vs 2SLS SOBRE LOS MISMOS DATOS
columnas_34 = [
    ("(1) Todas públicas",        sub_todas, "E_turno_30d_prev", "IV_30D",    "anio"),
    ("(2) Alta Marg.",            sub_vuln,  "E_turno_30d_prev", "IV_30D",    "anio"),
    ("(3) Alta Marg. (Mun*Año)",  sub_vuln,  "E_turno_30d_prev", "IV_30D",    "mun_anio"),
    ("(4) Baja/Media Marg.",      sub_novul, "E_turno_30d_prev", "IV_30D",    "anio"),
    ("(5) Alta Marg. (15d)",      sub_vuln,  "E_turno_15d_prev", "IV_15D",    "anio"),
    ("(6) Placebo Post (30d)",    sub_vuln,  "E_turno_30d_post", "IV_POST30", "anio"),
]

print("\n=== TABLA 3.4 SIMÉTRICA: COMPARACIÓN DIRECTA TWFE FÍSICO vs FORMA REDUCIDA vs 2SLS (ug/m3) ===")
for panel_lbl, y_var in [("PANEL A: LENGUAJE Y COMUNICACIÓN", "lyc_std_500"), ("PANEL B: MATEMÁTICAS", "mat_std_500")]:
    print(f"\n{panel_lbl}")
    for col_lbl, d, e_c, z_c, fe_t in columnas_34:
        tw = pf.feols(f"{y_var} ~ {e_c} + {controles_W} | id_cct_clean + {fe_t}", data=d, vcov=VC)
        rf = pf.feols(f"{y_var} ~ {z_c} + {controles_W} | id_cct_clean + {fe_t}", data=d, vcov=VC)
        iv = pf.feols(f"{y_var} ~ {controles_W} + [{e_c} ~ {z_c}] | id_cct_clean + {fe_t}", data=d, vcov=VC, collin_tol=1e-12)
        fs = pf.feols(f"{e_c} ~ {z_c} + {controles_W} | id_cct_clean + {fe_t}", data=d, vcov=VC, collin_tol=1e-12)
        f1 = fs.tstat()[z_c] ** 2
        bt, set_, pt = tw.coef()[e_c], tw.se()[e_c], tw.pvalue()[e_c]
        br, ser, pr  = rf.coef()[z_c], rf.se()[z_c], rf.pvalue()[z_c]
        bi, sei, pi  = iv.coef()[e_c], iv.se()[e_c], iv.pvalue()[e_c]
        print(f"  {col_lbl:25s} | TWFE={bt:7.2f}{get_stars(pt):3s} ({set_:6.2f}, p={pt:.3f}) | RF={br:7.3f}{get_stars(pr):3s} ({ser:5.3f}, p={pr:.3f}) | 2SLS={bi:8.2f}{get_stars(pi):3s} ({sei:6.2f}, p={pi:.3f}) | F1={f1:5.1f} | N={iv._N:,}")
'''

with open("04_master_tablas_cap3.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

lines = [l + "\n" for l in NUEVA_CELDA_6.splitlines()]
lines[-1] = lines[-1].rstrip("\n")
nb["cells"][-1]["source"] = lines

# Ejecutar todo el notebook limpio en memoria para guardar outputs actualizados
ns = {}
full_out = []
for idx, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile("".join(cell["source"]), f"<cell-{idx}>", "exec"), ns)
        txt = buf.getvalue()
        cell["outputs"] = [{"name": "stdout", "output_type": "stream", "text": [l + "\n" for l in txt.splitlines()]}]
        if idx == len(nb["cells"]) - 1:
            full_out.append(txt)

with open("04_master_tablas_cap3.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("".join(full_out))
