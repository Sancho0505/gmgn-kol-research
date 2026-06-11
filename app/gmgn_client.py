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


def token_traders(address, limit=20):
    cmd = [
        "gmgn-cli",
        "token",
        "traders",
        "--chain",
        "sol",
        "--address",
        address,
        "--limit",
        str(limit),
        "--order-by",
        "buy_volume_cur",
        "--raw",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def token_traders_by_tag(address, tag, limit=20):
    cmd = [
        "gmgn-cli",
        "token",
        "traders",
        "--chain",
        "sol",
        "--address",
        address,
        "--limit",
        str(limit),
        "--tag",
        tag,
        "--order-by",
        "buy_volume_cur",
        "--raw",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def token_info(address):
    cmd = [
        "gmgn-cli",
        "token",
        "info",
        "--chain",
        "sol",
        "--address",
        address,
        "--raw",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)


def trenches(token_type="completed", limit=80):
    cmd = [
        "gmgn-cli",
        "market",
        "trenches",
        "--chain",
        "sol",
        "--type",
        token_type,
        "--limit",
        str(limit),
        "--sort-by",
        "created_timestamp",
        "--direction",
        "desc",
        "--raw",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return json.loads(result.stdout)
