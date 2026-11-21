"""
Genera un caso de prueba autocontenido (5 fuentes, 20 receptores, 7 días de meteorología)
para verificar la compilación de AERMOD en ~2 segundos.
"""
import os

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
AERMAP_OUT = f"{BASE}/02-data/processed/aermap_out"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
TOY_DIR = f"{BASE}/00-onboarding-aermod/toy_case"
os.makedirs(TOY_DIR, exist_ok=True)

# 1. Recortar las primeras 5 fuentes (LOCATION + SRCPARAM) de sources_2017.so
locs, params, srcids = [], [], []
with open(f"{AERMAP_OUT}/sources_2017.so", "r", encoding="utf-8") as f:
    for line in f:
        s = line.strip()
        if s.startswith("LOCATION") and len(locs) < 5:
            locs.append(line)
            srcids.append(s.split()[1])
        elif s.startswith("SRCPARAM") and len(params) < 5:
            if s.split()[1] in srcids:
                params.append(line)

with open(f"{TOY_DIR}/toy_sources.so", "w", encoding="utf-8") as f:
    f.write("** Toy Case: 5 fuentes puntuales reales de la ZMVM\n")
    f.writelines(locs)
    f.write("\n")
    f.writelines(params)
    f.write("\n   SRCGROUP  ALL\n")

# 2. Recortar los primeros 20 receptores de receptores_elevados.rou
recs = []
with open(f"{AERMAP_OUT}/receptores_elevados.rou", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip().startswith("DISCCART") and len(recs) < 20:
            recs.append(line)

with open(f"{TOY_DIR}/toy_receptors.rou", "w", encoding="utf-8") as f:
    f.write("** Toy Case: 20 receptores escolares reales\n")
    f.writelines(recs)

# 3. Recortar 7 días (168 horas) de aer_2017.sfc y aer_2017.pfl
with open(f"{AERMET_OUT}/aer_2017.sfc", "r", encoding="utf-8") as fin, \
     open(f"{TOY_DIR}/toy_met.sfc", "w", encoding="utf-8") as fout:
    fout.write(fin.readline())
    for _ in range(168):
        fout.write(fin.readline())

with open(f"{AERMET_OUT}/aer_2017.pfl", "r", encoding="utf-8") as fin, \
     open(f"{TOY_DIR}/toy_met.pfl", "w", encoding="utf-8") as fout:
    for line in fin:
        parts = line.split()
        try:
            mm, dd = int(parts[1]), int(parts[2])
        except (IndexError, ValueError):
            continue
        if mm == 1 and dd <= 7:
            fout.write(line)
        elif mm > 1 or dd > 7:
            break

# 4. Escribir el aermod.inp del Toy Case
toy_inp = """CO STARTING
   TITLEONE  Toy Case Laboratorio - Verificacion de Entorno AERMOD
   TITLETWO  5 fuentes x 20 receptores x 7 dias (Ene 2017)
   MODELOPT  DFAULT CONC
   AVERTIME  24
   POLLUTID  OTHER
   FLAGPOLE  1.5
   RUNORNOT  RUN
   ERRORFIL  toy_errors.err
CO FINISHED

SO STARTING
   INCLUDED  toy_sources.so
SO FINISHED

RE STARTING
   INCLUDED  toy_receptors.rou
RE FINISHED

ME STARTING
   SURFFILE  toy_met.sfc
   PROFFILE  toy_met.pfl
   SURFDATA  766793  2017  AICM_CDMX
   UAIRDATA  76679   2017  AICM_CDMX
   SITEDATA  00000   2017  NONE
   PROFBASE  2230.0  METERS
ME FINISHED

OU STARTING
   RECTABLE  ALLAVE  FIRST
   PLOTFILE  24      ALL   FIRST toy_plot_24h.plt
   POSTFILE  24      ALL   PLOT  toy_post_24h.pst
   SUMMFILE  toy_summary.sum
OU FINISHED
"""
with open(f"{TOY_DIR}/aermod.inp", "w", encoding="utf-8") as f:
    f.write(toy_inp)

print(f"[OK] Toy case generado en: {TOY_DIR}")
