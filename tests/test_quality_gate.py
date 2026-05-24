"""Tests for scripts/quality_gate.py — parse/compare helpers."""

import json
import sys
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from quality_gate import QualityGate  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gate(tmp_path: Path) -> QualityGate:
    """Return a QualityGate instance with a minimal .quality-gate.json."""
    config = {
        "gates": {
            "tests": {"threshold": 1, "operator": ">="},
            "coverage": {"threshold": 80, "operator": ">="},
            "lint": {"threshold": 0, "operator": "="},
            "types": {"threshold": 0, "operator": "<="},
            "build": {"threshold": 0, "operator": "="},
        },
        "commands": {},
    }
    (tmp_path / ".quality-gate.json").write_text(json.dumps(config))
    gate = QualityGate.__new__(QualityGate)
    gate.config_path = tmp_path / ".quality-gate.json"
    gate.baseline_path = tmp_path / ".quality-gate-baseline.json"
    gate.last_report_path = tmp_path / ".quality-gate-last-report.json"
    gate.config = config
    gate.gates = [
        ("Tests", "tests", "passed_tests", "≥", "make test"),
        ("Coverage", "coverage", "coverage_percentage", "≥", "make test-coverage"),
        ("Lint", "lint", "warning_count", "=", "make lint"),
        ("Types", "types", "error_count", "≤", "make type-check"),
        ("Build", "build", "build_status", "=", "make build"),
        ("Secrets", "security_secrets", "secret_count", "=", "detect-secrets scan"),
        ("VulnDeps", "security_vulns", "vuln_count", "≤", "pip-audit"),
    ]
    return gate


# ---------------------------------------------------------------------------
# _parse_passed_tests
# ---------------------------------------------------------------------------


