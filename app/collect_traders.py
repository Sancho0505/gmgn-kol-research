from datetime import datetime, timezone

from app.db import get_conn, json_dumps
from app.gmgn_client import token_traders


SMART_TAGS = {"smart_degen", "smart_wallet"}
RENOWNED_TAGS = {"renowned"}
SNIPER_TAGS = {"sniper"}
BUNDLER_TAGS = {"bundler"}
RAT_TAGS = {"rat_trader"}
FRESH_TAGS = {"fresh_wallet"}


def ts_to_dt(value):
    if not value:
        return None
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def normalize_tags(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        return [value]
    return []


def has_any(tags, expected):
    return bool(set(tags) & expected)


def extract_wallet_address(item):
    return (
        item.get("address")
        or item.get("account_address")
        or item.get("wallet_address")
    )


def save_trader(token_id, rank, item):
    tags = normalize_tags(item.get("tags") or item.get("wallet_tag_v2"))
    maker_token_tags = normalize_tags(item.get("maker_token_tags"))
    all_tags = tags + maker_token_tags

    wallet_address = extract_wallet_address(item)
    if not wallet_address:
        return False

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO token_traders (
                token_id,
                observed_at,
                wallet_address,
                rank,
                tags,
                maker_token_tags,
                is_smart_wallet,
                is_renowned,
                is_sniper,
                is_bundler,
                is_rat_trader,
                is_fresh_wallet,
                buy_volume_cur,
                sell_volume_cur,
                buy_tx_count_cur,
                sell_tx_count_cur,
                amount_percentage,
                realized_profit,
                unrealized_profit,
                realized_pnl,
                unrealized_pnl,
                start_holding_at,
                last_active_timestamp,
                wallet_created_at,
                funding_source_address,
                raw_json
            )
            VALUES (
                %s,NOW(),%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s
            )
            """,
            (
                token_id,
                wallet_address,
                rank,
                tags,
                maker_token_tags,
                has_any(all_tags, SMART_TAGS),
                has_any(all_tags, RENOWNED_TAGS),
                has_any(all_tags, SNIPER_TAGS),
                has_any(all_tags, BUNDLER_TAGS),
                has_any(all_tags, RAT_TAGS),
                has_any(all_tags, FRESH_TAGS),
                item.get("buy_volume_cur"),
                item.get("sell_volume_cur"),
                item.get("buy_tx_count_cur"),
                item.get("sell_tx_count_cur"),
                item.get("amount_percentage"),
                item.get("realized_profit") or item.get("profit"),
                item.get("unrealized_profit"),
                item.get("realized_pnl"),
                item.get("unrealized_pnl"),
                ts_to_dt(item.get("start_holding_at")),
                ts_to_dt(item.get("last_active_timestamp")),
                ts_to_dt(item.get("created_at")),
                (
                    item.get("native_transfer", {}).get("address")
                    if isinstance(item.get("native_transfer"), dict)
                    else None
                ),
                json_dumps(item),
            ),
        )
        return True


def get_recent_tokens(limit=20):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id, token_address, symbol
            FROM tokens
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()


def main():
    tokens = get_recent_tokens(limit=20)

    total_saved = 0

    for token in tokens:
        print(f"collecting traders: {token['symbol']} {token['token_address']}")

        data = token_traders(token["token_address"], limit=20)

        items = (
            data.get("data", {}).get("list")
            or data.get("data", {}).get("rank")
            or data.get("data", [])
            or data.get("list", [])
            or []
        )

        saved = 0
        for idx, item in enumerate(items, start=1):
            if save_trader(token["id"], idx, item):
                saved += 1

        print(f"saved_traders={saved}")
        total_saved += saved

    print(f"total_saved_traders={total_saved}")


if __name__ == "__main__":
    main()
