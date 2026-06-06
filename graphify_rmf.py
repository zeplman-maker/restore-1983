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
OBSIDIAN_SUBFOLDER = "graphify-map"   # → RMF Commander/graphify-map/  (node notes + canvas)
WIKI_SUBFOLDER     = "graphify-wiki"  # → RMF Commander/graphify-wiki/ (community wiki)

# ── Source extensions graphify can parse ────────────────────────────────────
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".java", ".cs", ".cpp", ".c", ".h",
    ".rs", ".rb", ".kt", ".scala", ".php",
    ".swift", ".lua", ".zig",
}


def run(cmd: list[str], cwd: Path, fatal: bool = True) -> bool:
    """Run a subprocess command, streaming output live. Returns True on success."""
    print(f"\n▶  {' '.join(str(c) for c in cmd)}\n")
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        msg = f"\n✖  Command failed (exit {result.returncode}). See errors above."
        if fatal:
            print(msg, file=sys.stderr)
            sys.exit(result.returncode)
        else:
            print(f"{msg} (skipping — not fatal)", file=sys.stderr)
            return False
    return True


def scan_project(project: Path) -> dict:
    """Walk the project tree and count files by type."""
    counts: dict[str, int] = {}
    for f in project.rglob("*"):
        if f.is_file():
            ext = f.suffix.lower()
            counts[ext] = counts.get(ext, 0) + 1
    return counts


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

    print("=" * 60)
    print("  graphify  →  Obsidian  |  RMF Commander")
    print("=" * 60)

    if not project.exists():
        print(f"\n✖  Project folder not found:\n   {project}", file=sys.stderr)
        print("\n   Check that the path is correct and try again.", file=sys.stderr)
        sys.exit(1)

    graphify_out   = project / "graphify-out"
    obsidian_dir   = project / OBSIDIAN_SUBFOLDER
    wiki_dir       = project / WIKI_SUBFOLDER
    graph_json     = graphify_out / "graph.json"

    print(f"  Project : {project}")
    print(f"  Graph   : {graph_json}")
    print(f"  Notes   : {obsidian_dir}")
    print(f"  Wiki    : {wiki_dir}")
    print("=" * 60)

    # ── File inventory ───────────────────────────────────────────────────────
    print("\n── File inventory ────────────────────────────────────────────")
    file_counts = scan_project(project)

    code_files = {ext: n for ext, n in file_counts.items() if ext in CODE_EXTENSIONS}
    other_files = {ext: n for ext, n in file_counts.items() if ext not in CODE_EXTENSIONS}

    total_code = sum(code_files.values())
    total_other = sum(other_files.values())

    if code_files:
        print(f"  Source code files graphify can parse ({total_code} total):")
        for ext, n in sorted(code_files.items()):
            print(f"    {ext:<8} {n}")
    else:
        print("  Source code files graphify can parse: NONE FOUND")

    if other_files:
        top = sorted(other_files.items(), key=lambda x: -x[1])[:6]
        print(f"  Other files ({total_other} total, top types):")
        for ext, n in top:
            label = ext if ext else "(no ext)"
            print(f"    {label:<8} {n}")

    if total_code == 0:
        print(
            "\n  ⚠  No parseable source code files found in this folder.\n"
            "     graphify reads: .py .js .ts .go .java .cs .rs .cpp etc.\n"
            "\n"
            "     If your RMF Commander project is code-based, make sure the\n"
            "     source files are inside (or below) this folder:\n"
            f"     {project}\n"
            "\n"
            "     If this project is documentation/notes only (.md), graphify\n"
            "     cannot build a graph from it — it parses code structure,\n"
            "     not markdown text.\n",
            file=sys.stderr,
        )
        input("  Press Enter to exit...")
        sys.exit(1)

    print(f"\n  ✓  Found {total_code} source file(s) — proceeding with extraction.")

    python = sys.executable
    gfy    = [python, "-m", "graphify"]

    # ── Step 1: AST extraction (no LLM required) ─────────────────────────────
    if not args.skip_extract:
        print("\n── Step 1 / 3 : AST extraction ──────────────────────────────")
        run(gfy + ["update", str(project)], cwd=project)
    else:
        print("\n── Step 1 / 3 : skipped (--skip-extract) ────────────────────")

    if not graph_json.exists():
        print(f"\n✖  graph.json not found at:\n   {graph_json}", file=sys.stderr)
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

    # ── Step 3b: Wiki export (optional — requires LLM analysis data) ─────────
    print("\n── Wiki export (optional) ────────────────────────────────────")
    wiki_dir.mkdir(parents=True, exist_ok=True)
    wiki_ok = run(
        gfy + [
            "export", "wiki",
            "--graph", str(graph_json),
            "--dir",   str(wiki_dir),
        ],
        cwd=project,
        fatal=False,
    )
    if not wiki_ok:
        print("  (Wiki export skipped — it requires LLM-enhanced data.", file=sys.stderr)
        print("   The canvas and node notes above are still fully usable.)", file=sys.stderr)

    # ── Done ──────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✓  Done!  Open Obsidian and look inside:")
    print(f"     03 - Projects/RMF Commander/{OBSIDIAN_SUBFOLDER}/")
    print(f"       → graph.canvas      (visual canvas — open in Obsidian Canvas)")
    print(f"       → one .md per node  (shows in Obsidian graph view)")
    if wiki_ok:
        print(f"     03 - Projects/RMF Commander/{WIKI_SUBFOLDER}/")
        print(f"       → index.md          (community index)")
    print("=" * 60)
    print("\n  Tip: Re-run any time after editing code to refresh the graph.")
    print("  Tip: Add --skip-extract if you only changed labels/clustering.")


if __name__ == "__main__":
    main()
