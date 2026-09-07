"""
graph_engine.py
Builds a NetworkX graph from transactions and traces fund flow
outward from a wallet using BFS, hop by hop.
"""

import logging
from typing import List, Dict, Any, Optional

import networkx as nx

logger = logging.getLogger("graph_engine")


def build_graph(wallet: str, transactions: List[Dict[str, Any]]) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_node(wallet.lower(), role="origin")

    for tx in transactions:
        src, dst = tx["from"], tx["to"]
        if not src or not dst:
            continue

        g.add_node(src)
        g.add_node(dst)

        if g.has_edge(src, dst):
            edge = g[src][dst]
            edge["value"] += tx["value"]
            edge["tx_count"] += 1
            edge["tx_hashes"].append(tx["hash"])
        else:
            g.add_edge(
                src, dst,
                value=tx["value"],
                asset=tx.get("asset", "ETH"),
                tx_count=1,
                tx_hashes=[tx["hash"]],
                last_timestamp=tx.get("timestamp"),
            )

    return g


def bfs_hop_trace(g: nx.DiGraph, origin: str, max_hops: int = 3) -> Dict[str, int]:
    origin = origin.lower()
    if origin not in g:
        return {}

    hops: Dict[str, int] = {origin: 0}
    frontier = [origin]
    current_hop = 0

    while frontier and current_hop < max_hops:
        next_frontier = []
        for node in frontier:
            for neighbor in g.successors(node):
                if neighbor not in hops:
                    hops[neighbor] = current_hop + 1
                    next_frontier.append(neighbor)
        frontier = next_frontier
        current_hop += 1

    return hops


def get_traced_path(g: nx.DiGraph, origin: str, target: str) -> Optional[List[str]]:
    try:
        return nx.shortest_path(g, source=origin.lower(), target=target.lower())
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def graph_to_json(g: nx.DiGraph, hops: Dict[str, int]) -> Dict[str, Any]:
    nodes = [
        {"id": node, "hop_distance": hops.get(node)}
        for node in g.nodes()
    ]
    edges = [
        {
            "from": u,
            "to": v,
            "value": data["value"],
            "asset": data.get("asset", "ETH"),
            "tx_count": data.get("tx_count", 1),
            "tx_hashes": data.get("tx_hashes", []),
        }
        for u, v, data in g.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges}