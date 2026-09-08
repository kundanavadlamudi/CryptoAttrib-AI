import json
from pathlib import Path


# Find the project root:
# CryptoAttrib-AI/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Our generated GraphSense database
VASP_DATA_FILE = (
    PROJECT_ROOT
    / "backend"
    / "graphsense"
    / "known_vasps_eth.json"
)


with open(VASP_DATA_FILE, "r", encoding="utf-8") as f:
    KNOWN_VASPS = json.load(f)


def match_address(address: str):
    """Match an Ethereum address against GraphSense data."""
    if not address:
        return None

    return KNOWN_VASPS.get(address.strip().lower())


def find_first_vasp(hops):
    """Find the first known VASP in a transaction path."""

    for hop in hops:
        address = hop.get("address")

        if not address:
            continue

        result = match_address(address)

        if result:
            return {
                "matched_vasp": result["vasp_name"],
                "vasp_id": result["vasp_id"],
                "matched_address": address,
                "tx_hash": hop.get("tx_hash"),
                "metadata": result,
            }

    return None


# ---------------------------------------------------------
# TEST 1: Known address
# ---------------------------------------------------------

known = "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8"

print("TEST 1: Known address")
print(match_address(known))


# ---------------------------------------------------------
# TEST 2: Uppercase address
# ---------------------------------------------------------

print("\nTEST 2: Uppercase address")
print(match_address(known.upper()))


# ---------------------------------------------------------
# TEST 3: Unknown address
# ---------------------------------------------------------

print("\nTEST 3: Unknown address")

unknown = "0x0000000000000000000000000000000000000001"

print(match_address(unknown))


# ---------------------------------------------------------
# TEST 4: Multi-hop path
# ---------------------------------------------------------

print("\nTEST 4: Multi-hop path")

hops = [
    {
        "address": "0x1111111111111111111111111111111111111111",
        "tx_hash": "0xaaa",
    },
    {
        "address": "0x2222222222222222222222222222222222222222",
        "tx_hash": "0xbbb",
    },
    {
        "address": known,
        "tx_hash": "0xccc",
    },
]

print(find_first_vasp(hops))