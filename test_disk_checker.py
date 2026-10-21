import pytest

from disk_checker import (
    check_disk_usage,
    load_config,
    format_report,
    check_all_filesystems
)


def test_load_config_reads_settings(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"warning_threshold": 80, "critical_threshold": 90, '
        '"paths": ["/tmp"]}',
        encoding="utf-8"
    )

    config = load_config(config_file)

    assert config["warning_threshold"] == 80
    assert config["critical_threshold"] == 90
    assert config["paths"] == ["/tmp"]


def test_usage_0_is_ok():
    assert check_disk_usage(0) == "OK"


def test_usage_79_is_ok():
    assert check_disk_usage(79) == "OK"


def test_usage_79point9_is_ok():
    assert check_disk_usage(79.9) == "OK"


def test_usage_80_is_warning():
    assert check_disk_usage(80) == "WARNING"


def test_usage_89_is_warning():
    assert check_disk_usage(89) == "WARNING"


def test_usage_89point9_is_warning():
    assert check_disk_usage(89.9) == "WARNING"


def test_usage_90_is_critical():
    assert check_disk_usage(90) == "CRITICAL"


def test_usage_100_is_critical():
    assert check_disk_usage(100) == "CRITICAL"


def test_numeric_text_is_accepted():
    assert check_disk_usage("85") == "WARNING"


def test_usage_above_100_raises_error():
    with pytest.raises(ValueError):
        check_disk_usage(101)

def test_usage_below_0_raises_error():
    with pytest.raises(ValueError):
        check_disk_usage(-1)


def test_nonnumeric_text_raises_error():
    with pytest.raises(ValueError):
        check_disk_usage("unknown")

def test_custom_thresholds_are_used():
    assert check_disk_usage(
        85, warning_threshold=70, critical_threshold=80
    ) == "CRITICAL"

def test_reversed_thresholds_raise_error():
    with pytest.raises(ValueError):
        check_disk_usage(
            85, warning_threshold=90, critical_threshold=80
        )

def test_equal_thresholds_raise_error():
    with pytest.raises(ValueError):
        check_disk_usage(
            85, warning_threshold=80, critical_threshold=80
        )


def test_critical_threshold_above_100_raises_error():
    with pytest.raises(ValueError):
        check_disk_usage(
            85, warning_threshold=80, critical_threshold=101
        )

def test_load_config_missing_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_config(missing_file)

def test_load_config_rejects_reversed_thresholds(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"warning_threshold": 90, "critical_threshold": 80, '
        '"paths": ["/tmp"]}',
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        load_config(config_file)

def test_load_config_rejects_empty_paths(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"warning_threshold": 80, "critical_threshold": 90, '
        '"paths": []}',
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="paths"):
        load_config(config_file)

def test_format_report_shows_success_and_failure():
    results = [
        {"path": "/tmp", "usage": 85, "status": "WARNING"},
        {
            "path": "/missing",
            "usage": None,
            "status": "UNKNOWN",
            "detail": "Path not found"
        }
    ]

    report = format_report(results)

    assert "/tmp | 85.0% | WARNING" in report
    assert "/missing | -- | UNKNOWN | Path not found" in report

def test_failed_path_does_not_stop_remaining_checks(tmp_path):
    config = {
        "warning_threshold": 80,
        "critical_threshold": 90,
        "paths": [
            str(tmp_path / "missing"),
            str(tmp_path)
        ]
    }

    results = check_all_filesystems(config)

    assert len(results) == 2

    assert results[0]["status"] == "UNKNOWN"
    assert results[0]["usage"] is None
    assert results[0]["detail"]

    assert results[1]["status"] in ("OK", "WARNING", "CRITICAL")
    assert 0 <= results[1]["usage"] <= 100
