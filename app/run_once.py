from app.discover_tokens import main as discover_tokens
from app.collect_traders import main as collect_traders
from app.collect_tagged_traders import main as collect_tagged_traders
from app.collect_outcomes import main as collect_outcomes


def main():
    print("=== discover_tokens ===")
    discover_tokens()

    print("=== collect_traders ===")
    collect_traders()

    print("=== collect_tagged_traders ===")
    collect_tagged_traders()

    print("=== collect_outcomes ===")
    collect_outcomes()

    print("=== done ===")


if __name__ == "__main__":
    main()
