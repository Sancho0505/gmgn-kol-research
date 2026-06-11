from datetime import datetime, timezone

from app.db import get_conn, json_dumps
from app.gmgn_client import trenches


TRENCH_TYPES = [
    "new_creation",
    "near_completion",
    "completed",
]


def ts_to_dt(value):
    if not value:
        return None
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def get_items(payload, token_type):
    items = payload.get(token_type) or []

    if token_type == "near_completion" and not items:
        items = payload.get("pump") or []

    return items


def save_token(item, source):
    address = item.get("address")
    if not address:
        return False

    created_at = ts_to_dt(
        item.get("created_timestamp")
        or item.get("open_timestamp")
        or item.get("complete_timestamp")
    )

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO tokens (
                chain,
                token_address,
                symbol,
                name,
                discovered_at,
                creation_timestamp,
                open_timestamp,
                launchpad_platform,
                launchpad_status,
                raw_discovery_json,
                discovery_source,
                raw_trenches_json
            )
            VALUES (%s,%s,%s,%s,NOW(),%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (token_address)
            DO UPDATE SET
                symbol = COALESCE(EXCLUDED.symbol, tokens.symbol),
                name = COALESCE(EXCLUDED.name, tokens.name),
                launchpad_platform = COALESCE(EXCLUDED.launchpad_platform, tokens.launchpad_platform),
                discovery_source = COALESCE(tokens.discovery_source, EXCLUDED.discovery_source),
                raw_trenches_json = EXCLUDED.raw_trenches_json
            """,
            (
                item.get("chain") or "sol",
                address,
                item.get("symbol"),
                item.get("name"),
                created_at,
                ts_to_dt(item.get("open_timestamp")),
                item.get("launchpad_platform") or item.get("launchpad"),
                str(item.get("status")) if item.get("status") is not None else None,
                json_dumps(item),
                source,
                json_dumps(item),
            ),
        )

    return True


def main():
    total_saved = 0

    for token_type in TRENCH_TYPES:
        print(f"collecting trenches: {token_type}")

        payload = trenches(token_type=token_type, limit=80)
        items = get_items(payload, token_type)

        saved = 0
        for item in items:
            if save_token(item, f"trenches_{token_type}"):
                saved += 1

        total_saved += saved
        print(f"saved_{token_type}={saved}")

    print(f"total_saved_trenches={total_saved}")


if __name__ == "__main__":
    main()
