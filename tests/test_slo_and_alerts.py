from __future__ import annotations

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_slo_config_structure():
    """Kiểm tra REQ-FR-07: Cấu hình SLO và công thức tính Error Budget tại config/slo.yaml."""
    slo_path = REPO_ROOT / "config" / "slo.yaml"
    assert slo_path.exists(), "File config/slo.yaml phải tồn tại"

    data = yaml.safe_load(slo_path.read_text(encoding="utf-8"))
    assert "primary_slo" in data
    slo = data["primary_slo"]
    assert slo["target_percent"] == 99.5
    assert slo["error_budget_percent"] == 0.5
    assert "calculation" in slo["error_budget"]
    assert slo["error_budget"]["example_10000_requests"] == 50

    # Kiểm tra guardrails
    assert "guardrails" in data
    assert data["guardrails"]["error_rate_pct_max"] == 2
    assert data["guardrails"]["retrieval_success_rate_pct_min"] == 90


def test_alert_rules_structure_and_runbooks():
    """Kiểm tra REQ-FR-07: Thiết lập 3 Alert rules symptom-based và runbooks đi kèm."""
    alerts_path = REPO_ROOT / "config" / "alert_rules.yaml"
    assert alerts_path.exists(), "File config/alert_rules.yaml phải tồn tại"

    data = yaml.safe_load(alerts_path.read_text(encoding="utf-8"))
    assert "alerts" in data
    alerts = data["alerts"]
    assert len(alerts) == 3, "Phải có đúng 3 alert rules theo yêu cầu"

    runbook_path = REPO_ROOT / "docs" / "alerts.md"
    assert runbook_path.exists(), "File docs/alerts.md phải tồn tại"
    runbook_content = runbook_path.read_text(encoding="utf-8")

    required_fields = {"name", "severity", "condition", "duration", "type", "channel", "destination", "owner", "runbook"}
    for alert in alerts:
        assert required_fields.issubset(alert.keys()), f"Alert {alert.get('name')} thiếu trường bắt buộc"
        assert alert["type"] == "symptom-based"
        assert alert["channel"] == "slack"
        assert alert["destination"] == "#llmops-alerts"
        assert alert["severity"] in {"warning", "critical"}
        assert alert["duration"] in {"5m", "10m"}

        # Xác thực liên kết runbook
        assert "docs/alerts.md#" in alert["runbook"]
        anchor = alert["runbook"].split("#")[-1]
        assert f"## Alert" in runbook_content
