import os, re, sys, time, glob, shutil, subprocess

BASE = "/Users/gabrielevangelista/thesis-cdmx-air"
OUT_DIR = f"{BASE}/03-analysis/run_aermod_postfile_95d"
AERMAP_OUT = f"{BASE}/02-data/processed/aermap_out"
AERMET_OUT = f"{BASE}/02-data/processed/aermet_out"
BIN_DIR = f"{BASE}/03-analysis/aermod_bin"

# 1. Localizar binario de AERMOD compilado en Mac
def find_aermod_bin():
    excl = (".zip", ".f", ".f90", ".for", ".o", ".mod", ".txt", ".md", ".sh", ".inp", ".out", ".exe")
    for root, dirs, files in os.walk(BIN_DIR):
        depth = root[len(BIN_DIR):].count(os.sep)
        if depth > 2:
            continue
        for f in sorted(files):
            fl = f.lower()
            if fl.startswith("aermod") and not fl.endswith(excl):
                cand = os.path.join(root, f)
                if os.path.isfile(cand):
                    os.chmod(cand, 0o755)
                    return cand
    # Respaldo: leer ruta desde run_all_years.sh
    sh_path = f"{BASE}/03-analysis/run_aermod_emisfact/run_all_years.sh"
    if os.path.exists(sh_path):
        txt = open(sh_path).read()
        m = re.search(r"(/[^\s\"']+aermod[^\s\"']*)", txt)
        if m and os.path.isfile(m.group(1)):
            os.chmod(m.group(1), 0o755)
            return m.group(1)
    return None

AERMOD_BIN = find_aermod_bin()
if not AERMOD_BIN:
    sys.exit("[ERROR] No se encontró el binario de AERMOD en aermod_bin/. Revisa la ruta.")
print(f"[OK] Binario encontrado: {AERMOD_BIN}")

free_gb = shutil.disk_usage(OUT_DIR).free / 1e9
print(f"[OK] Espacio libre en disco: {free_gb:.1f} GB (se requieren ~4.5 GB)")
if free_gb < 7.0:
    sys.exit("[ERROR] Menos de 7 GB libres. Libera espacio antes de lanzar.")

# 2. Definir las 5 corridas: (etiqueta, año_emisiones, año_meteorología)
CORRIDAS = [
    ("real_2015",     2015, 2015),
    ("real_2017",     2017, 2017),
    ("real_2019",     2019, 2019),
    ("fija2015_2017", 2015, 2017),
    ("fija2015_2019", 2015, 2019),
]

# Verificar existencia de todos los insumos antes de arrancar
for tag, yr_e, yr_m in CORRIDAS:
    for p in [
        f"{AERMAP_OUT}/sources_emisfact_{yr_e}.so",
        f"{AERMAP_OUT}/receptores_elevados.rou",
        f"{AERMET_OUT}/aer_{yr_m}.sfc",
        f"{AERMET_OUT}/aer_{yr_m}.pfl",
    ]:
        if not os.path.isfile(p):
            sys.exit(f"[ERROR] Falta archivo de entrada para {tag}: {p}")
print("[OK] Todos los archivos .so, .rou, .sfc y .pfl verificados.")

def build_inp(tag, yr_e, yr_m, run_mode="RUN"):
    yy = yr_m % 100
    # POLLUTID OTHER usa la misma física gaussiana que PM25 en DFAULT CONC,
    # pero permite AVERTIME 1 sin bloqueos de formato NAAQS.
    return f"""CO STARTING
   TITLEONE  Horaria 95d Pre/Post PLANEA - {tag} (Emis {yr_e}, Met {yr_m})
   TITLETWO  285 Fuentes AP-42 + EMISFACT MHRDOW -> 3172 Escuelas
   MODELOPT  DFAULT CONC
   AVERTIME  1
   POLLUTID  OTHER
   FLAGPOLE  1.5
   RUNORNOT  {run_mode}
   ERRORFIL  errors_{tag}.err
CO FINISHED

SO STARTING
   INCLUDED  {AERMAP_OUT}/sources_emisfact_{yr_e}.so
SO FINISHED

RE STARTING
   INCLUDED  {AERMAP_OUT}/receptores_elevados.rou
RE FINISHED

ME STARTING
   SURFFILE  {AERMET_OUT}/aer_{yr_m}.sfc
   PROFFILE  {AERMET_OUT}/aer_{yr_m}.pfl
   SURFDATA  766793  {yr_m}  AICM_CDMX
   UAIRDATA  76679   {yr_m}  AICM_CDMX
   SITEDATA  00000   {yr_m}  NONE
   PROFBASE  2230.0  METERS
   STARTEND  {yy:02d} 04 28  {yy:02d} 07 31
ME FINISHED

OU STARTING
   RECTABLE  ALLAVE  FIRST
   POSTFILE  1  ALL  PLOT  post_{tag}.plt
   SUMMFILE  summary_{tag}.sum
OU FINISHED
"""

