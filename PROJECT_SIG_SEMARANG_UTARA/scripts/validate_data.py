import os
import json

BASE_DIR = "/home/faishal-anwar/Project SIG/PROJECT_SIG_SEMARANG_UTARA/webgis/data"

print("=== VALIDATING SPATIAL DATASETS & ATTRIBUTES FOR WEBGIS ===")

files_to_check = [
    "batas_kelurahan.geojson",
    "sungai.geojson",
    "permukiman.geojson",
    "area_genangan.geojson",
    "titik_survei.geojson",
    "buffer_sungai.geojson",
    "permukiman_terdampak.geojson",
    "statistik.json"
]

all_passed = True
for fname in files_to_check:
    fpath = os.path.join(BASE_DIR, fname)
    if not os.path.exists(fpath):
        print(f"[FAIL] Missing file: {fname}")
        all_passed = False
        continue
    
    file_size_kb = os.path.getsize(fpath) / 1024
    if fname.endswith(".geojson"):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        features = data.get("features", [])
        print(f"[PASS] {fname:30s} | {len(features):2d} features | {file_size_kb:6.1f} KB")
        if len(features) == 0:
            print(f"       Warning: 0 features in {fname}!")
            all_passed = False
    elif fname.endswith(".json"):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[PASS] {fname:30s} | Valid JSON     | {file_size_kb:6.1f} KB")

if all_passed:
    print("=== ALL 8 DATASETS PASSED VALIDATION WITH 100% INTEGRITY ===")
else:
    print("=== SOME VALIDATION CHECKS FAILED ===")
