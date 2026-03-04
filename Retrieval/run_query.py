"""
run_query.py
CLI entry point for the semantic retrieval module.

Usage
-----
# Basic query (default k=5, default outputs dir)
python run_query.py "What did I work on last time?"

# Specify top-k and a custom outputs directory
python run_query.py "Did I code something?" --k 3 --outputs-dir /path/to/outputs

# Pass a JSON file as input
python run_query.py --json-input query.json
  where query.json = {"query": "What did I do yesterday?", "k": 5}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from any working directory by adding the module dir to path
sys.path.insert(0, str(Path(__file__).parent))

from retriever import Retriever


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Semantic retrieval over outputs/events.json files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Natural language query string.",
    )
    p.add_argument(
        "--k",
        type=int,
        default=5,
        metavar="K",
        help="Number of top results to return (default: 5).",
    )
    p.add_argument(
        "--outputs-dir",
        default="outputs",
        metavar="DIR",
        help="Path to the root outputs/ directory (default: outputs).",
    )
    p.add_argument(
        "--json-input",
        metavar="FILE",
        help='JSON file with {"query": "...", "k": N} — overrides positional args.',
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True).",
    )
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # ── Resolve query & k ─────────────────────────────────────────────
    query: str | None = args.query
    k: int = args.k

    if args.json_input:
        try:
            payload = json.loads(Path(args.json_input).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            parser.error(f"Cannot read --json-input: {exc}")

        query = payload.get("query", query)
        k = int(payload.get("k", k))

    if not query:
        parser.error("Provide a query string as a positional argument or via --json-input.")

    # ── Run retrieval ─────────────────────────────────────────────────
    retriever = Retriever(outputs_dir=args.outputs_dir)
    result = retriever.retrieve(query=query, k=1)

    # ── Print + save results ──────────────────────────────────────────
    indent = 2 if args.pretty else None
    output = json.dumps(result, indent=indent, ensure_ascii=False)

    print(output)

    bundle_path = Path("contextbundle.json")
    bundle_path.write_text(output, encoding="utf-8")
    print(f"\n[run_query] Results written to {bundle_path.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()