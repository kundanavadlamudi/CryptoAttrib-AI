from pathlib import Path
import json
import yaml


# Project root:
# CryptoAttrib-AI/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw GraphSense YAML files are kept locally here:
# CryptoAttrib-AI/graphsense_data/
DATA_DIR = PROJECT_ROOT / "graphsense_data"

# Generated VASP database:
# CryptoAttrib-AI/backend/graphsense/known_vasps_eth.json
OUTPUT_DIR = PROJECT_ROOT / "backend" / "graphsense"
OUTPUT_FILE = OUTPUT_DIR / "known_vasps_eth.json"


# GraphSense actor ID -> human-readable VASP name
VASP_NAMES = {
    "binance": "Binance",
    "bitfinex": "Bitfinex",
    "bybit": "Bybit",
    "cryptocom": "Crypto.com",
    "deribit": "Deribit",
    "huobi": "Huobi",
    "kucoin": "KuCoin",
    "okex": "OKX",
    "swissborg": "SwissBorg",
}


def normalize_address(address: str) -> str:
    """Normalize an Ethereum address for consistent lookup."""
    return address.strip().lower()


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"GraphSense data directory not found: {DATA_DIR}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    known_vasps = {}

    yaml_files = sorted(
        DATA_DIR.glob("exchange-wallets-*.yaml")
    )

    print(f"Found {len(yaml_files)} exchange-wallet YAML files.\n")

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                pack = yaml.safe_load(f)

            if not isinstance(pack, dict):
                print(f"Skipping {yaml_file.name}: invalid YAML structure")
                continue

            if pack.get("category") != "exchange":
                continue

            actor_id = pack.get("actor")

            if not actor_id:
                print(f"Skipping {yaml_file.name}: no actor")
                continue

            vasp_name = VASP_NAMES.get(
                actor_id,
                actor_id.replace("_", " ").title()
            )

            eth_count = 0

            for tag in pack.get("tags", []):
                if not isinstance(tag, dict):
                    continue

                address = tag.get("address")
                currency = tag.get("currency")

                # We only want Ethereum addresses.
                if not address or currency != "ETH":
                    continue

                normalized = normalize_address(address)

                if normalized not in known_vasps:
                    known_vasps[normalized] = {
                        "vasp_id": actor_id,
                        "vasp_name": vasp_name,
                        "label": (
                            tag.get("label")
                            or pack.get("label")
                            or pack.get("title")
                        ),
                        "currency": "ETH",
                        "source": (
                            tag.get("source")
                            or pack.get("source")
                        ),
                        "confidence": pack.get("confidence"),
                    }

                    eth_count += 1

            print(
                f"{yaml_file.name}: "
                f"{eth_count} ETH addresses"
            )

        except Exception as e:
            print(
                f"ERROR processing "
                f"{yaml_file.name}: {e}"
            )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            known_vasps,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print(
        f"Total unique ETH addresses: "
        f"{len(known_vasps)}"
    )
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()