#!/usr/bin/env python3
"""
Deduplicates RETC emitting sources across the 2015-2019 span where facilities
changed their legal name or NRA (e.g., CFE -> LFC -> CGI, PROCTER & GAMBLE,
BIO PAPPEL, etc.) while remaining the same physical facility.

Outputs:
1. 02-data/processed/retc_15_19_nra_mapping.csv
   Audit & mapping table of all merged NRAs -> canonical NRA (most recent record).
2. 02-data/processed/retc_15_19_est_complete_clean.csv (and updates retc_15_19_est_complete.csv,
   retc_15_19_est.csv, retc_15_19_est_min.csv)
3. Consolidated multi-year PM emissions tables where split histories across old/new NRAs
   are combined into a single row per facility:
   - retc_15_19_pm.csv (and _clean.csv)
   - retc_15_19_pm_est_complete.csv (and _clean.csv)
   - retc_15_19_pm_est_top10.csv (and _clean.csv)
   - retc_15_19_pm_est_spur.csv (and _clean.csv)
"""

import csv
import math
import os
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

BASE_DIR = Path("/Users/gabrielevangelista/thesis-cdmx-air")
RAW_DIR = BASE_DIR / "02-data" / "raw"
PROC_DIR = BASE_DIR / "02-data" / "processed"

STOPWORDS = {
    "MEXICO", "MEXICANA", "MEXICANO", "PLANTA", "UNIDAD", "INDUSTRIAL", "GRUPO",
    "PRODUCTOS", "MANUFACTURERA", "MANUFACTURAS", "MANUFACTURING", "MANUFACTURA",
    "LABORATORIOS", "LABORATORIO", "COMPANIA", "INDUSTRIAS", "INDUSTRIA",
    "CORPORACION", "COMERCIAL", "COMERCIALIZADORA", "SERVICIOS", "SISTEMAS",
    "QUIMICA", "QUIMICOS", "AUTOMOTRIZ", "NACIONAL", "CENTRO", "INTERNACIONAL",
    "DISTRIBUIDORA", "DISTRIBUCION", "GENERAL", "FABRICA", "CDMX", "TOLUCA",
    "IZCALLI", "TLALNEPANTLA", "ECATEPEC", "NAUCALPAN", "VALLEJO", "APAXCO",
    "CUAUTITLAN", "LERMA", "UNIVERSIDAD", "NORTE", "SUR", "ORIENTE", "PONIENTE",
    "AND", "DEL", "LAS", "LOS", "PARA", "POR", "CON", "SIN", "THE",
    "SAN", "SANTA", "MARTIN", "OBISPO", "JUAN", "PABLO", "CRUZ", "CLARA",
    "RESINAS", "PINTURAS", "BARNICES", "PLASTICOS", "METALES", "METALICA",
    "ALUMINIO", "ENVASES", "ENVASE", "CARTON", "PAPEL", "EMPAQUES", "HULE",
    "HULERA", "AUTOPARTES", "HOSPITAL", "INSTITUTO"
}


def norm_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").upper()
    s = re.sub(r"\b(S\.?A\.?B?\.?|DE|C\.?V\.?|S\.?|R\.?L\.?|S\.?A\.?P\.?I\.?|I\.?A\.?P\.?)\b", " ", s)
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return " ".join(s.split())


def norm_street(s: str) -> str:
    if not s:
        return ""
    s = norm_text(s)
    s = re.sub(
        r"\b(CALLE|AVENIDA|AV|BLVD|BOULEVARD|CARRETERA|CARR|AUTOPISTA|CALZADA|CALZ|"
        r"PROLONGACION|PROL|RETORNO|CIRCUITO|COLONIA|COL|FRACCIONAMIENTO|FRACC|"
        r"INDUSTRIAL|IND|PARQUE|PUEBLO|EJIDO|CONJUNTO|HABITACIONAL|UNIDAD|NUMERO|"
        r"NUM|NO|SN|SIN|N)\b",
        " ",
        s,
    )
    return " ".join(s.split())


