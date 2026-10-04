from __future__ import annotations


class UnexpectedPromptClient:
    def get_prompt(self, *args, **kwargs):
        raise AssertionError("Không được gọi Langfuse khi tracing bị tắt")


class FakeManagedPrompt:
    version = 7

    def compile(self, **variables: str) -> str:
        return (
            f"Feature={variables['feature']}\n"
            f"Docs={variables['docs']}\n"
            f"Question={variables['message']}"
        )


class RecordingPromptClient:
    def __init__(self) -> None:
        self.request: tuple[str, dict] | None = None
        self.prompt = FakeManagedPrompt()

    def get_prompt(self, name: str, **kwargs):
        self.request = (name, kwargs)
        return self.prompt


class FailingPromptClient:
    def get_prompt(self, *args, **kwargs):
        raise TimeoutError("Langfuse local is unavailable")


class FallbackManagedPrompt(FakeManagedPrompt):
    version = 0
    is_fallback = True


class FallbackReturningPromptClient:
    def get_prompt(self, *args, **kwargs):
        return FallbackManagedPrompt()


def test_local_prompt_fallback_keeps_lab_runnable_without_langfuse() -> None:
    from app.prompt_management import resolve_prompt

    resolved = resolve_prompt(
        UnexpectedPromptClient(),
        feature="qa",
        docs=["Refund within 7 days", "Proof of purchase is required"],
        message="What is the refund policy?",
        enabled=False,
    )

    assert resolved.source == "local"
    assert resolved.name == "day13-chat"
    assert resolved.label == "production"
    assert resolved.version == "local-v1"
    assert resolved.managed_prompt is None
    assert resolved.text == (
        "Feature=qa\n"
        "Docs=Refund within 7 days\nProof of purchase is required\n"
        "Question=What is the refund policy?"
    )


def test_langfuse_prompt_version_and_label_are_resolved(monkeypatch) -> None:
    from app.prompt_management import DEFAULT_PROMPT_TEMPLATE, resolve_prompt

    monkeypatch.setenv("LANGFUSE_PROMPT_NAME", "day13-incident-assistant")
    monkeypatch.setenv("LANGFUSE_PROMPT_LABEL", "candidate")
    client = RecordingPromptClient()

    resolved = resolve_prompt(
        client,
        feature="monitoring",
        docs=["Trace first", "Confirm with logs"],
        message="Where is the bottleneck?",
        enabled=True,
    )

    assert client.request == (
        "day13-incident-assistant",
        {
            "label": "candidate",
            "type": "text",
            "fallback": DEFAULT_PROMPT_TEMPLATE,
            "cache_ttl_seconds": 60,
            "fetch_timeout_seconds": 2,
            "max_retries": 0,
        },
    )
    assert resolved.source == "langfuse"
    assert resolved.version == "7"
    assert resolved.managed_prompt is client.prompt
    assert resolved.text == (
        "Feature=monitoring\n"
        "Docs=Trace first\nConfirm with logs\n"
        "Question=Where is the bottleneck?"
    )


def test_prompt_fetch_failure_uses_visible_local_fallback() -> None:
    from app.prompt_management import resolve_prompt

    resolved = resolve_prompt(
        FailingPromptClient(),
        feature="qa",
        docs=["Trace first"],
        message="What happened?",
        enabled=True,
    )

    assert resolved.source == "local-fallback"
    assert resolved.version == "local-v1"
    assert resolved.fetch_error == "TimeoutError"
    assert resolved.managed_prompt is None
    assert resolved.text == "Feature=qa\nDocs=Trace first\nQuestion=What happened?"


def test_sdk_fallback_is_not_reported_as_managed_prompt() -> None:
    from app.prompt_management import resolve_prompt

    resolved = resolve_prompt(
        FallbackReturningPromptClient(),
        feature="qa",
        docs=["Trace first"],
        message="What happened?",
        enabled=True,
    )

    assert resolved.source == "local-fallback"
    assert resolved.version == "local-v1"
    assert resolved.fetch_error == "LangfuseFallback"
    assert resolved.managed_prompt is None


def test_prompt_label_switching_and_rollback(monkeypatch) -> None:
    """Kiểm tra REQ-FR-05: Chuyển đổi nhãn phiên bản prompt và kịch bản Rollback."""
    from app.prompt_management import resolve_prompt

    class DynamicVersionPromptClient:
        def __init__(self) -> None:
            self.labels_to_version = {"baseline": 1, "candidate": 2, "production": 1}

        def get_prompt(self, name: str, **kwargs):
            label = kwargs.get("label", "production")
            ver = self.labels_to_version[label]
            prompt = FakeManagedPrompt()
            prompt.version = ver
            return prompt

    client = DynamicVersionPromptClient()

    # 1. Baseline -> Version 1
    monkeypatch.setenv("LANGFUSE_PROMPT_LABEL", "baseline")
    res_base = resolve_prompt(client, feature="qa", docs=["doc1"], message="msg", enabled=True)
    assert res_base.version == "1"
    assert res_base.label == "baseline"

    # 2. Candidate -> Version 2
    monkeypatch.setenv("LANGFUSE_PROMPT_LABEL", "candidate")
    res_cand = resolve_prompt(client, feature="qa", docs=["doc1"], message="msg", enabled=True)
    assert res_cand.version == "2"
    assert res_cand.label == "candidate"

    # 3. Promote production to Version 2
    client.labels_to_version["production"] = 2
    monkeypatch.setenv("LANGFUSE_PROMPT_LABEL", "production")
    res_prod_v2 = resolve_prompt(client, feature="qa", docs=["doc1"], message="msg", enabled=True)
    assert res_prod_v2.version == "2"

    # 4. Rollback production back to Version 1
    client.labels_to_version["production"] = 1
    res_prod_v1 = resolve_prompt(client, feature="qa", docs=["doc1"], message="msg", enabled=True)
    assert res_prod_v1.version == "1"
    assert res_prod_v1.source == "langfuse"
