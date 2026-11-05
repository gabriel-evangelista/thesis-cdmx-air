"""
Re-ensambla sources_emisfact_YYYY.so respetando el orden estricto de AERMOD:
1. LOCATION -> 2. SRCPARAM -> 3. EMISFACT (6 factores por linea) -> 4. SRCGROUP (al final)
"""
import csv, os

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
MHRDOW_DIR = f"{BASE}/02-data/processed/emisfact_mhrdow"
CENACE_DIR = f"{BASE}/02-data/processed/cenace_cfe"
AERMAP_OUT = f"{BASE}/02-data/processed/aermap_out"

def read_864_from_emi(emi_path):
    vals = []
    with open(emi_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("SO EMISFACT") or line.strip().startswith("EMISFACT"):
                parts = line.split()
                idx = parts.index("MHRDOW")
                vals.extend(float(x) for x in parts[idx+1:])
    if len(vals) != 864:
        raise ValueError(f"Error en {emi_path}: {len(vals)} valores en vez de 864")
    return vals

profiles = {
    "CFE_BASE":  read_864_from_emi(f"{CENACE_DIR}/emisfact_cfe_base.emi"),
    "CFE_PUNTA": read_864_from_emi(f"{CENACE_DIR}/emisfact_cfe_punta.emi"),
    "CHEMICAL":  read_864_from_emi(f"{MHRDOW_DIR}/emisfact_CHEMICAL.emi"),
    "FOODBEV":   read_864_from_emi(f"{MHRDOW_DIR}/emisfact_FOODBEV.emi"),
    "METALS":    read_864_from_emi(f"{MHRDOW_DIR}/emisfact_METALS.emi"),
    "PLAS_RUB":  read_864_from_emi(f"{MHRDOW_DIR}/emisfact_PLAS_RUB.emi"),
}

cat_csv = f"{AERMAP_OUT}/catalogo_285_fuentes_aermod_ap42.csv"
with open(cat_csv, "r", encoding="utf-8") as f:
    sources = list(csv.DictReader(f))

def assign_emisfact_group(row):
    tech = row["TECH_GROUP"].strip()
    sector = row["SECTOR"].strip().upper()
    scian = row["SCIAN"].strip()
    nombre = row["NOMBRE"].strip().upper()
    municipio = row["MUNICIPIO"].strip().upper()

    if tech == "TURBINA_GAS":
        if "ACOLMAN" in municipio or "VALLE DE MEXICO" in nombre or "COGENERACION" in nombre:
            return "CFE_BASE"
        return "CFE_PUNTA"
    if tech == "HORNO_VIDRIO" or "VIDRIO" in sector or "CEMENTO" in sector or "CELULOSA" in sector or scian.startswith("322"):
        return None
    if scian.startswith("326") or "PLASTICO" in sector:
        return "PLAS_RUB"
    if "QUIMICA" in sector or "PINTURAS" in sector or "PETROLEO" in sector or scian.startswith("325"):
        return "CHEMICAL"
    if tech == "FUNDICION_METAL" or "METAL" in sector or scian.startswith("331") or scian.startswith("332"):
        return "METALS"
    if "ALIMENT" in sector or "BEBIDA" in sector or scian.startswith("311") or scian.startswith("312"):
        return "FOODBEV"
    return None

src_to_prof = {r["SRCID"].strip(): assign_emisfact_group(r) for r in sources}

for yr in [2015, 2016, 2017, 2018, 2019]:
    base_so = f"{AERMAP_OUT}/sources_{yr}.so"
    emi_so = f"{AERMAP_OUT}/sources_emisfact_{yr}.so"

    pre_group_lines = []
    srcgroup_lines = []
    with open(base_so, "r", encoding="utf-8") as f:
        for line in f:
            if "SRCGROUP" in line or "Grupos de fuentes" in line:
                srcgroup_lines.append(line)
            else:
                pre_group_lines.append(line)

    emisfact_lines = ["\n** Factores horarios de emision MHRDOW (864 factores por fuente activa)\n"]
    for r in sources:
        sid = r["SRCID"].strip()
        ptag = src_to_prof[sid]
        if ptag and ptag in profiles:
            vec = profiles[ptag]
            # 6 valores por linea (144 lineas por fuente) para no exceder jamas el ancho Fortran
            for i in range(0, 864, 6):
                chunk = "  ".join(f"{v:8.5f}" for v in vec[i:i+6])
                emisfact_lines.append(f"   EMISFACT  {sid:<12s}  MHRDOW  {chunk}\n")

    with open(emi_so, "w", encoding="utf-8") as f:
        f.writelines(pre_group_lines)
        f.writelines(emisfact_lines)
        f.write("\n")
        f.writelines(srcgroup_lines)

print("[OK] Archivos sources_emisfact_YYYY.so re-ensamblados con SRCGROUP al final y 6 cols por linea.")
