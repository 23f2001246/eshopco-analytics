from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import numpy as np

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Load telemetry data
DATA_PATH = Path(__file__).parent.parent / "telemetry.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


@app.options("/")
def options():
    return Response(status_code=200)


@app.get("/")
def root():
    return {"message": "eShopCo Analytics API running"}


@app.post("/")
async def analytics(request: Request):
    req = await request.json()

    regions = req["regions"]
    threshold_ms = req["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(
                1 for r in rows
                if r["latency_ms"] > threshold_ms
            ),
        }

    return result