def load_raw_metadata():
    """Loads active years and latest establishment record for each NRA from raw 2015-2019 files."""
    years_by_nra = {}
    latest_by_nra = {}
    for year in range(2015, 2020):
        path = RAW_DIR / f"retc_{year}_est.csv"
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = [" ".join(h.split()) for h in next(reader)]
            for row in reader:
                d = dict(zip(header, row))
                nra = d["NRA"].strip()
                years_by_nra.setdefault(nra, []).append(year)
                latest_by_nra[nra] = d
    return years_by_nra, latest_by_nra


def score_pair(r1: dict, r2: dict):
    """
    Evaluates whether two establishment records with different NRAs represent
    the same physical facility across different reporting years.
    Returns (distance_m, reason_str) if they match, or None otherwise.
    """
    # Facilities that reported simultaneously in the same year under different NRAs
    # are distinct active registries (or separate plants/lines), not a sequential rename.
    if set(r1["years"]) & set(r2["years"]):
        return None

    # Do not merge explicitly distinct plant numbers (e.g. PLANTA I vs PLANTA II)
    n1, n2 = r1["norm_name"] + " ", r2["norm_name"] + " "
    if ("PLANTA I " in n1 and "PLANTA II " in n2) or ("PLANTA II " in n1 and "PLANTA I " in n2):
        return None
    if ("PLANTA 1 " in n1 and "PLANTA 2 " in n2) or ("PLANTA 2 " in n1 and "PLANTA 1 " in n2):
        return None

    dist = math.hypot(r1["x"] - r2["x"], r1["y"] - r2["y"])
    if dist > 3800:
        return None

    st_sim = SequenceMatcher(None, r1["street"], r2["street"]).ratio()
    ext_match = (r1["ext"] == r2["ext"]) and (r1["ext"] != "")
    ext_conflict = (r1["ext"] != "") and (r2["ext"] != "") and (r1["ext"] != r2["ext"]) and (dist > 35)

    # 1. CFE Power Plants (CFE -> LFC -> CGI reorganization)
    if r1["is_cfe"] and r2["is_cfe"]:
        if dist < 3500 and (st_sim > 0.50 or dist < 100):
            return (dist, f"CFE_REORG (dist={dist:.1f}m, street_sim={st_sim:.2f})")
        return None

    nsim = max(
        SequenceMatcher(None, r1["norm_name"], r2["norm_name"]).ratio(),
        SequenceMatcher(None, r1["norm_name_latest"], r2["norm_name_latest"]).ratio(),
    )
    asim = SequenceMatcher(None, r1["norm_act"], r2["norm_act"]).ratio()
    ctok = r1["tokens"] & r2["tokens"]
    same_scian = r1["SCIAN"] == r2["SCIAN"]
    same_scian3 = r1["SCIAN"][:3] == r2["SCIAN"][:3]
    same_ca = r1["CLAVE AMBIENTAL"] == r2["CLAVE AMBIENTAL"]
    same_sector = r1["SECTOR"] == r2["SECTOR"]

    # 2. Exact or near-exact coordinates (< 50m)
    if dist < 50:
        if (same_scian3 or same_ca or same_sector) and (
            nsim > 0.55 or asim > 0.65 or ctok or (st_sim > 0.80 and ext_match)
        ):
            return (dist, f"NEAR_EXACT_COORD (dist={dist:.1f}m, name_sim={nsim:.2f}, act_sim={asim:.2f})")

    # 3. Close coordinates (< 500m)
    if dist < 500:
        if ctok and (same_scian3 or same_ca or same_sector) and (nsim > 0.50 or asim > 0.45 or st_sim > 0.75):
            return (dist, f"CLOSE_BRAND_MATCH (dist={dist:.1f}m, tokens={sorted(ctok)}, name_sim={nsim:.2f})")
        if (
            not ext_conflict
            and st_sim > 0.80
            and (ext_match or (r1["street"] == r2["street"] and len(r1["street"]) > 8))
            and (same_scian3 or same_ca or same_sector)
            and asim > 0.70
        ):
            return (dist, f"CLOSE_ADDR_ACT_MATCH (dist={dist:.1f}m, street_sim={st_sim:.2f}, act_sim={asim:.2f})")

    # 4. Shifted GPS coordinates (500m - 3700m) with verified address/brand & activity
    if dist < 3700:
        if ctok and (same_scian3 or same_ca) and ((st_sim > 0.75 and not ext_conflict) or nsim > 0.85):
            return (dist, f"SHIFTED_BRAND_MATCH (dist={dist:.1f}m, tokens={sorted(ctok)}, street_sim={st_sim:.2f})")
        if st_sim > 0.90 and ext_match and (same_scian or same_ca) and asim > 0.95:
            return (dist, f"SHIFTED_EXACT_ADDR_ACT (dist={dist:.1f}m, addr={r1['street']} #{r1['ext']})")
        if st_sim > 0.75 and ext_match and same_scian and asim > 0.95:
            return (dist, f"SHIFTED_ADDR_ACT (dist={dist:.1f}m, addr={r1['street']} #{r1['ext']})")

    return None


