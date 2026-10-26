"""
Script reproducible (Commit 1 AERMOD):
1. Filtra las 285 fuentes activas de CO2 desde fuentes_elevadas.sou (sin re-correr AERMAP).
2. Clasifica cada fuente en su rama tecnológica AP-42.
3. Asigna ratios controlados (kg PM / t CO2) y parámetros termodinámicos de chimenea (hs, Ts, vs, ds).
4. Calcula tasas de emisión Q (g/s) para 2015-2019 y exporta catálogo CSV + archivos .so para AERMOD.
"""
import csv, glob, os

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
CSV_IN = glob.glob(f"{BASE}/02-data/processed/retc_15_19_pm_est_complete_clean*")[0]
SOU_IN = f"{BASE}/02-data/processed/aermap_out/fuentes_elevadas.sou"
OUT_DIR = f"{BASE}/02-data/processed/aermap_out"

TECH_PARAMS = {
    "TURBINA_GAS":     {"ratio_kg_t": 0.0600, "hs": 30.0, "ts": 750.0, "vs": 28.0, "ds": 3.20},
    "MOTOR_RICE":      {"ratio_kg_t": 0.1300, "hs": 12.0, "ts": 673.0, "vs": 22.0, "ds": 0.45},
    "HORNO_VIDRIO":    {"ratio_kg_t": 0.4500, "hs": 45.0, "ts": 550.0, "vs": 15.0, "ds": 1.80},
    "FUNDICION_METAL": {"ratio_kg_t": 0.6500, "hs": 22.0, "ts": 370.0, "vs": 12.0, "ds": 1.10},
    "SECADO_QUIM":     {"ratio_kg_t": 0.2500, "hs": 25.0, "ts": 365.0, "vs": 11.0, "ds": 1.20},
    "CALDERA_IND":     {"ratio_kg_t": 0.0633, "hs": 15.0, "ts": 450.0, "vs": 10.0, "ds": 0.80},
}

NRA_EXPLICIT = {
    "TCOQT1510411": "TURBINA_GAS",
    "TPN0901600351": "TURBINA_GAS",
    "FERAD0900711": "MOTOR_RICE",
    "SMB0901600592": "MOTOR_RICE",
    "LVI6Z1505711": "HORNO_VIDRIO",
    "NFN6Z1510911": "HORNO_VIDRIO",
    "VVI1510400289": "HORNO_VIDRIO",
    "CUPND1510411": "FUNDICION_METAL",
    "ICA7P0901111": "FUNDICION_METAL",
    "LAI1503300246": "FUNDICION_METAL",
    "NCO7N0900221": "FUNDICION_METAL",
    "TME7Q1510411": "FUNDICION_METAL",
    "PAG0900200342": "SECADO_QUIM",
}

def classify_plant(row):
    nra = row["NRA"].strip()
    nombre = row["NOMBRE"].upper()
    scian = str(row["SCIAN"]).strip()
    sector = row["SECTOR"].upper()

    if nra in NRA_EXPLICIT:
        return NRA_EXPLICIT[nra]
    if nra.startswith("CFE") or nra.startswith("CGI") or "COMISION FEDERAL DE ELECTRICIDAD" in nombre or "TERMOELECTRICA" in nombre:
        return "TURBINA_GAS"
    if scian in ["221110", "486210"] or "ENERGIA ELECTRICA" in sector:
        return "MOTOR_RICE" if ("MOTOR" in nombre or "FERMICAISE" in nombre) else "TURBINA_GAS"
    if scian.startswith("3272") or "VIDRIO" in sector or "CEMENTO Y CAL" in sector:
        return "FUNDICION_METAL" if scian.startswith("331") else "HORNO_VIDRIO"
    if scian.startswith("331") or "METALURGICA" in sector:
        return "FUNDICION_METAL"
    if scian in ["325610", "325510", "325910"] or "PINTURAS" in sector:
        return "SECADO_QUIM"
    return "CALDERA_IND"

