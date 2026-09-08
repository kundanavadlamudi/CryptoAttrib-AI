"""
ethereum_feature_extractor.py

Extracts behavioral features from normalized Ethereum transactions.

Input format:
[
    {
        "hash": "...",
        "from": "...",
        "to": "...",
        "value": 2.5,
        "asset": "ETH",
        "timestamp": 1735689600,
        "direction": "out"
    },
    ...
]

This module is responsible only for feature extraction.
It does not perform VASP attribution or risk classification.
"""

from typing import List, Dict, Any
from datetime import datetime


def extract_features(
    wallet: str,
    transactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Convert Ethereum transactions into wallet-level behavioral features.
    """

    wallet = wallet.lower()

    if not transactions:
        return {
            "total_transactions": 0,
            "sent_transactions": 0,
            "received_transactions": 0,
            "total_sent_eth": 0.0,
            "total_received_eth": 0.0,
            "average_sent_eth": 0.0,
            "average_received_eth": 0.0,
            "max_sent_eth": 0.0,
            "max_received_eth": 0.0,
            "unique_counterparties": 0,
            "wallet_lifetime_seconds": 0,
        }

    sent = []
    received = []
    counterparties = set()
    timestamps = []

    for tx in transactions:
        value = float(tx.get("value", 0) or 0)
        timestamp = int(tx.get("timestamp", 0) or 0)

        if timestamp > 0:
            timestamps.append(timestamp)

        from_addr = (tx.get("from") or "").lower()
        to_addr = (tx.get("to") or "").lower()

        if from_addr == wallet:
            sent.append(value)

            if to_addr and to_addr != wallet:
                counterparties.add(to_addr)

        elif to_addr == wallet:
            received.append(value)

            if from_addr and from_addr != wallet:
                counterparties.add(from_addr)

    total_sent = sum(sent)
    total_received = sum(received)

    if timestamps:
        wallet_lifetime = max(timestamps) - min(timestamps)
    else:
        wallet_lifetime = 0

    features = {
        # Activity
        "total_transactions": len(transactions),
        "sent_transactions": len(sent),
        "received_transactions": len(received),

        # ETH volume
        "total_sent_eth": round(total_sent, 6),
        "total_received_eth": round(total_received, 6),

        # Average transaction values
        "average_sent_eth": round(
            total_sent / len(sent), 6
        ) if sent else 0.0,

        "average_received_eth": round(
            total_received / len(received), 6
        ) if received else 0.0,

        # Maximum transaction values
        "max_sent_eth": round(max(sent), 6) if sent else 0.0,
        "max_received_eth": round(max(received), 6)
        if received else 0.0,

        # Network behavior
        "unique_counterparties": len(counterparties),

        # Wallet activity duration
        "wallet_lifetime_seconds": wallet_lifetime,
    }

    return features


def extract_features_from_transactions(
    wallet: str,
    transactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Alias kept for readability when called from the backend.
    """
    return extract_features(wallet, transactions)