# 3. Pre-flight check (2 segundos, RUNORNOT NOT)
print("\n[CHECK] Ejecutando prueba en seco (RUNORNOT NOT) sobre real_2015...")
with open(f"{OUT_DIR}/aermod.inp", "w") as f:
    f.write(build_inp("preflight_2015", 2015, 2015, run_mode="NOT"))

res = subprocess.run([AERMOD_BIN], cwd=OUT_DIR, capture_output=True, text=True)
out_txt = open(f"{OUT_DIR}/aermod.out", errors="ignore").read() if os.path.exists(f"{OUT_DIR}/aermod.out") else ""
if not re.search(r"A Total of\s+0 Fatal Error Message", out_txt):
    print("[FALLO EN PRE-FLIGHT] Revisa los errores detectados por AERMOD:")
    if os.path.exists(f"{OUT_DIR}/errors_preflight_2015.err"):
        print(open(f"{OUT_DIR}/errors_preflight_2015.err").read()[:2000])
    print(res.stdout[-1000:], res.stderr[-1000:])
    sys.exit(1)

print("[OK] Pre-flight superado con 0 errores fatales. Iniciando las 5 corridas...\n")
for tmp in ["errors_preflight_2015.err", "summary_preflight_2015.sum", "post_preflight_2015.plt", "aermod.out"]:
    tp = os.path.join(OUT_DIR, tmp)
    if os.path.exists(tp):
        os.remove(tp)

# 4. Ejecutar las 5 corridas en cadena
t_global = time.time()
for i, (tag, yr_e, yr_m) in enumerate(CORRIDAS, 1):
    plt_path = f"{OUT_DIR}/post_{tag}.plt"
    if os.path.exists(plt_path) and os.path.getsize(plt_path) > 100_000_000:
        print(f"[{i}/5] {tag}: ya existe ({os.path.getsize(plt_path)/1e6:.1f} MB), saltando.")
        continue

    inp_txt = build_inp(tag, yr_e, yr_m, run_mode="RUN")
    with open(f"{OUT_DIR}/aermod_{tag}.inp", "w") as f:
        f.write(inp_txt)
    with open(f"{OUT_DIR}/aermod.inp", "w") as f:
        f.write(inp_txt)

    t0 = time.time()
    print(f"[{i}/5] Corriendo {tag} (Emis {yr_e}, Met {yr_m}) | Inicio: {time.strftime('%H:%M:%S')}", flush=True)
    proc = subprocess.run([AERMOD_BIN], cwd=OUT_DIR)
    elapsed = (time.time() - t0) / 60.0

    if os.path.exists(f"{OUT_DIR}/aermod.out"):
        shutil.move(f"{OUT_DIR}/aermod.out", f"{OUT_DIR}/aermod_{tag}.out")

    sz_mb = os.path.getsize(plt_path) / 1e6 if os.path.exists(plt_path) else 0.0
    out_check = open(f"{OUT_DIR}/aermod_{tag}.out", errors="ignore").read()
    ok = bool(re.search(r"A Total of\s+0 Fatal Error Message", out_check))
    status = "OK" if (proc.returncode == 0 and ok and sz_mb > 10) else "REVISAR"
    print(f"      -> [{status}] {tag} terminado en {elapsed:.1f} min | post_{tag}.plt = {sz_mb:.1f} MB\n", flush=True)

print(f"=== PROCESO COMPLETO EN {(time.time() - t_global)/60.0:.1f} MINUTOS ===")
