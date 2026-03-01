import argparse
from pathlib import Path

from src.config import SliceConfig
from src.pipeline.capture_preprocess import run_capture_preprocess


def main():
    parser = argparse.ArgumentParser(description="Slice-1: Capture + Preprocess")
    parser.add_argument("--source", required=True, choices=["reading", "transcript", "code"])
    parser.add_argument("--path", required=True, help="Path to input file (txt/diff)")
    parser.add_argument("--task_id", required=True, help="Task identifier (e.g., TASK001)")
    parser.add_argument("--outdir", default="outputs", help="Base output directory")
    parser.add_argument("--token_budget", type=int, default=220, help="Token budget per chunk")
    parser.add_argument("--overlap_tokens", type=int, default=0, help="Overlap tokens between chunks")
    parser.add_argument("--min_chunk_tokens", type=int, default=30, help="Minimum tokens per chunk")
    args = parser.parse_args()

    cfg = SliceConfig(
        token_budget=args.token_budget,
        overlap_tokens=args.overlap_tokens,
        min_chunk_tokens=args.min_chunk_tokens,
        output_base_dir=args.outdir,
    )

    input_path = Path(args.path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    session_dir = run_capture_preprocess(
        cfg=cfg,
        source_type=args.source,
        input_path=input_path,
        task_id=args.task_id,
    )

    print(f"\nDONE ✅")
    print(f"Session output directory: {session_dir}\n")


if __name__ == "__main__":
    main()