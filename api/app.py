from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Load telemetry CSV (put it in repo root)
df = pd.read_csv("q-colab-secrets-drive.csv")

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

class Query(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/latency")
def latency_metrics(query: Query):
    result = {}
    for region in query.regions:
        region_df = df[df["region"] == region]
        if region_df.empty:
            result[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue

        avg_latency = region_df["latency_ms"].mean()
        p95_latency = region_df["latency_ms"].quantile(0.95)
        avg_uptime = region_df["uptime"].mean()
        breaches = (region_df["latency_ms"] > query.threshold_ms).sum()

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": int(breaches)
        }
    return result
