# Disk Usage Monitor

A Python command-line tool that checks disk usage for configured paths and reports OK, WARNING, CRITICAL, or UNKNOWN status.

## Features

- Configurable warning and critical thresholds.
- Checks multiple paths from a JSON configuration file.
- Reports unavailable paths as UNKNOWN with error details.
- Includes 22 automated pytest tests.

## Requirements

- Python 3
- pytest to run the tests

## Setup

```powershell
git clone https://github.com/joelavalleeteach/disk-usage-monitor.git
cd disk-usage-monitor
py -m pip install pytest
```

## Configuration

Edit `config.json` to set thresholds and paths:

```json
{
  "warning_threshold": 80,
  "critical_threshold": 90,
  "paths": [
    "C:/",
    "C:/this-path-does-not-exist"
  ]
}
```

The nonexistent path demonstrates error handling. Replace these paths with ones appropriate for your computer.

## Run the Monitor

```powershell
py disk_checker.py
```

Example output; usage values vary:

```text
PATH | USED | STATUS | DETAIL
C:/ | 77.6% | OK |
C:/this-path-does-not-exist | -- | UNKNOWN | [WinError 3] The system cannot find the path specified
```

## Run the Tests

```powershell
py -m pytest -q
```

The tests cover threshold boundaries, input validation, configuration loading, and monitoring behavior.

## Project Status

Developed and tested locally on Windows. All 22 automated tests also pass on Ubuntu with Python 3.13 through GitHub Actions. The workflow runs on pushes and pull requests. The supplied example configuration uses Windows paths.