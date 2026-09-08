"""
main.py
Wires etherscan_client + graph_engine together into /health and /api/analyze.
"""

import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import etherscan_client
import graph_engine
from graphsense import vasp_attribution

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title="CryptoAttrib AI - Backend",
    description="Wallet attribution & fund-flow tracing backend (SIH26182)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    wallet_address: str = Field(..., description="Wallet address to investigate")
    network: str = Field(default="ethereum", description="Blockchain network")
    max_hops: int = Field(default=3, ge=1, le=6, description="Max BFS hops to trace")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    if req.network.lower() != "ethereum":
        raise HTTPException(
            status_code=400,
            detail=f"Network '{req.network}' not supported yet. Use 'ethereum'.",
        )

    wallet = req.wallet_address.strip().lower()
    if not wallet.startswith("0x") or len(wallet) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format.")

    logger.info("Analyzing wallet=%s max_hops=%s", wallet, req.max_hops)

    transactions = etherscan_client.get_transactions(wallet)

    g = graph_engine.build_graph(wallet, transactions)
    hops = graph_engine.bfs_hop_trace(g, wallet, max_hops=req.max_hops)
    graph_json = graph_engine.graph_to_json(g, hops)

    traced_wallets = [w for w in hops.keys() if w != wallet]

    vasp_match = vasp_attribution.find_first_vasp_in_hops(hops, wallet)

    return {
        "wallet": wallet,
        "network": req.network,
        "max_hops": req.max_hops,
        "transactions": transactions,
        "traced_wallets": traced_wallets,
        "hop_distances": hops,
        "graph": graph_json,
        "vasp_match": vasp_match,
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
    }