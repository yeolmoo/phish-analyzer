from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt

from .utils import safe_netloc, effective_second_level, top_level_domain

log = logging.getLogger(__name__)

def load_and_clean(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # url column
    if "url" not in df.columns:
        raise ValueError("Input CSV must contain a 'url' column.")
    # select column: ie use source, first_seen 
    # URL normalize
    df["netloc"] = df["url"].apply(safe_netloc)
    df = df.dropna(subset=["netloc"]).copy()

    # root domain / TLD
    df["root_domain"] = df["netloc"].apply(effective_second_level)
    df["tld"] = df["netloc"].apply(top_level_domain)

    # remove same url - choose one if same
    before = len(df)
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)
    log.info("Deduplicated URLs: %d -> %d", before, len(df))

    # if there is time and date, refine
    for col in ["first_seen", "timestamp", "date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    return df

def plot_top_counts(series: pd.Series, title: str, xlabel: str, out_png: Path, topn: int = 10) -> None:
    top = series.value_counts().head(topn)
    if top.empty:
        log.warning("No data to plot for %s", title)
        return
    plt.figure(figsize=(10,6))
    top.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def analyze(df: pd.DataFrame, out_dir: Path) -> Tuple[Optional[Path], Optional[Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)

    # make graph 1: root domain
    p1 = out_dir / "top10_root_domains.png"
    plot_top_counts(df["root_domain"].dropna(), "Top 10 Root Domains (Phishing)", "Root Domain", p1)

    # make graph 2: tld
    p2 = out_dir / "top10_tld.png"
    plot_top_counts(df["tld"].dropna(), "Top 10 TLDs (Phishing)", "TLD", p2)

    return (p1 if p1.exists() else None, p2 if p2.exists() else None)

def to_markdown_report(df: pd.DataFrame, out_dir: Path, figs: Tuple[Optional[Path], Optional[Path]]) -> Path:
    md = out_dir / "report.md"
    total = len(df)
    top_root = df["root_domain"].value_counts().head(10)
    top_tld = df["tld"].value_counts().head(10)

    with md.open("w", encoding="utf-8") as f:
        f.write(f"# Phishing URL Analysis Report\n\n")
        f.write(f"- Total URLs Collected: **{total}**\n")
        if "first_seen" in df.columns:
            first = df["first_seen"].min()
            last = df["first_seen"].max()
            f.write(f"- Time range (first_seen): **{first} → {last}**\n")
        f.write("\n## Top 10 Root Domains\n\n")
        f.write(top_root.to_markdown())
        if figs[0]:
            f.write(f"\n\n![Top Root Domains]({figs[0].name})\n")
        f.write("\n\n## Top 10 TLDs\n\n")
        f.write(top_tld.to_markdown())
        if figs[1]:
            f.write(f"\n\n![Top TLDs]({figs[1].name})\n")
        # additional stuff : source and date
        if "source" in df.columns:
            f.write("\n\n## By Source (Top 10)\n\n")
            f.write(df["source"].value_counts().head(10).to_markdown())
        if "first_seen" in df.columns:
            by_day = df.set_index("first_seen").resample("D").size()
            f.write("\n\n## Daily Volume (first_seen)\n\n")
            f.write(by_day.tail(30).to_markdown())

    return md
