from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars

from .pii import scrub_text

LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))


# REQ-NFR-04: Khởi tạo sẵn renderer tái sử dụng để tránh cấp phát bộ nhớ lặp đi lặp lại
_JSONL_RENDERER = structlog.processors.JSONRenderer(ensure_ascii=False)


class JsonlFileProcessor:
    def __call__(self, logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        parent = LOG_PATH.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        rendered = _JSONL_RENDERER(logger, method_name, event_dict)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(rendered + "\n")
        return event_dict



def scrub_event(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """REQ-NFR-01: Bộ lọc PII toàn diện xử lý đệ quy trên toàn bộ cấu trúc log record.
    
    Đảm bảo:
    - Loại bỏ PII trong tất cả các chuỗi (string values).
    - Loại bỏ PII nếu người dùng vô tình đưa dữ liệu nhạy cảm vào key của dictionary.
    - Duyệt đệ quy qua các cấu trúc lồng nhau: dict, list, tuple, set.
    """
    def scrub_value(value: Any) -> Any:
        if isinstance(value, str):
            return scrub_text(value)
        if isinstance(value, dict):
            return {
                (scrub_text(k) if isinstance(k, str) else k): scrub_value(item)
                for k, item in value.items()
            }
        if isinstance(value, set):
            return {scrub_value(item) for item in value}
        if isinstance(value, list):
            return [scrub_value(item) for item in value]
        if isinstance(value, tuple):
            return tuple(scrub_value(item) for item in value)
        return value

    return scrub_value(event_dict)



def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
            # REQ-NFR-01: format_exc_info và StackInfoRenderer phải chạy TRƯỚC scrub_event
            # để đảm bảo mọi traceback hoặc thông báo lỗi hệ thống có chứa dữ liệu nhạy cảm
            # đều được chuyển thành chuỗi và scrub sạch sẽ trước khi ghi log/render.
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            scrub_event,
            JsonlFileProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )



def get_logger() -> structlog.typing.FilteringBoundLogger:
    return structlog.get_logger()
