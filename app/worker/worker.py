import os
import time
import httpx
from redis import Redis
from prometheus_client import Counter, Histogram, start_http_server
from shared.storage import Storage
from shared.monitor import CheckResult

WORKER_CHECKS = Counter("worker_checks_total", "Total URL checks performed", ["ok"])
WORKER_LATENCY = Histogram("worker_check_latency_seconds", "URL check latency seconds")
WORKER_ERRORS = Counter("worker_errors_total", "Worker errors total")

def get_redis() -> Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    password = os.getenv("REDIS_PASSWORD", None)
    return Redis(host=host, port=port, password=password, decode_responses=False)

def main():
    interval_default = int(os.getenv("WORKER_INTERVAL_DEFAULT", "15"))
    timeout_s = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5"))
    metrics_port = int(os.getenv("WORKER_METRICS_PORT", "9102"))

    # expose worker metrics on :9102/metrics
    start_http_server(metrics_port)

    r = get_redis()
    st = Storage(r)

    print("worker started")
    while True:
        try:
            monitors = st.list_monitors()
            if not monitors:
                time.sleep(interval_default)
                continue

            for m in monitors:
                # each monitor has its own interval; for MVP we still do loop,
                # but you can later improve scheduling.
                with WORKER_LATENCY.time():
                    t0 = time.time()
                    ok = False
                    status_code = None
                    latency_ms = None
                    err = None

                    try:
                        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
                            resp = client.get(str(m.url))
                            status_code = resp.status_code
                            ok = 200 <= resp.status_code < 400
                    except Exception as e:
                        err = str(e)

                    latency_ms = (time.time() - t0) * 1000.0

                    result = CheckResult(
                        monitor_id=m.id,
                        url=str(m.url),
                        ok=ok,
                        status_code=status_code,
                        latency_ms=latency_ms,
                        error=err,
                    )
                    st.save_last_result(result)
                    WORKER_CHECKS.labels(ok=str(ok).lower()).inc()

                # sleep a tiny bit to avoid hammering in a tight loop
                time.sleep(0.2)

            time.sleep(interval_default)
        except Exception as e:
            WORKER_ERRORS.inc()
            print(f"worker error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
