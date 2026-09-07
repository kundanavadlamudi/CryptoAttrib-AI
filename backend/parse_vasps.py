import yaml
import json
import os

# Point this to wherever your graphsense-tagpacks folder is on your laptop
BASE_PATH = r"C:\Users\kunda\graphsense-tagpacks\packs"

# Pick a handful of exchange files — not all of them, to keep the output small for the demo
FILES_TO_PARSE = [
    "exchange-wallets-binance.yaml",
    "exchange-wallets-huobi.yaml",
    "exchange-wallets-bitfinexcom.yaml",
    "exchange-wallets-bitmex_0.yaml",
]

known_vasps = []

for filename in FILES_TO_PARSE:
    filepath = os.path.join(BASE_PATH, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Some files have a top-level label (e.g. Bitmex format), use as fallback
    top_level_label = data.get("label", "unknown")

    tags = data.get("tags", [])
    for tag in tags:
        address = tag.get("address")
        label = tag.get("label", top_level_label)
        if address:
            known_vasps.append({"address": address, "name": label})

# Save the combined result
output_path = os.path.join("vasp_data", "known_vasps.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(known_vasps, f, indent=2)

print(f"Saved {len(known_vasps)} VASP entries to {output_path}")