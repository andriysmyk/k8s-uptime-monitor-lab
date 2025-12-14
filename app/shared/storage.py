import json
import uuid
from typing import List, Optional, Dict, Any
from redis import Redis
from .monitor import Monitor, MonitorCreate, CheckResult


# Keys:
# monitors:list -> set of monitor IDs
# monitors:{id} -> monitor json
# results:last:{id} -> last result json

class Storage:
    def __init__(self, redis_client: Redis):
        self.r = redis_client

    def add_monitor(self, data: MonitorCreate) -> Monitor:
        mid = str(uuid.uuid4())
        monitor = Monitor(id=mid, **data.model_dump())
        self.r.sadd("monitors:list", mid)
        self.r.set(f"monitors:{mid}", monitor.model_dump_json())
        return monitor

    def list_monitors(self) -> List[Monitor]:
        ids = sorted([x.decode("utf-8") for x in self.r.smembers("monitors:list")])
        out: List[Monitor] = []
        for mid in ids:
            raw = self.r.get(f"monitors:{mid}")
            if raw:
                out.append(Monitor.model_validate_json(raw))
        return out

    def get_monitor(self, mid: str) -> Optional[Monitor]:
        raw = self.r.get(f"monitors:{mid}")
        if not raw:
            return None
        return Monitor.model_validate_json(raw)

    def delete_monitor(self, mid: str) -> bool:
        removed = self.r.srem("monitors:list", mid)
        self.r.delete(f"monitors:{mid}")
        self.r.delete(f"results:last:{mid}")
        return bool(removed)

    def save_last_result(self, result: CheckResult) -> None:
        self.r.set(f"results:last:{result.monitor_id}", result.model_dump_json())

    def get_last_result(self, mid: str) -> Optional[CheckResult]:
        raw = self.r.get(f"results:last:{mid}")
        if not raw:
            return None
        return CheckResult.model_validate_json(raw)
