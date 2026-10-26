"""
Script reproducible para sincronizar salidas de AERMAP (.rou y .sou)
con el catálogo de escuelas (CCT) y generar la tabla puente definitiva.
Puede adaptarse a cualquier otra ciudad o dominio cambiando base_dir.
"""
import csv, glob, os, shutil

BASE_DIR = "/Users/gabrielevangelista/thesis-cdmx-air"
ROU_PATH = f"{BASE_DIR}/03-analysis/run_aermap/receptores_elevados.rou"
SOU_PATH = f"{BASE_DIR}/03-analysis/run_aermap/fuentes_elevadas.sou"
OUT_DIR  = f"{BASE_DIR}/02-data/processed/aermap_out"

def sync_receptors():
    os.makedirs(OUT_DIR, exist_ok=True)
    for src in [ROU_PATH, SOU_PATH]:
        if os.path.exists(src):
            shutil.copy(src, f"{OUT_DIR}/{os.path.basename(src)}")

    rou_file = f"{OUT_DIR}/receptores_elevados.rou"
    rou_dict = {}
    rec_count = 1
    with open(rou_file, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 5 and parts[0] == "DISCCART":
                x, y = round(float(parts[1]), 2), round(float(parts[2]), 2)
                rou_dict[(x, y)] = {
                    "Z_ELEV": float(parts[3]),
                    "Z_HILL": float(parts[4]),
                    "RECID": f"R{rec_count:05d}"
                }
                rec_count += 1

    matches = glob.glob(f"{BASE_DIR}/**/tabla_enlace_cct_recid.csv", recursive=True)
    raw_matches = [m for m in matches if "aermap_out" not in m]
    source_csv = raw_matches[0] if raw_matches else matches[0]

    merged_rows = []
    with open(source_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        out_fields = [fld for fld in reader.fieldnames if fld not in ["RECID", "Z_ELEV", "Z_HILL"]]
        out_fields.extend(["RECID", "Z_ELEV", "Z_HILL"])
        for row in reader:
            coord = (round(float(row["X_UTM"]), 2), round(float(row["Y_UTM"]), 2))
            if coord in rou_dict:
                new_row = {k: row[k] for k in out_fields if k in row}
                new_row.update(rou_dict[coord])
                merged_rows.append(new_row)

    out_csv = f"{OUT_DIR}/tabla_enlace_cct_recid.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(merged_rows)

    print(f"[OK] Sincronización completa: {len(rou_dict)} receptores únicos -> {len(merged_rows)} CCTs en {out_csv}")

if __name__ == "__main__":
    sync_receptors()
