from __future__ import annotations

import re
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


# REQ-NFR-04: Pre-compile regex pattern ở cấp module để tối ưu hóa hiệu năng,
# tránh re-compile trên mỗi request trong môi trường tải cao.
CORRELATION_ID_REGEX = re.compile(r"^req-[0-9a-fA-F]{8}$")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start each request with a clean context so concurrent requests cannot
        # inherit fields from a previous request.
        clear_contextvars()

        incoming_id = request.headers.get("x-request-id", "").strip()
        # Keep IDs opaque and non-PII by accepting only the lab's req-<8 hex>
        # format; otherwise generate a fresh ID.
        if CORRELATION_ID_REGEX.match(incoming_id):
            correlation_id = incoming_id
        else:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start) * 1000

            # Gán header phản hồi theo đúng chuẩn REQ-FR-01
            response.headers["x-request-id"] = correlation_id
            response.headers["x-response-time-ms"] = f"{elapsed_ms:.2f}"
            response.headers["x-response-time"] = f"{elapsed_ms:.2f}ms"
            return response
        finally:
            # Đảm bảo dọn dẹp contextvars sau khi request kết thúc, tránh rò rỉ sang request khác
            clear_contextvars()
