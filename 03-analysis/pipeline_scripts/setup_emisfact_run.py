"""
1. Recalcula las 5 curvas industriales MHRDOW usando el calendario real (2014-01-01, Mie -> Sab=Dia 4, Dom=Dia 5).
2. Lee los perfiles CFE_BASE y CFE_PUNTA ya generados.
3. Mapea cada una de las 285 fuentes del RETC a su perfil horario y genera sources_emisfact_YYYY.so.
4. Crea los archivos aermod_YYYY.inp en 03-analysis/run_aermod_emisfact/ (sin tocar run_aermod/).
"""
import csv, glob, os
import pandas as pd
import numpy as np

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
CURVES_DIR = f"{BASE}/02-data/raw/industrial_curves"
MHRDOW_DIR = f"{BASE}/02-data/processed/emisfact_mhrdow"
CENACE_DIR = f"{BASE}/02-data/processed/cenace_cfe"
AERMAP_OUT = f"{BASE}/02-data/processed/aermap_out"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
RUN_EMI_DIR = f"{BASE}/03-analysis/run_aermod_emisfact"

os.makedirs(MHRDOW_DIR, exist_ok=True)
os.makedirs(RUN_EMI_DIR, exist_ok=True)

# 1. Calendario exacto donde Día 1 = Miércoles, Día 4 = Sábado, Día 5 = Domingo (2014 no bisiesto)
DT_INDEX = pd.date_range("2014-01-01 00:00:00", periods=8760, freq="h")

def build_864_vector_from_raw(csv_path):
    vals = []
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "," in line:
                try:
                    vals.append(float(line.strip().split(",")[1]))
                except ValueError:
                    continue
    df = pd.DataFrame({"dt": DT_INDEX, "frac": vals})
    df["scalar"] = (df["frac"] / df["frac"].sum()) * 8760.0
    df["month"] = df["dt"].dt.month
    df["hour"] = df["dt"].dt.hour + 1
    df["day_type"] = df["dt"].dt.dayofweek.map(lambda d: 1 if d < 5 else (2 if d == 5 else 3))
    pivot = df.groupby(["day_type", "month", "hour"])["scalar"].mean().unstack("hour")

    vec_864 = []
    for dt_code in [1, 2, 3]:
        for m in range(1, 13):
            for h in range(1, 25):
                vec_864.append(float(pivot.loc[(dt_code, m), h]))
    return vec_864

