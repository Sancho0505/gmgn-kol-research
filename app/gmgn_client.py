import json
import subprocess


def trending(limit=10):
    cmd = [
        "gmgn-cli",
        "market",
        "trending",
        "--chain",
        "sol",
        "--interval",
        "1m",
        "--limit",
        str(limit),
        "--raw",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)
