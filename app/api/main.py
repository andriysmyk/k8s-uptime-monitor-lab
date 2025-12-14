import os
from fastapi import FastAPI, HTTPException
from redis import Redis
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from shared.storage import Storage
from shared.monitor import MonitorCreate

APP_NAME = "uptime-monitor-api"

# Prometheus metrics
REQUESTS = Counter("api_requests_total", "Total API requests", ["path", "method"])
LATENCY = Histogram("api_request_latency_seconds", "API request latency seconds", ["path"])

def get_redis() -> Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    password = os.getenv("REDIS_PASSWORD", None)
    return Redis(host=host, port=port, password=password, decode_responses=False)

app = FastAPI(title=APP_NAME)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    path = request.url.path
    method = request.method
    REQUESTS.labels(path=path, method=method).inc()
    with LATENCY.labels(path=path).time():
        return await call_next(request)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    try:
        r = get_redis()
        r.ping()
        return {"ready": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"redis not ready: {e}")

@app.post("/monitors")
def create_monitor(payload: MonitorCreate):
    st = Storage(get_redis())
    m = st.add_monitor(payload)
    return m.model_dump()

@app.get("/monitors")
def list_monitors():
    st = Storage(get_redis())
    items = [m.model_dump() for m in st.list_monitors()]
    return {"items": items}

@app.get("/monitors/{monitor_id}")
def get_monitor(monitor_id: str):
    st = Storage(get_redis())
    m = st.get_monitor(monitor_id)
    if not m:
        raise HTTPException(status_code=404, detail="monitor not found")
    last = st.get_last_result(monitor_id)
    return {"monitor": m.model_dump(), "last_result": last.model_dump() if last else None}

@app.delete("/monitors/{monitor_id}")
def delete_monitor(monitor_id: str):
    st = Storage(get_redis())
    ok = st.delete_monitor(monitor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="monitor not found")
    return {"deleted": True}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
