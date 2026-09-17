"""In-memory sliding-window rate limiter middleware / helper for API security."""
from __future__ import annotations

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status


class RateLimiter:
    """Sliding-window rate limiter."""

    def __init__(self, requests_per_minute: int = 60, window_seconds: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.history: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, max_requests: int | None = None) -> None:
        limit = max_requests if max_requests is not None else self.requests_per_minute
        now = time.time()
        cutoff = now - self.window_seconds
        timestamps = [t for t in self.history[key] if t > cutoff]
        self.history[key] = timestamps

        if len(timestamps) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: maximum {limit} requests per {self.window_seconds}s",
            )
        self.history[key].append(now)


# Global instances for sensitive endpoint categories
auth_limiter = RateLimiter(requests_per_minute=20)
cbt_limiter = RateLimiter(requests_per_minute=120)
admin_limiter = RateLimiter(requests_per_minute=300)


def limit_request(request: Request, max_requests: int = 30):
    client_ip = request.client.host if request.client else "127.0.0.1"
    endpoint = request.url.path
    key = f"{client_ip}:{endpoint}"
    cbt_limiter.check(key, max_requests=max_requests)