def main():
    sou_by_coord = {}
    with open(SOU_IN, "r") as f:
        for line in f:
            p = line.split()
            if len(p) >= 6 and p[0] == "SO" and p[1] == "LOCATION":
                sou_by_coord[(round(float(p[4]), 2), round(float(p[5]), 2))] = (p[2], float(p[6]))

    with open(CSV_IN, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    years = [2015, 2016, 2017, 2018, 2019]
    sec_per_year = {yr: (366 if yr == 2016 else 365) * 86400.0 for yr in years}

    catalog_out = []
    filtered_sou_lines = []
    tech_counts = {}
    used_srcids = set()

    for r in rows:
        x, y = round(float(r["COORDENADA_UTM_X"]), 2), round(float(r["COORDENADA_UTM_Y"]), 2)
        sid, z_elev = sou_by_coord[(x, y)]

        base_sid = sid
        cnt = 2
        while sid in used_srcids:
            sid = f"{base_sid[:10]}_{cnt}"
            cnt += 1
        used_srcids.add(sid)

        tech = classify_plant(r)
        tech_counts[tech] = tech_counts.get(tech, 0) + 1
        params = TECH_PARAMS[tech]

        filtered_sou_lines.append(f"SO LOCATION  {sid:<12s}  POINT  {x:12.2f}  {y:12.2f}  {z_elev:10.2f}\n")

        out_row = {
            "SRCID": sid, "NRA_ORIG": r["NRA"].strip(), "NOMBRE": r["NOMBRE"].strip(),
            "MUNICIPIO": r["MUNICIPIO"].strip(), "SCIAN": r["SCIAN"].strip(),
            "SECTOR": r["SECTOR"].strip(), "TECH_GROUP": tech,
            "RATIO_KG_PM_PER_T_CO2": params["ratio_kg_t"],
            "X_UTM": x, "Y_UTM": y, "Z_ELEV": z_elev,
            "HS_M": params["hs"], "TS_K": params["ts"], "VS_MS": params["vs"], "DS_M": params["ds"]
        }

        for yr in years:
            co2_kg = float(r[f"PM_{yr}"]) if r[f"PM_{yr}"] else 0.0
            co2_tons = co2_kg / 1000.0
            pm_kg_yr = co2_tons * params["ratio_kg_t"]
            q_gs = (pm_kg_yr * 1000.0) / sec_per_year[yr]
            out_row[f"CO2_TON_{yr}"] = round(co2_tons, 3)
            out_row[f"PM_KG_{yr}"] = round(pm_kg_yr, 3)
            out_row[f"Q_GS_{yr}"] = round(q_gs, 6)

        catalog_out.append(out_row)

    sou_285_path = f"{OUT_DIR}/fuentes_285_filtradas.sou"
    with open(sou_285_path, "w", encoding="utf-8") as f:
        f.write("** 285 Fuentes Fijas Activas RETC (ZMVM) con Z_ELEV de AERMAP SRTM 30m\n")
        f.write("SO ELEVUNIT METERS\n")
        f.writelines(filtered_sou_lines)

    cat_csv_path = f"{OUT_DIR}/catalogo_285_fuentes_aermod_ap42.csv"
    with open(cat_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(catalog_out[0].keys()))
        writer.writeheader()
        writer.writerows(catalog_out)

    for yr in years:
        so_yr_path = f"{OUT_DIR}/sources_{yr}.so"
        with open(so_yr_path, "w", encoding="utf-8") as f:
            f.write(f"** Bloque SO AERMOD - Anio {yr} (285 Fuentes RETC parametrizadas con AP-42)\n")
            f.write("   ELEVUNIT METERS\n")
            for row in catalog_out:
                f.write(f"   LOCATION  {row['SRCID']:<12s}  POINT  {row['X_UTM']:12.2f}  {row['Y_UTM']:12.2f}  {row['Z_ELEV']:10.2f}\n")
            f.write("\n** Parametros fisicos y tasa de emision Q (g/s): SRCPARAM SRCID Q_gs Hs Ts Vs Ds\n")
            for row in catalog_out:
                f.write(f"   SRCPARAM  {row['SRCID']:<12s}  {row[f'Q_GS_{yr}']:12.6f}  {row['HS_M']:6.2f}  {row['TS_K']:6.2f}  {row['VS_MS']:6.2f}  {row['DS_M']:6.2f}\n")
            f.write("\n** Grupos de fuentes por tecnologia y total\n")
            for tech in TECH_PARAMS.keys():
                sids = [r["SRCID"] for r in catalog_out if r["TECH_GROUP"] == tech]
                for i in range(0, len(sids), 8):
                    chunk = " ".join(f"{s:<12s}" for s in sids[i:i+8])
                    f.write(f"   SRCGROUP  {tech[:8]:<8s}  {chunk}\n")
            f.write("   SRCGROUP  ALL\n")

    print("=== RESUMEN DE PARAMETRIZACION AP-42 (285 FUENTES) ===")
    for t, c in sorted(tech_counts.items(), key=lambda x: -x[1]):
        p = TECH_PARAMS[t]
        print(f"  {t:<16s}: {c:3d} plantas | Ratio={p['ratio_kg_t']:.4f} kg/t | Hs={p['hs']}m, Ts={p['ts']}K, Vs={p['vs']}m/s, Ds={p['ds']}m")
    print(f"\n[OK] Catalogo guardado en: {cat_csv_path}")
    print(f"[OK] Archivos anuales .so (2015-2019) generados en: {OUT_DIR}/sources_YYYY.so")

if __name__ == "__main__":
    main()