def read_864_from_emi(emi_path):
    vals = []
    with open(emi_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("SO EMISFACT"):
                parts = line.split()[4:]
                vals.extend(float(x) for x in parts)
    if len(vals) != 864:
        raise ValueError(f"Se esperaban 864 factores en {emi_path}, se encontraron {len(vals)}")
    return vals

# Cargar los 2 perfiles de CFE
profiles = {
    "CFE_BASE":  read_864_from_emi(f"{CENACE_DIR}/emisfact_cfe_base.emi"),
    "CFE_PUNTA": read_864_from_emi(f"{CENACE_DIR}/emisfact_cfe_punta.emi"),
}

# Recalcular las 5 curvas industriales si los CSV crudos están en CURVES_DIR,
# o buscar cualquier CSV de 8760 filas en el proyecto
raw_Search = glob.glob(f"{BASE}/**/*year_normalization*.csv", recursive=True) + glob.glob(f"{CURVES_DIR}/*.csv")
raw_files = {}
for p in raw_Search:
    bn = os.path.basename(p).upper()
    if "CHEM" in bn: raw_files["CHEMICAL"] = p
    elif "FOOD" in bn or "BEV" in bn: raw_files["FOODBEV"] = p
    elif "METAL" in bn: raw_files["METALS"] = p
    elif "PLAS" in bn or "RUB" in bn: raw_files["PLAS_RUB"] = p
    elif "WATER" in bn: raw_files["WATER"] = p

for tag, path in raw_files.items():
    vec = build_864_vector_from_raw(path)
    profiles[tag] = vec
    # Actualizar también el archivo .emi individual corregido
    emi_out = f"{MHRDOW_DIR}/emisfact_{tag}.emi"
    with open(emi_out, "w", encoding="utf-8") as f:
        f.write(f"** Perfil EMISFACT MHRDOW corregido (Calendario 2014 Mie->Sab=Dia4, Dom=Dia5) para {tag}\n")
        for i in range(0, 864, 8):
            chunk = "  ".join(f"{v:8.5f}" for v in vec[i:i+8])
            f.write(f"SO EMISFACT  {tag:<12s}  MHRDOW  {chunk}\n")
    print(f"[OK] Curva {tag:<10s} recalculada con calendario correcto desde: {os.path.basename(path)}")

# Si alguna curva no se encontró como CSV crudo, leerla del .emi existente en MHRDOW_DIR
for tag, fname in [("CHEMICAL", "emisfact_CHEMICAL.emi"), ("FOODBEV", "emisfact_FOODBEV.emi"),
                   ("METALS", "emisfact_METALS.emi"), ("PLAS_RUB", "emisfact_PLAS_RUB.emi"),
                   ("WATER", "emisfact_WATER_YEAR_M.emi")]:
    if tag not in profiles and os.path.exists(f"{MHRDOW_DIR}/{fname}"):
        profiles[tag] = read_864_from_emi(f"{MHRDOW_DIR}/{fname}")
        print(f"[AVISO] Curva {tag} leída desde {fname} existente.")

# 2. Leer el catálogo de las 285 fuentes y asignar perfil horario a cada SRCID
cat_csv = f"{AERMAP_OUT}/catalogo_285_fuentes_aermod_ap42.csv"
with open(cat_csv, "r", encoding="utf-8") as f:
    sources = list(csv.DictReader(f))

def assign_emisfact_group(row):
    tech = row["TECH_GROUP"].strip()
    sector = row["SECTOR"].strip().upper()
    scian = row["SCIAN"].strip()
    nombre = row["NOMBRE"].strip().upper()
    municipio = row["MUNICIPIO"].strip().upper()

    # Centrales eléctricas (TURBINA_GAS)
    if tech == "TURBINA_GAS":
        # CT Valle de México en Acolman (Ciclo Combinado carga base/intermedia) vs Turbogás de punta
        if "ACOLMAN" in municipio or "VALLE DE MEXICO" in nombre or "COGENERACION" in nombre:
            return "CFE_BASE"
        return "CFE_PUNTA"

    # Hornos continuos 24/7 (Vidrio, Cemento, Celulosa y Papel) -> Constante (None)
    if tech == "HORNO_VIDRIO" or "VIDRIO" in sector or "CEMENTO" in sector or "CELULOSA" in sector or scian.startswith("322"):
        return None

    # Plásticos y Hule
    if scian.startswith("326") or "PLASTICO" in sector:
        return "PLAS_RUB"

    # Química, Farmacéutica, Pinturas, Petroquímica
    if "QUIMICA" in sector or "PINTURAS" in sector or "PETROLEO" in sector or scian.startswith("325"):
        return "CHEMICAL"

    # Metalurgia y productos metálicos
    if tech == "FUNDICION_METAL" or "METAL" in sector or scian.startswith("331") or scian.startswith("332"):
        return "METALS"

    # Alimentos y Bebidas
    if "ALIMENT" in sector or "BEBIDA" in sector or scian.startswith("311") or scian.startswith("312"):
        return "FOODBEV"

    # Tratamiento de agua si existiera
    if "AGUA" in nombre or scian.startswith("2213"):
        return "WATER"

    # Resto de fuentes sin certeza -> Constante 24/7
    return None

counts_prof = {}
src_to_prof = {}
for r in sources:
    sid = r["SRCID"].strip()
    p_tag = assign_emisfact_group(r)
    src_to_prof[sid] = p_tag
    counts_prof[p_tag or "CONSTANTE_24_7"] = counts_prof.get(p_tag or "CONSTANTE_24_7", 0) + 1

print("\n=== ASIGNACIÓN DE PERFILES EMISFACT MHRDOW EN LAS 285 FUENTES ===")
for k, v in sorted(counts_prof.items(), key=lambda x: -x[1]):
    print(f"  {k:<16s}: {v:3d} fuentes")

# 3. Generar sources_emisfact_YYYY.so y aermod_YYYY.inp en run_aermod_emisfact
YEARS = [2015, 2016, 2017, 2018, 2019]
for yr in YEARS:
    base_so = f"{AERMAP_OUT}/sources_{yr}.so"
    emi_so = f"{AERMAP_OUT}/sources_emisfact_{yr}.so"

    with open(base_so, "r", encoding="utf-8") as f:
        so_text = f.read()

    emisfact_lines = ["\n** Factores horarios de emision MHRDOW (864 factores por fuente activa)\n"]
    for r in sources:
        sid = r["SRCID"].strip()
        ptag = src_to_prof[sid]
        if ptag and ptag in profiles:
            vec = profiles[ptag]
            for i in range(0, 864, 12):
                chunk = " ".join(f"{v:7.4f}" for v in vec[i:i+12])
                emisfact_lines.append(f"   EMISFACT  {sid:<12s}  MHRDOW  {chunk}\n")

    with open(emi_so, "w", encoding="utf-8") as f:
        f.write(so_text)
        f.writelines(emisfact_lines)

    inp_content = f"""CO STARTING
   TITLEONE  Modelacion Dispersion PM ZMVM con EMISFACT MHRDOW - Anio {yr}
   TITLETWO  285 Fuentes AP-42 + Perfiles Horarios CFE/Industria -> 3172 Escuelas
   MODELOPT  DFAULT CONC
   AVERTIME  24 ANNUAL
   POLLUTID  PM25
   FLAGPOLE  1.5
   RUNORNOT  RUN
   ERRORFIL  errors_emi_{yr}.err
CO FINISHED

SO STARTING
   INCLUDED  {emi_so}
SO FINISHED

RE STARTING
   INCLUDED  {AERMAP_OUT}/receptores_elevados.rou
RE FINISHED

ME STARTING
   SURFFILE  {AERMET_OUT}/aer_{yr}.sfc
   PROFFILE  {AERMET_OUT}/aer_{yr}.pfl
   SURFDATA  766793  {yr}  AICM_CDMX
   UAIRDATA  76679   {yr}  AICM_CDMX
   SITEDATA  00000   {yr}  NONE
   PROFBASE  2230.0  METERS
ME FINISHED

OU STARTING
   RECTABLE  ALLAVE  FIRST
   PLOTFILE  ANNUAL  ALL       plot_emi_annual_all_{yr}.plt
   PLOTFILE  ANNUAL  TURBINA_  plot_emi_annual_turb_{yr}.plt
   PLOTFILE  ANNUAL  FUNDICIO  plot_emi_annual_fund_{yr}.plt
   PLOTFILE  ANNUAL  HORNO_VI  plot_emi_annual_vidr_{yr}.plt
   PLOTFILE  ANNUAL  SECADO_Q  plot_emi_annual_quim_{yr}.plt
   PLOTFILE  ANNUAL  CALDERA_  plot_emi_annual_cald_{yr}.plt
   SUMMFILE  summary_emi_{yr}.sum
OU FINISHED
"""
    with open(f"{RUN_EMI_DIR}/aermod_{yr}.inp", "w", encoding="utf-8") as f:
        f.write(inp_content)

# Crear archivo de validación de 1 segundo (RUNORNOT NOT)
with open(f"{RUN_EMI_DIR}/aermod_2017.inp", "r") as f:
    chk = f.read().replace("RUNORNOT  RUN", "RUNORNOT  NOT")
with open(f"{RUN_EMI_DIR}/aermod.inp", "w") as f:
    f.write(chk)

print(f"\n[OK] Archivos .so y .inp con EMISFACT generados en: {RUN_EMI_DIR}")

