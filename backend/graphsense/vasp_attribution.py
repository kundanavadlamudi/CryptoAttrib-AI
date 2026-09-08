"""
vasp_attribution.py

Reusable VASP attribution logic, backed by the GraphSense-derived
known_vasps_eth.json database. This module has no side effects on
import (no prints, no test code) so it's safe for main.py to import.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VASP_DATA_FILE = (
    PROJECT_ROOT
    / "backend"
    / "graphsense"
    / "known_vasps_eth.json"
)

with open(VASP_DATA_FILE, "r", encoding="utf-8") as f:
    KNOWN_VASPS: Dict[str, Any] = json.load(f)


def match_address(address: str) -> Optional[Dict[str, Any]]:
    """Match a single Ethereum address against the GraphSense-derived VASP database."""
    if not address:
        return None
    return KNOWN_VASPS.get(address.strip().lower())


def find_first_vasp_in_hops(
    hops: Dict[str, int],
    origin: str,
) -> Optional[Dict[str, Any]]:
    """
    Given graph_engine's hop-distance dict ({address: hop_distance}),
    check each traced address (nearest hop first) against known_vasps_eth.json
    and return the first VASP match found.

    Parameters
    ----------
    hops : dict
        Output of graph_engine.bfs_hop_trace(), e.g. {"0xabc...": 0, "0xdef...": 1}
    origin : str
        The wallet address being investigated (excluded from matching).

    Returns
    -------
    dict or None
        {
            "matched_vasp": "Binance",
            "vasp_id": "binance",
            "matched_address": "0x...",
            "hops": 2,
            "metadata": {...}
        }
        or None if no traced address matches a known VASP.
    """
    origin = origin.lower()

    # Check nearest hops first (hop 1 before hop 2, etc.)
    candidates = sorted(
        ((addr, dist) for addr, dist in hops.items() if addr != origin),
        key=lambda pair: pair[1],
    )

    for address, hop_distance in candidates:
        result = match_address(address)
        if result:
            return {
                "matched_vasp": result["vasp_name"],
                "vasp_id": result["vasp_id"],
                "matched_address": address,
                "hops": hop_distance,
                "metadata": result,
            }

    return None