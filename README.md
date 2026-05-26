# graphify → Obsidian setup for RMF Commander

Turn your **RMF Commander** source code into an interactive knowledge graph that lives directly inside your **Obsidian vault (Leo's Brain)**.

---

## What this does

| Output | Location in vault | What it is |
|--------|------------------|------------|
| Node notes | `03 - Projects/RMF Commander/graphify-map/*.md` | One note per class/function/module with `[[wikilinks]]` — shows up in Obsidian's graph view |
| Canvas | `03 - Projects/RMF Commander/graphify-map/graph.canvas` | Visual infinite canvas — communities as groups, nodes as cards, edges as arrows |
| Wiki | `03 - Projects/RMF Commander/graphify-wiki/*.md` | One article per community + `index.md` |

---

## First-time setup

> **Requires Python 3.10+ installed** — download from [python.org](https://www.python.org/downloads/)

1. Copy this folder's files somewhere on your machine (e.g. your Desktop, or the RMF Commander folder itself).
2. Double-click **`install_graphify.bat`**
3. That's it — it installs graphify and builds the graph automatically.

---

## Updating the graph (after code changes)

Just double-click **`run_graphify_rmf.bat`** any time you want to refresh.

Or from a terminal:
```bat
python graphify_rmf.py
```

**Speed options:**
```bat
REM Skip re-reading the code (just re-cluster and re-export):
python graphify_rmf.py --skip-extract

REM Skip both extraction and clustering (just re-export Obsidian files):
python graphify_rmf.py --skip-extract --skip-cluster
```

---

## Opening in Obsidian

1. Open **Obsidian** with your **Leo's Brain** vault (it probably already is)
2. In the file explorer, navigate to `03 - Projects → RMF Commander → graphify-map`
3. Open **`graph.canvas`** for the visual canvas view
4. Or open any `.md` note and click the **Graph view** icon (top-right) to see the full knowledge graph

**Tip:** In Obsidian's graph view filters, type `path:03 - Projects/RMF Commander/graphify-map` to see only the RMF Commander graph.

---

## How it works

```
RMF Commander source files
        │
        ▼
graphify update  (AST extraction — no LLM, fast)
        │  reads: .py / .js / .ts / .go / .java / .cs / etc.
        │  writes: graphify-out/graph.json
        ▼
graphify cluster-only  (Leiden community detection)
        │  groups related nodes into communities
        ▼
graphify export obsidian  →  graphify-map/
graphify export wiki      →  graphify-wiki/
```

No API keys or LLM calls needed — pure AST parsing via tree-sitter.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not found | Install Python from python.org; make sure "Add to PATH" is checked |
| `pip install` fails | Try `pip install --user "git+https://github.com/safishamsi/graphify.git@v8"` |
| Empty graph | Make sure your source files are in the RMF Commander folder (`.py`, `.js`, `.ts`, etc.) |
| Want LLM-enhanced graph | Run `python -m graphify extract "C:\...\RMF Commander" --backend claude` (needs `ANTHROPIC_API_KEY`) |
