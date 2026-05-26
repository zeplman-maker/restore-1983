"""
graphify_rmf.py  —  Build a graphify knowledge graph for RMF Commander
and export it as an Obsidian vault (notes + canvas) inside your existing vault.

Usage (from your RMF Commander folder):
    python graphify_rmf.py

Or from anywhere:
    python graphify_rmf.py --project "C:\\Users\\Zeplman\\Documents\\Leo's Brain\\03 - Projects\\RMF Commander"
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ── Default project path ──────────────────────────────────────────────────────
DEFAULT_PROJECT = r"C:\Users\Zeplman\Documents\Leo's Brain\03 - Projects\RMF Commander"

# ── Where inside the vault to write graphify notes ───────────────────────────
# These folders will appear as regular notes in your Obsidian vault (Leo's Brain).
OBSIDIAN_SUBFOLDER = "graphify-map"   # → RMF Commander/graphify-map/  (node notes + canvas)
WIKI_SUBFOLDER     = "graphify-wiki"  # → RMF Commander/graphify-wiki/ (community wiki)


def run(cmd: list[str], cwd: Path) -> None:
    """Run a subprocess command, streaming output live."""
    print(f"\n▶  {' '.join(str(c) for c in cmd)}\n")
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        print(f"\n✖  Command failed (exit {result.returncode}). See errors above.", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="graphify → Obsidian setup for RMF Commander")
    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT,
        help="Path to the RMF Commander folder (default: %(default)s)",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip AST extraction (use if graph.json already exists)",
    )
    parser.add_argument(
        "--skip-cluster",
        action="store_true",
        help="Skip clustering (use if community data already exists)",
    )
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"✖  Project folder not found: {project}", file=sys.stderr)
        sys.exit(1)

    graphify_out   = project / "graphify-out"
    obsidian_dir   = project / OBSIDIAN_SUBFOLDER
    wiki_dir       = project / WIKI_SUBFOLDER
    graph_json     = graphify_out / "graph.json"

    python = sys.executable
    gfy    = [python, "-m", "graphify"]

    print("=" * 60)
    print("  graphify  →  Obsidian  |  RMF Commander")
    print("=" * 60)
    print(f"  Project : {project}")
    print(f"  Graph   : {graph_json}")
    print(f"  Notes   : {obsidian_dir}")
    print(f"  Wiki    : {wiki_dir}")
    print("=" * 60)

    # ── Step 1: AST extraction (no LLM required) ─────────────────────────────
    if not args.skip_extract:
        print("\n── Step 1 / 3 : AST extraction ──────────────────────────────")
        run(gfy + ["update", str(project)], cwd=project)
    else:
        print("\n── Step 1 / 3 : skipped (--skip-extract) ────────────────────")

    if not graph_json.exists():
        print(f"\n✖  graph.json not found at {graph_json}", file=sys.stderr)
        print("   Run without --skip-extract to generate it first.", file=sys.stderr)
        sys.exit(1)

    # ── Step 2: Community detection (Leiden / Louvain) ───────────────────────
    if not args.skip_cluster:
        print("\n── Step 2 / 3 : Community detection ─────────────────────────")
        run(gfy + ["cluster-only", str(project), "--no-viz"], cwd=project)
    else:
        print("\n── Step 2 / 3 : skipped (--skip-cluster) ────────────────────")

    # ── Step 3a: Obsidian vault export (node notes + canvas) ─────────────────
    print("\n── Step 3 / 3 : Obsidian export ──────────────────────────────")
    obsidian_dir.mkdir(parents=True, exist_ok=True)
    run(
        gfy + [
            "export", "obsidian",
            "--graph", str(graph_json),
            "--dir",   str(obsidian_dir),
        ],
        cwd=project,
    )

    # ── Step 3b: Wiki export (community markdown articles) ───────────────────
    wiki_dir.mkdir(parents=True, exist_ok=True)
    run(
        gfy + [
            "export", "wiki",
            "--graph", str(graph_json),
            "--dir",   str(wiki_dir),
        ],
        cwd=project,
    )

    # ── Done ──────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✓  Done!  Open Obsidian and look inside:")
    print(f"     03 - Projects/RMF Commander/{OBSIDIAN_SUBFOLDER}/")
    print(f"       → graph.canvas      (visual canvas — open in Obsidian Canvas)")
    print(f"       → one .md per node  (shows in Obsidian graph view)")
    print(f"     03 - Projects/RMF Commander/{WIKI_SUBFOLDER}/")
    print(f"       → index.md          (community index)")
    print(f"       → one .md per community")
    print("=" * 60)
    print("\n  Tip: Re-run any time after editing code to refresh the graph.")
    print("  Tip: Add --skip-extract if you only changed labels/clustering.\n")


if __name__ == "__main__":
    main()
