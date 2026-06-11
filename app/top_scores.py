from app.db import get_conn


def main():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                s.score,
                tf.symbol,
                tf.token_address,
                'https://dexscreener.com/solana/' || tf.token_address AS dex_link,
                tf.smart_wallet_count,
                tf.renowned_wallet_count,
                tf.sniper_wallet_count,
                tf.latest_liquidity,
                tf.latest_holder_count
            FROM token_scores s
            JOIN token_features tf ON tf.token_id = s.token_id
            ORDER BY s.score DESC
            LIMIT 30
            """
        ).fetchall()

    for row in rows:
        print("-" * 80)
        print(f"score: {row['score']}")
        print(f"symbol: {row['symbol']}")
        print(f"address: {row['token_address']}")
        print(f"dex: {row['dex_link']}")
        print(
            "metrics: "
            f"smart={row['smart_wallet_count']} "
            f"renowned={row['renowned_wallet_count']} "
            f"snipers={row['sniper_wallet_count']} "
            f"liquidity={row['latest_liquidity']} "
            f"holders={row['latest_holder_count']}"
        )


if __name__ == "__main__":
    main()
