from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _is_https(request: Request) -> bool:
    if request.url.scheme == "https":
        return True
    forwarded_proto = request.headers.get("x-forwarded-proto")
    return forwarded_proto == "https"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, enable_hsts: bool = True):
        super().__init__(app)
        self._enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        )
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
        response.headers.setdefault("X-XSS-Protection", "0")

        if self._enable_hsts and _is_https(request):
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        path = request.url.path
        if "/docs" not in path and "/redoc" not in path:
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
            )

        return response


@dataclass(frozen=True)
class RateLimitConfig:
    enabled: bool
    window_seconds: int
    max_requests: int


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        config: RateLimitConfig,
        exempt_paths: Tuple[str, ...] = (),
    ):
        super().__init__(app)
        self._config = config
        self._exempt_paths = exempt_paths
        self._events: Dict[Tuple[str, str], Deque[float]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._config.enabled:
            return await call_next(request)

        path = request.url.path
        for prefix in self._exempt_paths:
            if path.startswith(prefix):
                return await call_next(request)

        ip = _get_client_ip(request)
        key = (ip, path)
        now = time.monotonic()
        window_start = now - self._config.window_seconds

        async with self._lock:
            dq = self._events.get(key)
            if dq is None:
                dq = deque()
                self._events[key] = dq

            while dq and dq[0] < window_start:
                dq.popleft()

            if len(dq) >= self._config.max_requests:
                retry_after = max(1, int(dq[0] + self._config.window_seconds - now))
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": str(retry_after)},
                )

            dq.append(now)

        return await call_next(request)

