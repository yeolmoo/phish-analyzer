from __future__ import annotations
import argparse
import logging
from pathlib import Path
from .analyzer import load_and_clean, analyze, to_markdown_report

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze phishing URLs CSV and produce charts & Markdown report."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to phishing_urls.csv")
    parser.add_argument("-o", "--out", default="reports", help="Output directory")
    parser.add_argument("--topn", type=int, default=10, help="Top N for charts")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s"
    )

    csv_path = Path(args.input)
    out_dir = Path(args.out)

    df = load_and_clean(csv_path)
    fig_paths = analyze(df, out_dir)
    md_path = to_markdown_report(df, out_dir, fig_paths)

    print("Analysis complete. Artifacts:")
    for p in fig_paths:
        if p:
            print("-", p)
    print("-", md_path)

if __name__ == "__main__":
    main()
