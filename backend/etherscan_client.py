"""
etherscan_client.py
Fetches raw transactions for a wallet address from Etherscan.
Falls back to demo data if no API key is set or the live call fails,
so the pipeline still works during offline demos.
"""

import os
import logging
from typing import List, Dict, Any

import httpx

logger = logging.getLogger("etherscan_client")

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"


class EtherscanClientError(Exception):
    pass


def _normalize_tx(raw: Dict[str, Any], wallet: str) -> Dict[str, Any]:
    from_addr = raw.get("from", "").lower()
    to_addr = raw.get("to", "").lower()
    value_wei = int(raw.get("value", 0) or 0)
    value_eth = value_wei / 1e18

    return {
        "hash": raw.get("hash"),
        "from": from_addr,
        "to": to_addr,
        "value": round(value_eth, 6),
        "asset": "ETH",
        "timestamp": int(raw.get("timeStamp", 0) or 0),
        "direction": "out" if from_addr == wallet.lower() else "in",
    }


def _fetch_live(wallet: str) -> List[Dict[str, Any]]:
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }
    try:
        resp = httpx.get(ETHERSCAN_BASE_URL, params=params, timeout=10.0)
        resp.raise_for_status()
    except httpx.TimeoutException as e:
        raise EtherscanClientError(f"Etherscan request timed out: {e}")
    except httpx.HTTPError as e:
        raise EtherscanClientError(f"Etherscan request failed: {e}")

    data = resp.json()
    if data.get("status") == "0" and not isinstance(data.get("result"), list):
        raise EtherscanClientError(f"Etherscan API error: {data.get('message')}")

    raw_txs = data.get("result", [])
    if not isinstance(raw_txs, list):
        raw_txs = []

    return [_normalize_tx(tx, wallet) for tx in raw_txs]


def _demo_transactions(wallet: str) -> List[Dict[str, Any]]:
    logger.warning("DEMO MODE: returning synthetic transactions for %s", wallet)
    wallet_a = "0xdemoAAAA000000000000000000000000000001"
    wallet_b = "0xdemoBBBB000000000000000000000000000002"
    known_vasp = "0xdemoVASP000000000000000000000000000003"

    return [
        {"hash": "0xdemo_tx_1", "from": wallet.lower(), "to": wallet_a,
         "value": 2.5, "asset": "ETH", "timestamp": 1735689600, "direction": "out"},
        {"hash": "0xdemo_tx_2", "from": wallet_a, "to": wallet_b,
         "value": 2.3, "asset": "ETH", "timestamp": 1735776000, "direction": "out"},
        {"hash": "0xdemo_tx_3", "from": wallet_b, "to": known_vasp,
         "value": 2.1, "asset": "ETH", "timestamp": 1735862400, "direction": "out"},
    ]


def get_transactions(wallet: str) -> List[Dict[str, Any]]:
    if not ETHERSCAN_API_KEY:
        return _demo_transactions(wallet)

    try:
        txs = _fetch_live(wallet)
        if not txs:
            logger.info("No live transactions found for %s, using demo data", wallet)
            return _demo_transactions(wallet)
        return txs
    except EtherscanClientError as e:
        logger.error("Live Etherscan fetch failed (%s), falling back to demo data", e)
        return _demo_transactions(wallet)