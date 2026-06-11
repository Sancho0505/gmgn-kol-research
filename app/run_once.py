from app.discover_tokens import main as discover_tokens
from app.collect_trenches import main as collect_trenches
from app.collect_snapshots import main as collect_snapshots
from app.collect_traders import main as collect_traders
from app.collect_tagged_traders import main as collect_tagged_traders
from app.collect_outcomes import main as collect_outcomes
from app.build_features import main as build_features
from app.score_tokens import main as score_tokens


def main():
    print("=== discover_tokens ===")
    discover_tokens()

    print("=== collect_trenches ===")
    collect_trenches()

    print("=== collect_snapshots ===")
    collect_snapshots()

    print("=== collect_traders ===")
    collect_traders()

    print("=== collect_tagged_traders ===")
    collect_tagged_traders()

    print("=== collect_outcomes ===")
    collect_outcomes()

    print("=== build_features ===")
    build_features()

    print("=== score_tokens ===")
    score_tokens()

    print("=== done ===")


if __name__ == "__main__":
    main()