def compute_Percentile_linear(vals: list, q: float) -> float:
    """Matches pandas/numpy default linear quantile calculation."""
    s = sorted(vals)
    if not s:
        return 0.0
    pos = (len(s) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    return s[lo] + (pos - lo) * (s[hi] - s[lo])


def main():
    years_by_nra, latest_by_nra = load_raw_metadata()

    # We read from the raw establishment files to ensure idempotency even if
    # retc_15_19_est_complete.csv was already updated by a previous run.
    est_fieldnames = [
        "NRA", "NOMBRE", "SCIAN", "DESCRIPCIÓN SCIAN", "SECTOR",
        "CLAVE AMBIENTAL", "PRINCIPAL ACTIVIDAD PRODUCTIVA", "PARQUE INDUSTRIAL",
        "COORDENADA UTM X", "COORDENADA UTM Y", "LATITUD NORTE", "LONGITUD OESTE"
    ]
    rows_by_nra = {}
    for year in range(2015, 2020):
        path = RAW_DIR / f"retc_{year}_est.csv"
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = [" ".join(h.split()) for h in next(reader)]
            for raw_row in reader:
                d = dict(zip(header, raw_row))
                nra = d["NRA"].strip()
                if nra not in rows_by_nra:
                    rows_by_nra[nra] = {col: d.get(col, "") for col in est_fieldnames}
                    rows_by_nra[nra]["NRA"] = nra
    rows = list(rows_by_nra.values())

    print(f"Loaded {len(rows)} unique NRA rows from raw 2015-2019 establishment files")

    # Enrich rows for matching
    for r in rows:
        nra = r["NRA"].strip()
        d_latest = latest_by_nra.get(nra, r)
        r["x"] = float(r["COORDENADA UTM X"]) if r["COORDENADA UTM X"] else 0.0
        r["y"] = float(r["COORDENADA UTM Y"]) if r["COORDENADA UTM Y"] else 0.0
        names_combined = r["NOMBRE"] + " " + d_latest.get("NOMBRE", "")
        r["norm_name"] = norm_text(r["NOMBRE"])
        r["norm_name_latest"] = norm_text(d_latest.get("NOMBRE", ""))
        r["norm_act"] = norm_text(r["PRINCIPAL ACTIVIDAD PRODUCTIVA"])
        r["years"] = sorted(list(set(years_by_nra.get(nra, []))))
        r["street"] = norm_street(d_latest.get("CALLE", ""))
        r["ext"] = norm_street(d_latest.get("NÚM. EXT", ""))
        r["tokens"] = set(w for w in norm_text(names_combined).split() if len(w) > 2 and w not in STOPWORDS)
        r["is_cfe"] = (r["SCIAN"] == "221110") and any(p in nra for p in ("CFE", "CGI", "LFC"))

    # Build candidate edges and sort by distance
    edges = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            res = score_pair(rows[i], rows[j])
            if res is not None:
                edges.append((res[0], i, j, res[1]))

    edges.sort(key=lambda x: x[0])

    # Agglomerative union-find with strict non-overlapping year constraint
    parent = list(range(len(rows)))
    cluster_years = {i: set(rows[i]["years"]) for i in range(len(rows))}
    cluster_reasons = {i: [] for i in range(len(rows))}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for dist, i, j, reason in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            if not (cluster_years[ri] & cluster_years[rj]):
                parent[rj] = ri
                cluster_years[ri] |= cluster_years[rj]
                cluster_reasons[ri].append((rows[i]["NRA"], rows[j]["NRA"], dist, reason))

    clusters_dict = {}
    for i in range(len(rows)):
        clusters_dict.setdefault(find(i), []).append(i)

    # Map each NRA to its canonical (most recent) NRA and build clean establishment list
    nra_to_canonical = {}
    canonical_record_by_nra = {}
    mapping_rows = []
    clean_est_rows = []

    merged_cluster_count = 0
    for root, member_indices in clusters_dict.items():
        # Sort members chronologically by their latest active year (then earliest year, then NRA)
        member_indices.sort(key=lambda idx: (max(rows[idx]["years"]), min(rows[idx]["years"]), rows[idx]["NRA"]))
        canonical_idx = member_indices[-1]  # Most recent record
        canonical_row = rows[canonical_idx]
        canonical_nra = canonical_row["NRA"].strip()

        # Use the most recent metadata from the raw establishment file for the canonical NRA
        d_latest = latest_by_nra.get(canonical_nra, {})
        clean_row = {}
        for col in est_fieldnames:
            clean_row[col] = d_latest.get(col, canonical_row[col])
        clean_est_rows.append(clean_row)
        canonical_record_by_nra[canonical_nra] = clean_row

        if len(member_indices) > 1:
            merged_cluster_count += 1
            reason_summary = "; ".join(f"{r}" for _, _, _, r in cluster_reasons[root])
            all_nras_in_cluster = [rows[idx]["NRA"].strip() for idx in member_indices]
            for idx in member_indices:
                m_row = rows[idx]
                m_nra = m_row["NRA"].strip()
                nra_to_canonical[m_nra] = canonical_nra
                dist_to_canon = math.hypot(m_row["x"] - canonical_row["x"], m_row["y"] - canonical_row["y"])
                mapping_rows.append({
                    "CLUSTER_ID": merged_cluster_count,
                    "OLD_NRA": m_nra,
                    "CANONICAL_NRA": canonical_nra,
                    "IS_CANONICAL": m_nra == canonical_nra,
                    "ACTIVE_YEARS": "-".join(str(y) for y in m_row["years"]),
                    "OLD_NOMBRE": m_row["NOMBRE"],
                    "CANONICAL_NOMBRE": clean_row["NOMBRE"],
                    "SCIAN": clean_row["SCIAN"],
                    "CLAVE_AMBIENTAL": clean_row["CLAVE AMBIENTAL"],
                    "DIST_TO_CANONICAL_M": f"{dist_to_canon:.1f}",
                    "CLUSTER_NRAS": " -> ".join(all_nras_in_cluster),
                    "MATCH_REASON": reason_summary,
                })
        else:
            nra_to_canonical[canonical_nra] = canonical_nra

    # Sort clean_est_rows by NRA
    clean_est_rows.sort(key=lambda r: r["NRA"])

    # 1. Save NRA mapping table
    mapping_path = PROC_DIR / "retc_15_19_nra_mapping.csv"
    mapping_fields = [
        "CLUSTER_ID", "OLD_NRA", "CANONICAL_NRA", "IS_CANONICAL", "ACTIVE_YEARS",
        "OLD_NOMBRE", "CANONICAL_NOMBRE", "SCIAN", "CLAVE_AMBIENTAL",
        "DIST_TO_CANONICAL_M", "CLUSTER_NRAS", "MATCH_REASON"
    ]
    with open(mapping_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=mapping_fields)
        writer.writeheader()
        writer.writerows(mapping_rows)

    print(f"Identified {merged_cluster_count} facilities with multiple NRAs ({len(mapping_rows)} total NRAs merged into {merged_cluster_count} canonical NRAs).")
    print(f"Saved mapping audit table to: {mapping_path}")

    # 2. Save cleaned establishment files
    for out_path in [PROC_DIR / "retc_15_19_est_complete_clean.csv", PROC_DIR / "retc_15_19_est_complete.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=est_fieldnames)
            writer.writeheader()
            writer.writerows(clean_est_rows)

    est_short_fields = ["NRA", "NOMBRE", "SCIAN", "SECTOR", "PARQUE INDUSTRIAL", "COORDENADA_UTM_X", "COORDENADA_UTM_Y"]
    est_short_rows = [
        {
            "NRA": r["NRA"],
            "NOMBRE": r["NOMBRE"],
            "SCIAN": r["SCIAN"],
            "SECTOR": r["SECTOR"],
            "PARQUE INDUSTRIAL": r["PARQUE INDUSTRIAL"],
            "COORDENADA_UTM_X": r["COORDENADA UTM X"],
            "COORDENADA_UTM_Y": r["COORDENADA UTM Y"],
        }
        for r in clean_est_rows
    ]
    for out_path in [PROC_DIR / "retc_15_19_est_clean.csv", PROC_DIR / "retc_15_19_est.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=est_short_fields)
            writer.writeheader()
            writer.writerows(est_short_rows)

    est_min_fields = ["NRA", "COORDENADA_UTM_X", "COORDENADA_UTM_Y"]
    est_min_rows = [
        {
            "NRA": r["NRA"],
            "COORDENADA_UTM_X": r["COORDENADA UTM X"],
            "COORDENADA_UTM_Y": r["COORDENADA UTM Y"],
        }
        for r in clean_est_rows
    ]
    for out_path in [PROC_DIR / "retc_15_19_est_min_clean.csv", PROC_DIR / "retc_15_19_est_min.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=est_min_fields)
            writer.writeheader()
            writer.writerows(est_min_rows)

    print(f"Updated establishment tables: {len(rows)} -> {len(clean_est_rows)} unique sources.")

    # 3. Consolidate multi-year PM emissions tables (reconstructed from raw air files for idempotency)
    FILTRO_SIMAT_MASTER = {
        "Alvaro Obregon", "Azcapotzalco", "Benito Juarez", "Coyoacan",
        "Cuajimalpa de Morelos", "Cuauhtemoc", "Gustavo A. Madero", "Iztacalco",
        "Iztapalapa", "Magdalena Contreras", "Miguel Hidalgo", "Milpa Alta",
        "Tlahuac", "Tlalpan", "Venustiano Carranza", "Xochimilco",
        "Acolman", "Atenco", "Atizapan de Zaragoza", "Chalco", "Chiautla",
        "Chicoloapan", "Chiconcuac", "Chimalhuacan", "Coacalco de Berriozabal",
        "Coyotepec", "Cuautitlan", "Cuautitlan Izcalli", "Ecatepec de Morelos",
        "Huehuetoca", "Ixtapaluca", "Jaltenco", "La Paz", "Melchor Ocampo",
        "Naucalpan de Juarez", "Nezahualcoyotl", "Nextlalpan", "Nicolas Romero",
        "Tecamac", "Teoloyucan", "Tepetlaoxtoc", "Tepotzotlan", "Texcoco",
        "Tlalnepantla de Baz", "Tultepec", "Tultitlan", "Valle de Chalco Solidaridad",
        "Zumpango"
    }
    pm_fields = ["NRA", "ESTADO", "MUNICIPIO", "CAS", "PM_2015", "PM_2016", "PM_2017", "PM_2018", "PM_2019"]
    pm_cols = ["PM_2015", "PM_2016", "PM_2017", "PM_2018", "PM_2019"]
    raw_pm_by_nra = {}
    for year in range(2015, 2020):
        air_path = RAW_DIR / f"retc_{year}_air.csv"
        with open(air_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r["CAS"].strip() == "124-38-9" and r["MUNICIPIO"].strip() in FILTRO_SIMAT_MASTER:
                    nra = r["NRA"].strip()
                    if nra not in raw_pm_by_nra:
                        raw_pm_by_nra[nra] = {
                            "NRA": nra,
                            "ESTADO": r["ESTADO"].strip(),
                            "MUNICIPIO": r["MUNICIPIO"].strip(),
                            "CAS": "124-38-9",
                            "PM_2015": 0.0, "PM_2016": 0.0, "PM_2017": 0.0, "PM_2018": 0.0, "PM_2019": 0.0,
                        }
                    val = float(r["AIRE"]) if r["AIRE"] and r["AIRE"].strip() != "" else 0.0
                    raw_pm_by_nra[nra][f"PM_{year}"] += val

    pm_rows = list(raw_pm_by_nra.values())
    consolidated_pm = {}

    for r in pm_rows:
        old_nra = r["NRA"].strip()
        canon_nra = nra_to_canonical.get(old_nra, old_nra)
        if canon_nra not in consolidated_pm:
            # Initialize with canonical NRA
            new_r = dict(r)
            new_r["NRA"] = canon_nra
            for c in pm_cols:
                new_r[c] = float(r[c])
            consolidated_pm[canon_nra] = new_r
        else:
            # Sum emissions across years (since years do not overlap, this combines the time series)
            existing = consolidated_pm[canon_nra]
            for c in pm_cols:
                val = float(r[c])
                existing[c] += val
            # If the current row is the canonical NRA itself, prefer its ESTADO/MUNICIPIO
            if old_nra == canon_nra:
                existing["ESTADO"] = r["ESTADO"]
                existing["MUNICIPIO"] = r["MUNICIPIO"]

    clean_pm_rows = sorted(consolidated_pm.values(), key=lambda x: x["NRA"])
    for out_path in [PROC_DIR / "retc_15_19_pm_clean.csv", PROC_DIR / "retc_15_19_pm.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=pm_fields)
            writer.writeheader()
            writer.writerows(clean_pm_rows)

    # Build retc_15_19_pm_est_complete.csv
    est_short_by_nra = {r["NRA"]: r for r in est_short_rows}
    pm_est_fields = pm_fields + ["NOMBRE", "SCIAN", "SECTOR", "PARQUE INDUSTRIAL", "COORDENADA_UTM_X", "COORDENADA_UTM_Y"]
    pm_est_rows = []
    for r in clean_pm_rows:
        nra = r["NRA"]
        est_info = est_short_by_nra.get(nra, {})
        merged_r = dict(r)
        for k in ["NOMBRE", "SCIAN", "SECTOR", "PARQUE INDUSTRIAL", "COORDENADA_UTM_X", "COORDENADA_UTM_Y"]:
            merged_r[k] = est_info.get(k, "")
        pm_est_rows.append(merged_r)

    for out_path in [PROC_DIR / "retc_15_19_pm_est_complete_clean.csv", PROC_DIR / "retc_15_19_pm_est_complete.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=pm_est_fields)
            writer.writeheader()
            writer.writerows(pm_est_rows)

    # Compute 90th percentile per year (ignoring 0s, matching pandas replace({0: np.nan}).quantile(0.9))
    q90 = {}
    for c in pm_cols:
        nonzero_vals = [r[c] for r in pm_est_rows if r[c] > 0]
        q90[c] = compute_Percentile_linear(nonzero_vals, 0.90)

    # Filter top 10% and spurious (< 3 non-zero years) formatting 0.0 as empty string (NaN in pandas)
    top10_rows = []
    spur_rows = []
    for r in pm_est_rows:
        nonzero_count = sum(1 for c in pm_cols if r[c] > 0)
        is_top10 = any(r[c] > q90[c] for c in pm_cols if r[c] > 0)
        formatted_r = dict(r)
        for c in pm_cols:
            formatted_r[c] = r[c] if r[c] > 0 else ""
        if is_top10:
            top10_rows.append(formatted_r)
        if nonzero_count < 3:
            spur_rows.append(formatted_r)

    for out_path in [PROC_DIR / "retc_15_19_pm_est_top10_clean.csv", PROC_DIR / "retc_15_19_pm_est_top10.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=pm_est_fields)
            writer.writeheader()
            writer.writerows(top10_rows)

    for out_path in [PROC_DIR / "retc_15_19_pm_est_spur_clean.csv", PROC_DIR / "retc_15_19_pm_est_spur.csv"]:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=pm_est_fields)
            writer.writeheader()
            writer.writerows(spur_rows)

    print(f"Consolidated PM emissions tables: {len(pm_rows)} -> {len(clean_pm_rows)} unique emitting facilities.")
    print(f"  - Top 10% emitting sources: {len(top10_rows)} rows")
    print(f"  - Spurious (<3 active years) sources: {len(spur_rows)} rows")


if __name__ == "__main__":
    main()
