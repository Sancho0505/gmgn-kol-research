from decimal import Decimal, InvalidOperation

from app.db import get_conn
from app.gmgn_client import token_info


def to_decimal(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def extract_price(data):
    payload = data.get("data", data)
    price = payload.get("price")

    if isinstance(price, dict):
        return to_decimal(price.get("price"))

    return to_decimal(price)


def get_eligible_tokens(limit=50):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT
                t.id,
                t.token_address,
                t.symbol,
                t.discovered_at,
                ts.price_usd AS base_price_usd,
                o.price_24h,
                o.price_72h
            FROM tokens t
            JOIN LATERAL (
                SELECT price_usd
                FROM token_snapshots
                WHERE token_id = t.id
                ORDER BY snapshot_at ASC
                LIMIT 1
            ) ts ON true
            LEFT JOIN token_outcomes o ON o.token_id = t.id
            WHERE ts.price_usd IS NOT NULL
            ORDER BY t.id DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()


def upsert_24h(token_id, base_price, current_price):
    if base_price is None or current_price is None or base_price == 0:
        return False

    roi = (current_price / base_price) - Decimal("1")

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO token_outcomes (
                token_id,
                base_price_usd,
                price_24h,
                roi_24h,
                winner_24h
            )
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (token_id)
            DO UPDATE SET
                base_price_usd = EXCLUDED.base_price_usd,
                price_24h = EXCLUDED.price_24h,
                roi_24h = EXCLUDED.roi_24h,
                winner_24h = EXCLUDED.winner_24h
            """,
            (
                token_id,
                base_price,
                current_price,
                roi,
                roi >= Decimal("3"),
            ),
        )
    return True


def upsert_72h(token_id, base_price, current_price):
    if base_price is None or current_price is None or base_price == 0:
        return False

    roi = (current_price / base_price) - Decimal("1")

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO token_outcomes (
                token_id,
                base_price_usd,
                price_72h,
                roi_72h,
                winner_72h,
                completed_at
            )
            VALUES (%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (token_id)
            DO UPDATE SET
                base_price_usd = EXCLUDED.base_price_usd,
                price_72h = EXCLUDED.price_72h,
                roi_72h = EXCLUDED.roi_72h,
                winner_72h = EXCLUDED.winner_72h,
                completed_at = NOW()
            """,
            (
                token_id,
                base_price,
                current_price,
                roi,
                roi >= Decimal("5"),
            ),
        )
    return True


def main():
    tokens = get_eligible_tokens(limit=50)

    saved_24h = 0
    saved_72h = 0
    skipped = 0

    for token in tokens:
        base_price = to_decimal(token["base_price_usd"])

        try:
            data = token_info(token["token_address"])
        except Exception as e:
            print(f"ERROR token_info {token['symbol']}: {e}")
            skipped += 1
            continue

        current_price = extract_price(data)

        if current_price is None:
            skipped += 1
            continue

        # Dev/test mode: fills both fields immediately.
        # Later we will gate this by discovered_at + 24h / +72h.
        if token["price_24h"] is None:
            if upsert_24h(token["id"], base_price, current_price):
                saved_24h += 1

        if token["price_72h"] is None:
            if upsert_72h(token["id"], base_price, current_price):
                saved_72h += 1

    print(f"saved_24h={saved_24h}")
    print(f"saved_72h={saved_72h}")
    print(f"skipped={skipped}")


if __name__ == "__main__":
    main()
