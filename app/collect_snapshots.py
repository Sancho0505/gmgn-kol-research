from app.db import get_conn, json_dumps
from app.gmgn_client import token_info


def get_tokens_for_snapshots(limit=250):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT
                t.id,
                t.token_address,
                t.symbol,
                MAX(ts.snapshot_at) AS last_snapshot_at
            FROM tokens t
            LEFT JOIN token_snapshots ts ON ts.token_id = t.id
            WHERE t.discovered_at >= NOW() - INTERVAL '12 hours'
            GROUP BY t.id, t.token_address, t.symbol
            HAVING
                MAX(ts.snapshot_at) IS NULL
                OR MAX(ts.snapshot_at) < NOW() - INTERVAL '15 minutes'
            ORDER BY
                MAX(ts.snapshot_at) NULLS FIRST,
                t.discovered_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()


def extract_payload(data):
    return data.get("data", data)


def save_snapshot(token_id, payload):
    price = payload.get("price") or {}
    stat = payload.get("stat") or {}
    wallet_tags = payload.get("wallet_tags_stat") or {}
    dev = payload.get("dev") or {}

    current_price = price.get("price") if isinstance(price, dict) else payload.get("price")

    with get_conn() as conn:
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
                volume_5m,
                volume_1h,

                buys_1m,
                sells_1m,
                buys_5m,
                sells_5m,

                swaps_1m,
                swaps_5m,

                smart_wallet_count,
                renowned_wallet_count,
                sniper_wallet_count,
                bundler_wallet_count,
                rat_trader_wallet_count,
                fresh_wallet_count,

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
            VALUES (
                %s,
                NOW(),
                'periodic',

                %s,%s,%s,%s,
                %s,%s,%s,
                %s,%s,%s,%s,
                %s,%s,
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s
            )
            """,
            (
                token_id,

                current_price,
                payload.get("market_cap") or payload.get("usd_market_cap"),
                payload.get("liquidity"),
                payload.get("holder_count") or stat.get("holder_count"),

                price.get("volume_1m"),
                price.get("volume_5m"),
                price.get("volume_1h"),

                price.get("buys_1m"),
                price.get("sells_1m"),
                price.get("buys_5m"),
                price.get("sells_5m"),

                price.get("swaps_1m"),
                price.get("swaps_5m"),

                wallet_tags.get("smart_wallets") or payload.get("smart_degen_count"),
                wallet_tags.get("renowned_wallets") or payload.get("renowned_count"),
                wallet_tags.get("sniper_wallets") or payload.get("sniper_count"),
                wallet_tags.get("bundler_wallets") or payload.get("bundler_count"),
                wallet_tags.get("rat_trader_wallets"),
                wallet_tags.get("fresh_wallets"),

                payload.get("rug_ratio") or stat.get("rug_ratio"),
                payload.get("is_wash_trading"),
                payload.get("top_10_holder_rate") or stat.get("top_10_holder_rate") or dev.get("top_10_holder_rate"),
                payload.get("creator_balance_rate") or stat.get("creator_hold_rate"),
                payload.get("creator_token_status") or dev.get("creator_token_status"),
                payload.get("rat_trader_amount_rate") or stat.get("top_rat_trader_percentage"),
                payload.get("bundler_trader_amount_rate") or stat.get("top_bundler_trader_percentage"),
                payload.get("sniper_count"),

                json_dumps(payload),
                json_dumps({}),
            ),
        )


def main():
    tokens = get_tokens_for_snapshots(limit=250)

    saved = 0
    skipped = 0

    for token in tokens:
        print(f"snapshot: {token['symbol']} {token['token_address']}")

        try:
            data = token_info(token["token_address"])
            payload = extract_payload(data)
            save_snapshot(token["id"], payload)
            saved += 1
        except Exception as e:
            print(f"ERROR snapshot {token['symbol']}: {e}")
            skipped += 1

    print(f"saved_snapshots={saved}")
    print(f"skipped_snapshots={skipped}")


if __name__ == "__main__":
    main()
