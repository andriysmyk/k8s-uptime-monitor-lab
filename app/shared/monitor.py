from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
import time


class MonitorCreate(BaseModel):
    url: HttpUrl
    interval_seconds: int = Field(default=30, ge=5, le=3600)
    tags: List[str] = Field(default_factory=list)


class Monitor(MonitorCreate):
    id: str
    created_at: float = Field(default_factory=lambda: time.time())


class CheckResult(BaseModel):
    monitor_id: str
    url: str
    ok: bool
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    checked_at: float = Field(default_factory=lambda: time.time())
    error: Optional[str] = None
