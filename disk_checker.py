import json
import shutil

def check_disk_usage(usage, warning_threshold=80, critical_threshold=90):
    if not (0 <= warning_threshold < critical_threshold <= 100):
        raise ValueError(
            "Thresholds must satisfy 0 <= warning < critical <= 100"
        )

    usage = float(usage)

    if usage < 0 or usage > 100:
        raise ValueError("Disk usage must be between 0 and 100")

    if usage >= critical_threshold:
        return "CRITICAL"

    if usage >= warning_threshold:
        return "WARNING"

    return "OK"

def load_config(filename):
    with open(filename, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    warning = config["warning_threshold"]
    critical = config["critical_threshold"]

    if not (0 <= warning < critical <= 100):
        raise ValueError(
            "Thresholds must satisfy 0 <= warning < critical <= 100"
        )

    if not config["paths"]:
        raise ValueError("paths must contain at least one path")

    return config

def format_report(results):
    lines = ["PATH | USED | STATUS | DETAIL"]

    for result in results:
        usage = result["usage"]
        used = "--" if usage is None else f"{usage:.1f}%"

        lines.append(
            f'{result["path"]} | {used} | '
            f'{result["status"]} | {result.get("detail", "")}'
        )

    return "\n".join(lines)

def check_all_filesystems(config):
    results = []

    for path in config["paths"]:
        try:
            disk = shutil.disk_usage(path)
            usage = disk.used / disk.total * 100

            status = check_disk_usage(
                usage,
                warning_threshold=config["warning_threshold"],
                critical_threshold=config["critical_threshold"]
            )

            results.append({
                "path": path,
                "usage": usage,
                "status": status
            })

        except OSError as error:
            results.append({
                "path": path,
                "usage": None,
                "status": "UNKNOWN",
                "detail": str(error)
            })

    return results

if __name__ == "__main__":
    config = load_config("config.json")
    results = check_all_filesystems(config)
    print(format_report(results))
    