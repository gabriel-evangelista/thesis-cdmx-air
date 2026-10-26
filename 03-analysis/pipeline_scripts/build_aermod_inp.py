"""
Script reproducible (Commit 2 AERMOD):
Genera los archivos de control aermod_YYYY.inp (2015-2019) en 03-analysis/run_aermod/
conectando bloques CO (FLAGPOLE 1.5), SO (285 fuentes AP-42), RE (3,172 escuelas) y ME (AICM 76679).
"""
import os

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
RUN_DIR = f"{BASE}/03-analysis/run_aermod"
AERMAP_OUT = f"{BASE}/02-data/processed/aermap_out"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"

os.makedirs(RUN_DIR, exist_ok=True)

YEARS = [2015, 2016, 2017, 2018, 2019]

for yr in YEARS:
    inp_content = f"""CO STARTING
   TITLEONE  Modelacion Dispersion PM ZMVM - Anio {yr} (285 Fuentes AP-42 -> 3172 Escuelas)
   TITLETWO  Evaluacion Exposicion Escolar con Terreno SRTM 30m y FLAGPOLE 1.5m
   MODELOPT  DFAULT CONC
   AVERTIME  24 ANNUAL
   POLLUTID  PM25
   FLAGPOLE  1.5
   RUNORNOT  RUN
   ERRORFIL  errors_{yr}.err
CO FINISHED

SO STARTING
   INCLUDED  {AERMAP_OUT}/sources_{yr}.so
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
   PLOTFILE  ANNUAL  ALL  plot_annual_all_{yr}.plt
   PLOTFILE  ANNUAL  TURBINA_  plot_annual_turb_{yr}.plt
   PLOTFILE  ANNUAL  FUNDICIO  plot_annual_fund_{yr}.plt
   PLOTFILE  ANNUAL  HORNO_VI  plot_annual_vidr_{yr}.plt
   PLOTFILE  ANNUAL  SECADO_Q  plot_annual_quim_{yr}.plt
   PLOTFILE  ANNUAL  CALDERA_  plot_annual_cald_{yr}.plt
   SUMMFILE  summary_{yr}.sum
OU FINISHED
"""
    inp_path = f"{RUN_DIR}/aermod_{yr}.inp"
    with open(inp_path, "w", encoding="utf-8") as f:
        f.write(inp_content)
    print(f"[OK] Generado: {inp_path}")

# Crear un archivo de chequeo instantáneo (RUNORNOT NOT) para validar sintaxis en 1 segundo
with open(f"{RUN_DIR}/aermod_2017.inp", "r") as f:
    chk_txt = f.read().replace("RUNORNOT  RUN", "RUNORNOT  NOT")
with open(f"{RUN_DIR}/aermod.inp", "w") as f:
    f.write(chk_txt)
print(f"[OK] Generado archivo de chequeo rapido (RUNORNOT NOT): {RUN_DIR}/aermod.inp")
