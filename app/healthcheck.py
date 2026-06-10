from app.db import count_table

TABLES = [
    "tokens",
    "token_snapshots",
    "token_traders",
    "kol_accounts",
    "kol_posts",
    "token_kol_links",
    "token_outcomes",
]

def main():
    for table in TABLES:
        print(f"{table}: {count_table(table)}")

if __name__ == "__main__":
    main()
