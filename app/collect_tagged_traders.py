from app.collect_traders import save_trader
from app.db import get_conn
from app.gmgn_client import token_traders_by_tag


TAGS_TO_COLLECT = [
    "smart_degen",
    "renowned",
    "sniper",
    "bundler",
    "rat_trader",
    "fresh_wallet",
]


def get_tokens_for_tagged_traders(limit=20):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT
                t.id,
                t.token_address,
                t.symbol,
                COUNT(tt.id) FILTER (
                    WHERE tt.is_smart_wallet = true
                       OR tt.is_renowned = true
                       OR tt.is_sniper = true
                       OR tt.is_bundler = true
                       OR tt.is_rat_trader = true
                       OR tt.is_fresh_wallet = true
                ) AS tagged_rows,
                MAX(tt.observed_at) AS last_tagged_at
            FROM tokens t
            LEFT JOIN token_traders tt ON tt.token_id = t.id
            WHERE t.discovered_at >= NOW() - INTERVAL '12 hours'
            GROUP BY t.id, t.token_address, t.symbol
            HAVING
                COUNT(tt.id) FILTER (
                    WHERE tt.is_smart_wallet = true
                       OR tt.is_renowned = true
                       OR tt.is_sniper = true
                       OR tt.is_bundler = true
                       OR tt.is_rat_trader = true
                       OR tt.is_fresh_wallet = true
                ) = 0
                OR MAX(tt.observed_at) < NOW() - INTERVAL '30 minutes'
            ORDER BY
                tagged_rows ASC,
                MAX(tt.observed_at) NULLS FIRST,
                t.discovered_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()


def extract_items(data):
    return (
        data.get("data", {}).get("list")
        or data.get("data", {}).get("rank")
        or data.get("data", [])
        or data.get("list", [])
        or []
    )


def main():
    tokens = get_tokens_for_tagged_traders(limit=20)
    total_saved = 0

    for token in tokens:
        for tag in TAGS_TO_COLLECT:
            print(f"collecting {tag}: {token['symbol']} {token['token_address']}")
            try:
                data = token_traders_by_tag(token["token_address"], tag=tag, limit=20)
            except Exception as e:
                print(f"ERROR {tag} {token['symbol']}: {e}")
                continue

            items = extract_items(data)
            saved = 0

            for idx, item in enumerate(items, start=1):
                item["maker_token_tags"] = list(
                    set(item.get("maker_token_tags") or []) | {tag}
                )

                if save_trader(token["id"], idx, item):
                    saved += 1

            print(f"saved_{tag}={saved}")
            total_saved += saved

    print(f"total_saved_tagged_traders={total_saved}")


if __name__ == "__main__":
    main()