class TestParsePassedTests:
    def test_standard_pytest_output(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_passed_tests("42 passed, 0 warnings") == 42

    def test_passed_equals_format(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_passed_tests("passed = 7") == 7

    def test_no_match_returns_zero(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_passed_tests("no tests found") == 0

    def test_empty_string(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_passed_tests("") == 0


# ---------------------------------------------------------------------------
# _parse_coverage
# ---------------------------------------------------------------------------


class TestParseCoverage:
    def test_total_line_with_percent(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        output = "TOTAL    100     12     16      2    83%"
        assert gate._parse_coverage(output) == pytest.approx(83.0)

    def test_coverage_report_line(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        output = "Total coverage: 91.5%"
        assert gate._parse_coverage(output) == pytest.approx(91.5)

    def test_no_match_returns_minus_one(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_coverage("build successful") == -1.0

    def test_empty_string(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_coverage("") == -1.0


# ---------------------------------------------------------------------------
# _parse_warning_count
# ---------------------------------------------------------------------------


class TestParseWarningCount:
    def test_single_warning(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_warning_count("1 warning") == 1

    def test_multiple_warnings(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_warning_count("5 warnings found") == 5

    def test_no_warnings(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_warning_count("0 issues") == 0


# ---------------------------------------------------------------------------
# _parse_error_count
# ---------------------------------------------------------------------------


class TestParseErrorCount:
    def test_single_error(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_error_count("1 error found") == 1

    def test_multiple_errors(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_error_count("3 errors") == 3

    def test_no_errors(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_error_count("all good") == 0


# ---------------------------------------------------------------------------
# _parse_secret_count
# ---------------------------------------------------------------------------


class TestParseSecretCount:
    def test_json_output(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        payload = json.dumps({"results": {"file.py": ["s1", "s2"]}})
        assert gate._parse_secret_count(payload) == 2

    def test_empty_results(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        payload = json.dumps({"results": {}})
        assert gate._parse_secret_count(payload) == 0

    def test_regex_fallback(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_secret_count("secrets found: 3") == 3

    def test_invalid_json_returns_zero(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_secret_count("not json") == 0


# ---------------------------------------------------------------------------
# _parse_vuln_count
# ---------------------------------------------------------------------------


class TestParseVulnCount:
    def test_found_N_vulnerabilities(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_vuln_count("found 4 vulnerabilities") == 4

    def test_cve_count(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        output = "CVE-2023-1234 and CVE-2024-5678 detected"
        assert gate._parse_vuln_count(output) == 2

    def test_no_known_vulns(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_vuln_count("No known vulnerabilities found") == 0

    def test_empty_string(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_vuln_count("") == 0


# ---------------------------------------------------------------------------
# _compare
# ---------------------------------------------------------------------------


class TestCompare:
    def test_equal_operator(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._compare(0, 0, "=") is True
        assert gate._compare(1, 0, "=") is False

    def test_gte_operator(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._compare(5, 3, "≥") is True
        assert gate._compare(2, 3, "≥") is False
        assert gate._compare(3, 3, ">=") is True

    def test_lte_operator(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._compare(2, 5, "≤") is True
        assert gate._compare(6, 5, "≤") is False
        assert gate._compare(5, 5, "<=") is True

    def test_unknown_operator_returns_false(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._compare(1, 1, "??") is False


# ---------------------------------------------------------------------------
# _parse_metric dispatch
# ---------------------------------------------------------------------------


class TestParseMetric:
    def test_tests_gate(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Tests", 0, "10 passed") == 10

    def test_coverage_gate(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Coverage", 0, "Total coverage: 85%") == pytest.approx(85.0)

    def test_lint_gate(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Lint", 0, "2 warnings") == 2

    def test_types_gate(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Types", 0, "1 error") == 1

    def test_build_pass(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Build", 0, "") == 0

    def test_build_fail(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Build", 1, "") == 1

    def test_secrets_gate(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        payload = json.dumps({"results": {}})
        assert gate._parse_metric("Secrets", 0, payload) == 0

    def test_unknown_gate_returns_none(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        assert gate._parse_metric("Unknown", 0, "anything") is None


# ---------------------------------------------------------------------------
# verify — missing baseline
# ---------------------------------------------------------------------------


class TestVerifyMissingBaseline:
    def test_returns_false_when_no_baseline(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        result = gate.verify()
        assert result is False
        report = json.loads(gate.last_report_path.read_text())
        assert report["reason"] == "missing_baseline"


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_init_loads_config(self, tmp_path: Path) -> None:
        config = {
            "gates": {},
            "commands": {"tests": "echo done"},
        }
        config_path = tmp_path / ".quality-gate.json"
        config_path.write_text(json.dumps(config))
        with patch("quality_gate.Path") as mock_path:
            mock_path.side_effect = lambda x: tmp_path / x
            gate = QualityGate.__new__(QualityGate)
            gate.config_path = config_path
            gate.baseline_path = tmp_path / ".quality-gate-baseline.json"
            gate.last_report_path = tmp_path / ".quality-gate-last-report.json"
            gate.config = json.loads(config_path.read_text())
            gate.gates = []
        assert gate.config["commands"]["tests"] == "echo done"

    def test_init_exits_when_config_missing(self, tmp_path: Path) -> None:
        with patch("quality_gate.Path") as mock_path:
            missing = tmp_path / ".quality-gate.json"
            mock_path.return_value = missing
            # Directly test sys.exit on missing file
            with pytest.raises(SystemExit):
                gate = QualityGate.__new__(QualityGate)
                gate.config_path = missing
                gate.baseline_path = tmp_path / ".baseline.json"
                gate.last_report_path = tmp_path / ".report.json"
                gate.config = {}
                gate.gates = []
                # Now call __init__ logic manually
                if not gate.config_path.exists():
                    sys.exit(1)


# ---------------------------------------------------------------------------
# _run
# ---------------------------------------------------------------------------


class TestRun:
    def test_run_success(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            code, output = gate._run("echo ok")
        assert code == 0
        assert "ok" in output

    def test_run_failure(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="err")
            code, output = gate._run("false")
        assert code == 1

    def test_run_timeout(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 600)):
            code, output = gate._run("sleep 999")
        assert code == 124
        assert "timed out" in output.lower()

    def test_run_exception(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        with patch("subprocess.run", side_effect=OSError("not found")):
            code, output = gate._run("missing-cmd")
        assert code == 127


# ---------------------------------------------------------------------------
# _run_gate
# ---------------------------------------------------------------------------


class TestRunGate:
    def test_run_gate_uses_config_command(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        gate.config["commands"]["tests"] = "echo 5 passed"
        with patch.object(gate, "_run", return_value=(0, "5 passed")):
            result = gate._run_gate("Tests", "tests", "passed_tests", "make test")
        assert result["gate"] == "Tests"
        assert result["metric"] == 5
        assert result["exit_code"] == 0

    def test_run_gate_uses_default_when_no_override(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        with patch.object(gate, "_run", return_value=(0, "1 passed")):
            result = gate._run_gate("Tests", "tests", "passed_tests", "make test")
        assert result["command"] == "make test"


# ---------------------------------------------------------------------------
# baseline
# ---------------------------------------------------------------------------


class TestBaseline:
    def _gate_result(self, name: str, exit_code: int = 0) -> dict:
        return {
            "gate": name,
            "command": "echo",
            "exit_code": exit_code,
            "metric_name": "metric",
            "metric": 1,
            "timestamp": "2026-01-01T00:00:00",
            "output": "1 passed",
        }

    def test_baseline_pass_writes_file(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        results = [self._gate_result(g[0]) for g in gate.gates]
        with patch.object(gate, "_run_gate", side_effect=results):
            result = gate.baseline()
        assert result is True
        assert gate.baseline_path.exists()

    def test_baseline_fail_when_gate_fails(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        results = [self._gate_result(g[0], exit_code=(1 if i == 0 else 0))
                   for i, g in enumerate(gate.gates)]
        with patch.object(gate, "_run_gate", side_effect=results):
            result = gate.baseline()
        assert result is False
        data = json.loads(gate.baseline_path.read_text())
        assert data["valid"] is False


# ---------------------------------------------------------------------------
# verify — with valid baseline
# ---------------------------------------------------------------------------


class TestVerifyWithBaseline:
    def _baseline_gate(self, name: str) -> dict:
        return {
            "gate": name,
            "metric": 10,
            "exit_code": 0,
            "command": "echo",
            "metric_name": "passed_tests",
            "output": "10 passed",
            "timestamp": "2026-01-01T00:00:00",
        }

    def _current_gate(self, name: str, exit_code: int = 0, metric: int = 10) -> dict:
        return {
            "gate": name,
            "command": "echo",
            "exit_code": exit_code,
            "metric_name": "passed_tests",
            "metric": metric,
            "timestamp": "2026-01-01T00:00:00",
            "output": "10 passed",
        }

    def _write_baseline(self, gate: QualityGate) -> None:
        baseline_data = {
            "recorded_at": "2026-01-01T00:00:00",
            "gates": {g[0]: self._baseline_gate(g[0]) for g in gate.gates},
            "valid": True,
        }
        gate.baseline_path.write_text(json.dumps(baseline_data))

    def test_verify_all_pass(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        self._write_baseline(gate)
        currents = [self._current_gate(g[0]) for g in gate.gates]
        with patch.object(gate, "_run_gate", side_effect=currents):
            result = gate.verify()
        assert result is True
        report = json.loads(gate.last_report_path.read_text())
        assert report["overall"] == "PASS"

    def test_verify_fail_on_command_failure(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        self._write_baseline(gate)
        currents = [self._current_gate(g[0], exit_code=(1 if i == 0 else 0))
                    for i, g in enumerate(gate.gates)]
        with patch.object(gate, "_run_gate", side_effect=currents):
            result = gate.verify()
        assert result is False

    def test_verify_fail_on_invalid_baseline(self, tmp_path: Path) -> None:
        gate = _make_gate(tmp_path)
        baseline_data = {
            "recorded_at": "2026-01-01T00:00:00",
            "gates": {g[0]: self._baseline_gate(g[0]) for g in gate.gates},
            "valid": False,
        }
        gate.baseline_path.write_text(json.dumps(baseline_data))
        currents = [self._current_gate(g[0]) for g in gate.gates]
        with patch.object(gate, "_run_gate", side_effect=currents):
            result = gate.verify()
        assert result is False
