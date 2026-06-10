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


def extract_items(data):
    return (
        data.get("data", {}).get("list")
        or data.get("data", {}).get("rank")
        or data.get("data", [])
        or data.get("list", [])
        or []
    )


def main():
    tokens = get_recent_tokens(limit=20)
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
