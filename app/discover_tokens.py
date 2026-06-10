from datetime import datetime, timezone
import json

from app.db import get_conn, json_dumps
from app.gmgn_client import trending


def ts_to_dt(value):
    if not value:
        return None
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def save_token(item):
    with get_conn() as conn:
        row = conn.execute(
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
                raw_discovery_json
            )
            VALUES (%s,%s,%s,%s,NOW(),%s,%s,%s,%s,%s)
            ON CONFLICT (token_address)
            DO UPDATE SET
                symbol = EXCLUDED.symbol,
                name = EXCLUDED.name,
                launchpad_platform = EXCLUDED.launchpad_platform,
                launchpad_status = EXCLUDED.launchpad_status
            RETURNING id
            """,
            (
                item.get("chain", "sol"),
                item.get("address"),
                item.get("symbol"),
                item.get("name"),
                ts_to_dt(item.get("creation_timestamp")),
                ts_to_dt(item.get("open_timestamp")),
                item.get("launchpad_platform"),
                str(item.get("launchpad_status")) if item.get("launchpad_status") is not None else None,
                json_dumps(item),
            ),
        ).fetchone()

        token_id = row["id"]

        conn.execute(
            """
            INSERT INTO token_snapshots (
                token_id,
                snapshot_at,
                snapshot_window,
                price_usd,
                market_cap,
                liquidity,
                holder_count,
                volume_1m,
                buys_1m,
                sells_1m,
                swaps_1m,
                smart_wallet_count,
                renowned_wallet_count,
                sniper_wallet_count,
                bundler_wallet_count,
                rat_trader_wallet_count,
                rug_ratio,
                is_wash_trading,
                top_10_holder_rate,
                creator_balance_rate,
                creator_token_status,
                rat_trader_amount_rate,
                bundler_trader_amount_rate,
                sniper_count,
                raw_info_json,
                raw_security_json
            )
            VALUES (%s,NOW(),'discovery',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                token_id,
                item.get("price"),
                item.get("market_cap"),
                item.get("liquidity"),
                item.get("holder_count"),
                item.get("volume"),
                item.get("buys"),
                item.get("sells"),
                item.get("swaps"),
                item.get("smart_degen_count"),
                item.get("renowned_count"),
                item.get("sniper_count"),
                item.get("bundler_wallets"),
                item.get("rat_trader_wallets"),
                item.get("rug_ratio"),
                item.get("is_wash_trading"),
                item.get("top_10_holder_rate"),
                item.get("creator_balance_rate"),
                item.get("creator_token_status"),
                item.get("rat_trader_amount_rate"),
                item.get("bundler_rate"),
                item.get("sniper_count"),
                json_dumps(item),
                json_dumps({}),
            ),
        )

        return token_id


def main():
    data = trending(limit=20)
    items = data.get("data", {}).get("rank", [])

    saved = 0
    for item in items:
        if not item.get("address"):
            continue
        save_token(item)
        saved += 1

    print(f"saved_tokens={saved}")


if __name__ == "__main__":
    main()
