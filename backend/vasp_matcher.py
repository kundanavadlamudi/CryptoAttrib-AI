import json
import os

VASP_DATA_PATH = os.path.join("vasp_data", "known_vasps.json")

def load_known_vasps():
    with open(VASP_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def match_vasp(address):
    """
    Checks if a given wallet address matches a known VASP.
    Returns the VASP name if matched, otherwise 'unknown'.
    """
    known_vasps = load_known_vasps()
    for entry in known_vasps:
        if entry["address"].lower() == address.lower():
            return entry["name"]
    return "unknown"

# Quick standalone test
if __name__ == "__main__":
    test_address = "TWd4WrZ9wn84f5x1hZhL4DHvk738ns5jwb"  # replace with a real one from your JSON
    result = match_vasp(test_address)
    print(f"Address {test_address} matched to: {result}")