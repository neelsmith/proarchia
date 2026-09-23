# Session log

Notes on work done in this repo by Claude, across Cowork sessions. Append,
don't rewrite, so history survives a fresh clone on another machine.

## 2026-09-21 -- first marimo notebook

Task (per `notes/project.md`): build the first marimo notebook -- one that
loads every syntax analysis file in `data/` automatically, with no user
prompting, and otherwise mimics the behavior of arsgrammatica's own
`marimo/latin_syntaxer_review.py`.

What I did:

- Read `CLAUDE.md` and `notes/project.md` for scope and restrictions.
- Inspected the `.cex` files in `data/` directly, and fetched
  arsgrammatica's serialization-format reference and the actual source of
  `marimo/latin_syntaxer_review.py` from
  https://github.com/neelsmith/arsgrammatica (installed the package with
  `pip install git+https://github.com/neelsmith/arsgrammatica.git` in a
  scratch environment to confirm exact function signatures and behavior
  against the real `data/` files -- not installed anywhere in this repo).
- Wrote `marimo/review_analyses.py`. It follows
  `latin_syntaxer_review.py` cell-for-cell, with one substantive change:
  the `mo.ui.file_browser` is replaced by a loading cell that globs
  `data/*.cex`, sorts them by the numeric `tokenized_<n>` suffix in each
  filename (so sentences stay in reading order regardless of alphabetical
  quirks -- e.g. `_10` sorting before `_2`), and calls `read_analyses()`
  on each file, concatenating `(tokengraph, verbalunits, sentences,
  lm_infos)` across all of them. A file that fails to parse is reported as
  a warning and skipped, rather than blocking the rest. Everything
  downstream (sentence picker, highlighting, Mermaid/Graphviz/displaCy
  diagrams, subordination-depth slider, AAT graph) is unchanged from the
  reference notebook, now just spanning every sentence in `data/` instead
  of one browsed file.
- Validated the notebook two ways before writing it back: (1) ran the
  loading/concatenation logic standalone against the real 17 files in
  `data/` (confirms 17 sentences load in the correct order 1-12, 14-18 --
  file `..._13_...` does not exist -- and that every rendering function
  arsgrammatica exposes runs cleanly on the first sentence); (2)
  `marimo export script` + `marimo export html` on the assembled notebook
  itself, both completing without error.
- Did not modify `README.md`, `releases.md`, `quarto/`, or `docs/`.
- Did not run `git add`/`git commit`/`git push` -- left the new file and
  this log entry unstaged for Neel to review.

Left for a future session: nothing outstanding from `notes/project.md` --
the first notebook is done. Possible next steps if wanted: notebooks for
the other `marimo/latin_syntaxer_*.py` variants (ctsdata, graph metrics,
selected ids, text input, tokenized), or a `pyproject.toml`/requirements
file pinning `arsgrammatica`/`marimo` for this repo specifically (the new
notebook currently only declares them via a PEP 723 `# /// script` header,
which `marimo edit --sandbox` and `uv run` pick up automatically but a
plain `pip install` workflow would not).

## 2026-09-21 -- fix sandbox dependency resolution

Neel hit this on `marimo edit --sandbox marimo/review_analyses.py`:

    No solution found when resolving `--with` dependencies:
    Because arsgrammatica was not found in the package registry ...

Cause: arsgrammatica isn't published on PyPI, so the notebook's PEP 723
`dependencies = ["marimo", "arsgrammatica"]` block alone gives `uv` nothing
to resolve `arsgrammatica` against.

Fix: added a `[tool.uv.sources]` table to the same header pointing
`arsgrammatica` at its GitHub repo directly:

    [tool.uv.sources]
    arsgrammatica = { git = "https://github.com/neelsmith/arsgrammatica.git" }

Verified with `uv export --script marimo/review_analyses.py` (resolves
cleanly, pulls arsgrammatica from the git repo) and a full
`uv run --isolated --with-requirements <exported reqs> ...` install into a
throwaway venv (installs all 83 packages, `import arsgrammatica` and
`import marimo` both succeed) before writing the fix back.

## 2026-09-21 -- sentence menu wasn't showing; removed the AAT graph section

Neel reported the sentence-selection menu wasn't appearing, and asked to
drop the "Reduction to AAT graph" section entirely.

Root cause of the missing menu: marimo only displays a cell's bare,
unassigned top-level expression as that cell's last statement. The status
cell built its `mo.vstack([...])` call *inside* an `if/else` (to show a
warning line only when some files failed to read), so neither branch's
vstack was ever the cell's own top-level last expression -- nothing
rendered, menu included. Fixed by assigning the result to `status_display`
in both branches and referencing that name as its own bare statement
before `return`, matching the same pattern already used elsewhere in this
notebook (e.g. `diagram_display`). Confirmed the fix with
`marimo export html`: the rendered output now embeds a
`<marimo-dropdown ...>` element listing all 17 sentences, which it did not
before.

Removed entirely: the "## Reduction to AAT graph" heading, its display
cell, the `aat_tokengraph`/`aat_diagram`/`aat_display` build cells, and the
now-unused `aatgraph`, `filter_tokengraph_by_aat_depth`, `SimpleNamespace`,
`aat_available`, `graph_to_mermaid` imports (including the `aat.core` probe
import). Left everything else alone -- in particular the `aat_depth`
*parameter name* on `tokengraph_to_mermaid`/`tokengraph_to_dot`/
`tokengraph_to_displacy_svg` is unrelated to this feature (it's just what
those functions call the subordination-depth cutoff) and still works the
same way, fed by the same "Maximum depth of subordination to display"
slider as before.

Verified with `marimo export html` again after both changes: the rendered
page shows the sentence dropdown with all 17 entries, and no trace of the
AAT section or any error/traceback.

## 2026-09-21 -- shorten sentence-menu labels to the passage number only

Neel asked for the sentence-selection menu to show just the CTS URN's
passage component (the part after the last colon, e.g. `1`) instead of the
whole URN (`urn:cts:latinLit:phi0474.phi016.omar:1`), still followed by
the first few words of the sentence.

Changed `sentence_label()` (in `marimo/review_analyses.py`) to derive
`passage = citation.rsplit(":", 1)[-1]` before building the menu-entry
prefix, rather than using the raw `citation` string directly. Falls back
to the citation unchanged if it has no colon at all. Verified with
`marimo export html` against the real `data/` files: menu entries now read
like `1. 1: si quid est in me ingeni,…` and `4. 2: ac ne quis a nobis
hoc…` rather than repeating the full URN each time.

## 2026-09-21 -- previous fix hadn't actually landed; reapplied on top of hand edits

Neel reported the dropdown was still showing the full URN, and flagged
that he'd hand-edited the notebook in the meantime (title changed to
"Cicero, *Pro Archia*", the "## Sentence selection" heading reworded to
"## Select a sentence", the old instructions blockquote removed, the
`analysis_paths` cell's redundant `analysis_sort_key` parameter dropped,
and the `selected_sentence`/`selected_verbalunits` cell's return trimmed
down to just `selected_citation, selected_tokengraph` now that nothing
downstream needs the other two -- a cleanup that was overdue after the
AAT-graph removal above, since I'd left those two lying around unused).

What actually happened: this repo has a `marimo/__marimo__/session/`
folder, meaning marimo edit has an active session on this notebook. My
previous push (the passage-number fix) landed on disk only briefly before
that live session's own autosave overwrote it with content from an
*earlier* version it still had open in the browser -- one that predates
that fix but postdates the AAT removal, and that Neel had since hand-edited
in the UI. Net effect: Neel's hand edits survived, but my `sentence_label`
change silently didn't.

This time, rather than overwriting the whole file from a local copy,
edited `sentence_label()` in place on Neel's own machine with a targeted
Python read-modify-write against the file as it currently stood (verified
by diffing against Neel's actual hand-edited content first), so none of
the hand edits above were touched. Re-verified with `marimo export html`
against the real `data/` files afterward: menu entries read `1. 1: si
quid est in me ingeni,…` etc., and every hand-edited piece (title, "Select
a sentence" heading, trimmed return tuple) is still intact.

Flagged to Neel: as long as a `marimo edit` session on this notebook stays
open, its autosave will keep clobbering any change made to the file from
outside that session with whatever it still has loaded in the browser --
reloading the page in the browser after an outside edit (or saving/closing
before one) avoids this.

## 2026-09-21 -- split into reader.py and reader_w_graphviz.py

Neel asked to rename `review_analyses.py` to `reader.py`, and add a second
notebook, `reader_w_graphviz.py`, that adds the option of viewing a
sentence's syntax graph as a Graphviz digraph.

Read this as: `reader.py` going forward is the lean version (Mermaid/
displaCy only, no Graphviz-related code or dependency at all), and
`reader_w_graphviz.py` is that same notebook plus Graphviz layered back
in as a third diagram-tool option -- rather than both notebooks ending up
identical, which would make "adds ... the option" a no-op.

What I did:

- `mv marimo/review_analyses.py marimo/reader.py` (an actual rename, not
  delete + recreate).
- Saved a copy of reader.py's pre-edit content (which already had all
  three diagram tools working, from earlier work) as
  `marimo/reader_w_graphviz.py`, and added `graphviz` (the PyPI wrapper
  package) to its own PEP 723 `dependencies` list -- since offering that
  option is this notebook's whole reason to exist, unlike reader.py where
  it was only ever an optional, try/except import.
- Stripped every Graphviz-related piece back out of `reader.py`: the
  `graphviz` try/except import (and `graphviz`/`graphviz_available` from
  that cell's returned names), the `tokengraph_to_dot` import and the
  cell that computed `dot_source`/`dot_warnings` from it, the "graphviz"
  branch in both the diagram-display and diagram-download cells, and the
  `graphviz_available` conditional on the diagram-tool radio (now always
  just `["mermaid", "displacy"]`).
- Left a one-line pointer in reader.py's diagram-display cell noting that
  reader_w_graphviz.py offers Graphviz too, for anyone reading the code
  who wonders why it's missing.

Verified both notebooks for real on this machine (not just in my own
sandbox) with `uv run --isolated --no-project --with marimo --with
"arsgrammatica @ git+..." [--with graphviz] -- python3 -m marimo export
html ...`, against the actual `data/` files:
- `reader.py`: diagram-tool radio resolves to exactly `["mermaid",
  "displacy"]`, sentence menu still lists all 17 sentences correctly, no
  errors.
- `reader_w_graphviz.py`: diagram-tool radio resolves to `["mermaid",
  "graphviz", "displacy"]`. This machine already has both the `graphviz`
  PyPI package's dependency (`dot`) on PATH and the package itself
  installs cleanly, so this actually exercised real SVG rendering via
  `graphviz.Source(...).pipe(format="svg")`, not just the
  package-missing/executable-missing fallback paths. No errors either
  way.

Also cleaned up build-artifact clutter this session's own testing left
behind: removed the stale `marimo/__pycache__/` (including a `.pyc` for
the now-gone `review_analyses.py`), and added `__pycache__/` and
`marimo/__marimo__/` to `.gitignore` so neither gets committed going
forward. Did not touch `marimo/__marimo__/` itself -- that's Neel's own
live `marimo edit` session state, not mine to remove.

Left uncommitted, as always -- `git status` shows the rename (as a
delete + two new files, since content diverged too) plus the `.gitignore`
change.

## 2026-09-21 -- fix broken Graphviz digraphs (not just noisy warnings)

Neel reported a stream of warnings like `Warning: syntax ambiguity -
badly delimited number '6.t' in line 5 of <stdin> splits into two
tokens` when choosing the Graphviz option in `reader_w_graphviz.py`.

Traced this to arsgrammatica's own `tokengraph_to_dot()` (arsgrammatica/
dot.py): it writes each token's id -- "1.t2", "1.t19_implied", etc. -- as
a BARE, unquoted DOT identifier, both as a node's own name and in every
`->` edge referencing it. DOT's grammar has no identifier form that
starts with a digit and also contains letters; the closest thing, a
numeral, allows only digits and a single ".", so Graphviz's own lexer
reads "1.t2" as the numeral "1." immediately followed by a separate
identifier "t2" -- hence the warning.

This turned out to be a real correctness bug, not just noise: rendered
without a fix, EVERY token id sharing the same leading "N." (e.g. every
"1.tNN" token) collapses onto one shared, malformed node literally named
"1." in the output graph -- confirmed by rendering a real sentence's DOT
source both ways and comparing SVG node/edge titles: unpatched, edges
that should read e.g. "1.t72 -> 1.t92" instead read "t72 -> 1." (a bogus
node merging every "1.*" token's edges together); patched, they read
correctly.

Added a `quote_dot_token_ids()` helper (an `@app.function`, same
convention as `sentence_label`/`analysis_sort_key`) to
`marimo/reader_w_graphviz.py` only -- `reader.py` doesn't offer Graphviz
at all, so it's unaffected -- that wraps every bare token-id-shaped
identifier in the DOT source in quotes via
`re.sub(r"\b(\d+\.t\d+(?:_implied)?)\b", r'"\1"', dot_source)` before it's
used anywhere downstream (both the live SVG render and the "Download
Graphviz DOT source (.dot)" button now get the corrected source). Applied
in the cell that calls `tokengraph_to_dot()`, right after the call.

Verified on this machine with real data and the real `dot` executable
(not just the fallback path): before the fix, `dot -Tsvg` on a real
sentence's DOT source printed dozens of "badly delimited number"
warnings and silently merged nodes; after, zero warnings, and the SVG's
node/edge titles show each token as its own distinct node with the
correct governor. Also ran the whole notebook through `uv run --isolated
--with marimo --with arsgrammatica --with graphviz -- python3 -m marimo
export html marimo/reader_w_graphviz.py` end to end afterward -- no
errors, no leftover warnings.

This is a workaround living in this repo's own notebook, not a fix to
arsgrammatica itself (not this project's package to change) -- worth
reporting upstream at some point, but out of scope here.

## 2026-09-23: WASM-export dependency check — arsgrammatica not yet live on PyPI

User asked to switch `reader.py`/`reader_w_graphviz.py` off the
`[tool.uv.sources]` git pointer for `arsgrammatica` and onto plain PyPI
dependencies for both `arsgrammatica` and `aatgraph` (the renamed `aat`
package), specifically to unblock `marimo export html-wasm`.

Checked both packages against PyPI's JSON API (`https://pypi.org/pypi/
<name>/json`) rather than assuming:

- `aatgraph` **is** live: 0.3.0, pure-Python wheel
  (`aatgraph-0.3.0-py3-none-any.whl`), and its own `dspy` dependency is
  now an optional extra (`dspy>=3.0; extra == "english"` /
  `"dev"`), not unconditional. Moot for now, though -- neither notebook
  currently imports `aat`/`aatgraph` at all (it was removed from
  `reader.py` earlier this project, per the user's own request, and
  never existed in `reader_w_graphviz.py`); this only matters if an AAT
  view comes back.
- `arsgrammatica` is **not** live under that name: `pypi.org/pypi/
  arsgrammatica/json` returns a clean 404 (checked repeatedly, not a
  transient blip), and `pip index versions arsgrammatica` / `pip
  download arsgrammatica` both fail the same way run directly on this
  machine. Checked GitHub for context: `pyproject.toml` on `main` is at
  0.11.1, and `releases.md`'s 0.11.1 entry (dated today) reads
  "Corrects configuration of pypi.org" -- and the repo's
  `publish.yml` only pushes to the real index on a GitHub Release
  publish event (a tag push alone only reaches TestPyPI), gated on PyPI
  Trusted Publishing (OIDC) being registered correctly on pypi.org's own
  side for this exact repo/workflow/environment. Reads like the publish
  is mid-setup rather than finished.

Good news found along the way: `main`'s `pyproject.toml` shows
`arsgrammatica`'s own maintainer has already done almost exactly the
fix I'd floated last session for the DSPy-dependency WASM blocker --
base package dependencies are now just `pydantic` and `networkx`; `dspy`
moved to an optional `llm` extra; and `__init__.py`'s imports of
`latin_syntax_dspy.py`/`segmentation_dspy.py`/`pipeline.py` are lazy-
stub guarded the same way `aat_bridge.py` already was, per the extra's
own inline comment (which cites this exact WASM use case and this
project's earlier `latin_syntaxer_review.py` by name). Once this is
actually live on PyPI, the `litellm`/`tokenizers`/`fastuuid` blockers
identified in the previous WASM investigation should disappear from
`reader.py`'s dependency chain entirely.

**Not yet changed**: left both notebooks' PEP 723 headers pointing at
the GitHub `[tool.uv.sources]` override, since switching to a PyPI
dependency that doesn't resolve would break `uv run --sandbox` outright.
Told the user to confirm the PyPI publish succeeded (or fix the
Trusted Publisher config) before I make the switch.

## 2026-09-23 (cont.): Switched both notebooks to PyPI `arsgrammatica`

Re-checked PyPI now that the user confirmed the publish went through:
`pypi.org/pypi/arsgrammatica/json` now returns 0.11.2, a pure-Python
wheel (`arsgrammatica-0.11.2-py3-none-any.whl`), with `requires_dist`
showing base deps of just `pydantic>=2.0` and `networkx>=3.0` -- `dspy`
is an `llm` extra, and `aatgraph` (the renamed `aat` package, also
confirmed live on PyPI at 0.3.0) is now its own `aat` extra, so the old
`aat @ git+...` direct-URL dependency is gone from arsgrammatica's own
metadata too. Confirmed the same from this machine directly (`pip index
versions arsgrammatica` -> 0.11.2).

Updated the PEP 723 header in both `marimo/reader.py` and
`marimo/reader_w_graphviz.py`: dropped the `[tool.uv.sources]` git
override entirely and changed the dependency to `"arsgrammatica>=0.11.2"`
(plain PyPI). Edited in place on this machine with a fresh read +
single-match `count(old) == 1` assertion first, per the established
safe-edit convention, so nothing else in either file was touched.

Verified, not just asserted:

- `uv export --script` on both notebooks resolves cleanly (37 packages
  for `reader.py`, 38 for `reader_w_graphviz.py` with `graphviz` added)
  with zero occurrences of `dspy`, `litellm`, `tokenizers`, `fastuuid`,
  `boto3`, or `botocore` anywhere in the tree -- the entire blocker
  identified in the previous WASM investigation is gone, not just
  hidden behind an extra.
- Every native-only package still in the resolved set (`pyzmq`,
  `psutil`, `starlette`, `uvicorn`, `websockets`, `loro`) already carries
  marimo's own `sys_platform != 'emscripten'` marker, so Pyodide skips
  them automatically; the rest (`pydantic`, `pydantic-core`, `networkx`,
  `msgspec`, and the small doc/markdown/parso/jedi-type tooling marimo
  itself needs) were already confirmed in the prior investigation to
  have Pyodide-provided wheels.
- Installed the resolved set into a fresh isolated venv and imported
  `arsgrammatica`'s rendering functions directly: `dspy`/`litellm` never
  appear in `sys.modules` afterward.
- Ran `marimo export html-wasm marimo/reader.py --mode run --execute -f`
  end to end (succeeds); the exported `index.html`'s embedded
  `notebookCode` shows the PEP 723 header baked in as
  `dependencies = ["marimo==0.24.2", "arsgrammatica==0.11.2"]` -- i.e.
  the artifact marimo actually built for the browser is resolved purely
  from PyPI, no git source, no dspy chain. (Note: `--execute`'s own
  preview still runs under native CPython here, not real Pyodide --
  the Pyodide lockfile fetch fails from this network the same as last
  time -- so this checks the resolved dependency set and that the
  export step itself succeeds, not that Pyodide can install every wheel
  in a real browser. Given every remaining package's wheel status was
  independently confirmed via PyPI/Pyodide metadata, that residual gap
  is small, but a real in-browser load is the only fully conclusive
  test.)
- `uv run --isolated ... -- python3 -m marimo export script` on both
  notebooks also completed cleanly against the newly-resolved PyPI-only
  dependency sets, using this repo's real `data/` files.

Left `reader_w_graphviz.py`'s own explanatory comment about needing the
system `dot` executable as-is -- that's a runtime/PATH concern, separate
from package resolution, and still accurate (the `graphviz` PyPI package
itself is pure Python, only the separate `dot` binary is native, and it
just isn't reachable from Pyodide -- the notebook already degrades to
reporting that rather than failing).

## 2026-09-23 (cont.): Read from marimo/public/ via mo.notebook_location()

User put a copy of the `data/` analysis files in `marimo/public/` and
asked both notebooks to read from there via `mo.notebook_location()`,
continuing the WASM-export prep.

Checked `mo.notebook_location()`'s actual implementation (marimo 0.24.2)
before writing anything against it: in native execution it's just
`notebook_dir()` (a real local `pathlib.Path`); under Pyodide it returns
`URLPath` -- a bare `pathlib.PurePosixPath` subclass with no filesystem
methods at all (`.open()`/`.is_dir()`/`.glob()` all raise
`AttributeError`), representing the notebook's own hosted URL. Also
checked marimo's server code (`assets.py`) and its `html-wasm` export
path (`Exporter().export_public_folder()`): the exported bundle serves
each `public/` file by its own exact name as a static file -- there is
no directory-listing endpoint, in dev mode or in the exported static
bundle. So the existing `DATA_DIR.glob("*.cex")` approach cannot carry
over as-is: the *path construction* needed to switch to
`mo.notebook_location() / "public"`, but file *discovery* needed a
different mechanism entirely, since nothing can list a `public/`
directory's contents over plain HTTP once it's exported.

Also checked arsgrammatica's `read_analyses()` (0.11.2) directly: it
does a plain local `open(path, ...)` -- no URL awareness -- so under
Pyodide it can't be handed a URLPath directly either.

Solution, implemented identically in both `reader.py` and
`reader_w_graphviz.py`:

- New `marimo/generate_public_manifest.py` (standalone script, not part
  of the interactive notebook -- keeps the notebooks themselves free of
  filesystem writes, matching their existing read-only design) scans
  `public/*.cex` and writes `public/manifest.json`, a plain sorted JSON
  array of filenames. Ran it now to produce the initial manifest (17
  entries, matching `data/`). Re-run it whenever `public/`'s `.cex`
  files change, before the next `marimo export html-wasm`.
- Three new `@app.function` helpers, in both notebooks:
  `is_remote_location(path)` (checks for `"://" ` in `str(path)` --
  `URLPath.__str__` is written specifically to preserve it, so this is
  the one reliable, public-API-only way to tell a URLPath from a real
  Path); `read_location_text(path)` (local `.read_text()` or
  `urllib.request.urlopen(str(path))` depending); and
  `resolve_readable_path(path)` (passthrough locally, or -- under
  Pyodide -- fetches the content and writes it to a local tempfile,
  since `read_analyses()` needs an actually-openable local path either
  way).
- `DATA_DIR = Path(__file__).parent.parent / "data"` became
  `PUBLIC_DIR = mo.notebook_location() / "public"`.
- File discovery changed from `DATA_DIR.glob("*.cex")` to reading
  `public/manifest.json` (via `read_location_text` + `json.loads`) and
  building `analysis_paths` from its filename list -- still re-sorted
  through the existing `analysis_sort_key()` afterward, so citation
  ordering is unaffected. A manifest read/parse failure now surfaces
  through the same `read_error` display path the old "no files found"/
  "files found but unreadable" cases already used.
- The per-file read loop now calls `read_analyses(resolve_readable_path(_path))`
  instead of `read_analyses(str(_path))`.
- Updated the status line's "`data/`" wording to "`public/`", and the
  two `read_error` message strings to name `public/manifest.json`
  instead of `data/`.
- Imports cell: dropped `from pathlib import Path` (no longer used
  anywhere outside comments) and added `import json`.

An intentional design choice worth calling out: both notebooks now
resolve their file list through the manifest in *every* context, not
just under Pyodide -- so what a local `marimo edit`/`marimo run` shows
is exactly what the exported bundle will show, with no risk of a file
freshly added to `public/` working locally (old glob-based discovery)
but silently missing from the export because the manifest wasn't
regenerated yet.

Verified, not just asserted:

- `marimo check` on both notebooks: no errors.
- `from reader import app; app.run()` (marimo's own documented way to
  execute a notebook programmatically) against the real `public/`
  directory: 17/17 files found via the manifest, 17 sentences loaded,
  no errors or warnings. Same for `reader_w_graphviz.py`.
- Started a real local HTTP server over `public/`
  (`python3 -m http.server`) and exercised `is_remote_location`,
  `read_location_text`, `resolve_readable_path`, and
  `analysis_sort_key` directly against a real `marimo._runtime.runtime.URLPath`
  pointed at `http://127.0.0.1:8934` -- i.e. the exact code path Pyodide
  will take, not just the native one. Full round trip (manifest fetch,
  per-file fetch-to-tempfile, `read_analyses()` on the tempfile)
  succeeded: 17/17 files, 17 sentences, entirely over HTTP.
- Ran `marimo export html-wasm marimo/reader.py --mode run --execute -f`
  end to end again: the exported bundle's `public/` directory contains
  all 17 `.cex` files plus `manifest.json`, copied verbatim alongside
  `index.html` (confirms `Exporter().export_public_folder()` picked up
  the new files correctly).

Not independently verified: an actual Pyodide/browser load of the
exported bundle (the Pyodide lockfile fetch still fails from this
network, same limitation noted in the previous WASM investigations) --
the HTTP-server test above exercises the same `urllib.request` call
Pyodide is documented to transparently proxy through the browser's
`fetch()` for same-origin requests, but that proxying itself is the one
piece that can only be confirmed by actually opening the exported page
in a browser.

## 2026-09-23 (cont.): Moved generate_public_manifest.py to utilities/

Moved `marimo/generate_public_manifest.py` to `utilities/generate_public_manifest.py`
at the user's request -- it's a standalone maintenance script, not part
of either notebook, so it belongs with this project's other utility
scripts rather than inside `marimo/`. Updated its `PUBLIC_DIR` constant
(`Path(__file__).parent / "public"` -> `Path(__file__).parent.parent / "marimo" / "public"`,
since `utilities/` and `marimo/` are now siblings) and its own
docstring/usage line to match the new path. Re-ran it from the new
location to confirm it still finds `marimo/public/` correctly -- wrote
the same 17 filenames as before. Also fixed the one other reference to
the old path, in `notes/wasmexport.md`.

## 2026-09-23 (cont.): Optional display of '#!lm' model info in both notebooks

Added to both `marimo/reader.py` and `marimo/reader_w_graphviz.py`
(identical changes):

- The loading cell now also returns `lm_infos` (it was already collecting
  them from `read_analyses()`, padded with `None` for files without a
  `#!lm` block, but not exposing them).
- New `sentence_context_id(sentence)` function rebuilds the
  `CONTEXT=` identifier arsgrammatica writes
  (`<citation>.<id>-<citation>.<id>` of the sentence's first/last token;
  arsgrammatica's own `_sentence_context_identifier()` is private).
- New `lm_by_context` cell: `{info.context: info}` over every loaded entry.
- The selection cell now also returns `selected_lm_info`, matched by
  CONTEXT, falling back to the positionally aligned `lm_infos` entry.
- New `show_lm_info` checkbox (off by default) and `lm_info_display` cell,
  shown under "Selected text" right after the passage text: a callout with
  Model, Context and Reasoning for the selected sentence, or a note that
  no `#!lm` data was recorded for it.
- Consolidated `import html` into the imports cell (was `import html as
  _html` in one cell; a second one tripped `marimo check`'s
  private-import-alias rule).

Verified: `marimo check` clean on both; `app.run()` on both loads 17
sentences and all 17 match a `#!lm` entry by CONTEXT; ran the
`lm_info_display` cell directly with the checkbox on, for both a real
entry and `None`.

## 2026-09-23 (cont.): Moved analysis files to marimo/public/analyses/

At the user's request, moved all 17 `.cex` files and `manifest.json` from
`marimo/public/` into `marimo/public/analyses/` (with `git mv`, so the
renames are staged but not committed). The manifest moved with the
files it lists.

- Both notebooks: the `PUBLIC_DIR` cell is now `ANALYSES_DIR =
  mo.notebook_location() / "public" / "analyses"`; manifest and file
  paths, the status line, and the error messages now say
  `public/analyses/`.
- `utilities/generate_public_manifest.py`: `PUBLIC_DIR` -> `ANALYSES_DIR`
  (`.../marimo/public/analyses`); docstring updated.
- `notes/wasmexport.md`: path in the re-run reminder updated.

Verified: regenerating the manifest from the new location reproduces the
same 17 names; `marimo check` clean on both; `app.run()` on both loads
17 files / 17 sentences with no errors or warnings, and all 17 `#!lm` entries;
`marimo export html-wasm` copies `public/analyses/` (17 `.cex` +
manifest) into the bundle.

## 2026-09-23 (cont.): Manually-vetted marks and filter from public/sentencestatus.cex

Both notebooks now read `marimo/public/sentencestatus.cex` (`sentence|vetted`
header; first column `<file>:CONTEXT=<context id>`, second `True`/`False`):

- `SENTENCE_STATUS_PATH` added to the locations cell (next to `ANALYSES_DIR`).
- New `parse_sentence_status(text)` function -> `{context id: bool}`, keyed on
  the part after `CONTEXT=`, so it matches `sentence_context_id()`.
- New loading cell -> `vetted_by_context`, `sentence_status_warning`. A
  missing/unreadable file (`OSError`, which also covers urllib's
  `URLError`/`HTTPError` under Pyodide) shows a warning and treats every
  sentence as unvetted.
- New `vetted_only` checkbox (own cell, since the dropdown depends on it),
  shown just above the sentence menu.
- `sentence_label()` takes `vetted=False` and prefixes `✅ `; the dropdown
  cell skips unvetted sentences when `vetted_only` is checked. Menu numbers
  stay each sentence's position in the whole passage. The dropdown cell also
  returns `vetted_count`, shown in the status line.

Verified: `marimo check` clean on both; `app.run()`: 17 status rows, all
matching a loaded sentence, 1 vetted (no. 17, §6); full menu 17 entries with
exactly that one marked ✅; re-running the dropdown cell with the checkbox on
gives only that entry.

Known behaviour: toggling the checkbox rebuilds the dropdown, so the
current selection resets.

## 2026-09-23 (cont.): Removed obsolete quote_dot_token_ids() workaround

Graphviz diagrams in `reader_w_graphviz.py` were failing ("badly delimited
number '6.t' ... splits into two tokens"). Cause was local, not upstream:
arsgrammatica 0.11.2's `tokengraph_to_dot()` already quotes every id via
`arsgrammatica.dot._dot_id()`, so our older `quote_dot_token_ids()`
workaround re-quoted them to `""6.t97""` -- an empty quoted id followed by
a bare `6.t97`, i.e. the very lexing error it was written to prevent.

Removed `quote_dot_token_ids()` and its one call in the `dot_source` cell
(`reader.py` never had it). The `arsgrammatica>=0.11.2` pin already
guarantees the quoting: earlier versions aren't installable from the index
here anyway. The "arsgrammatica bug candidate" noted in the removed comment
is resolved upstream.

Verified: `marimo check` clean; the notebook's own `dot_source` cell run for
all 17 sentences renders through `dot -Tsvg` with no warnings or errors
(17/17; previously 17/17 failed).

## 2026-09-23 (cont.): LM info display -- drop Context, render Reasoning as Markdown

User had hand-added a "Show language model details" checkbox + display
(`show_lm_info`/`lm_info_display`) to both notebooks since my last edits
to this section -- confirmed by re-reading both files fresh before
touching anything, per the established safe-edit workflow, rather than
assuming their prior state. Asked for two changes to that display:
drop the `CONTEXT=` field (redundant -- it's just the selected
sentence's own citation span) and render `REASONING=`'s content as
Markdown rather than plain escaped text.

Checked arsgrammatica's `serialization.py` module docstring/`LMInfo`
directly (not just assuming) to confirm: `REASONING=`'s value is
free-form prose that `_collapse_to_single_line()` flattens to one line
on write (newlines/paragraph breaks -> single spaces) but otherwise
leaves untouched -- so any Markdown syntax within that one line (bold,
italic, code spans, links, etc.) survives a round trip through
write_analyses()/read_analyses() intact; it just can't contain block-
level constructs that depend on being on their own line.

Edited the `lm_info_display` cell identically in both `reader.py` and
`reader_w_graphviz.py`: dropped the `<p><b>Context</b>: ...` line
entirely; kept the Model line exactly as before (still
`html.escape()`d into `mo.Html(...)`, unchanged); and replaced the
Reasoning line's `html.escape()`-into-`<p>` with
`mo.md(f"**Reasoning**: {selected_lm_info.reasoning}")` (falling back
to the same "(not recorded)" `mo.Html` when reasoning is empty), wrapped
together with the Model line in `mo.vstack([...])` since `mo.callout`
takes one element.

Verified, not just asserted: `marimo check` on both files (no errors);
and, since no file in this repo's own `data/`/`public/` actually carries
a `#!lm` block right now to test against live, a synthetic check
reproducing the cell's exact logic against a fake `LMInfo` with
Markdown-bearing reasoning (`**cano**`, `*I sing*`, `` `arma` ``) --
confirmed in the real rendered output that those became actual
`<strong>`/`<em>`/`<code>` elements (not literal asterisks/backticks),
that the `Aeneid 1.1.t0-...` context string appears nowhere in the
output, and that the `reasoning=None`/`model=None` "(not recorded)"
fallback still renders correctly.

## 2026-09-23 (cont.): Larger font for plaintext_html in reader_w_graphviz.py

User asked, for `reader_w_graphviz.py` only (their own words: "I've got
reader_w_graphviz.py looking the way I want with one exception"), to
make the `plaintext_html` passage-text display a little larger than
regular body text. Re-read the file fresh before editing, per the usual
workflow.

Wrapped the cell's existing content in `<span style='font-size:
1.15em;'>...</span>` rather than a fixed px value, so it scales with
whatever the surrounding body text size actually is (theme/zoom-
independent) instead of being pinned to an absolute size. Left the
label's `<b><i>Passage text</i></b>` prefix and the `html.escape()`
call on the passage text itself untouched -- only added the wrapping
span.

Verified: `marimo check` clean; and a direct render against a real
sentence from `public/analyses/` (not a synthetic one) confirms the
full line -- label and escaped passage text together -- comes back
wrapped in the new span, e.g. `<span style='font-size:
1.15em;'><b><i>Passage text</i></b>: si quid est in me ingeni,
iudices, ...</span>`.

Note: did not touch `reader.py`'s own `plaintext_html` cell, which is
still worded identically without the size bump -- the user's request
was scoped to `reader_w_graphviz.py` specifically.

## 2026-09-23 (cont.): Reorganized reader.py to match reader_w_graphviz.py's layout

User asked to reorganize `reader.py` "to work just like `reader_w_graphviz.py`"
(minus graphviz, obviously). Re-read both files completely fresh first --
reader_w_graphviz.py had diverged substantially through the user's own
live hand-editing over the last several turns (sentence-vetting feature,
`public/analyses/` restructure, the accordion-based layout from the
last few turns' consultations, the larger plaintext_html font, the
vuhtml div-wrap fix). Found that the underlying data-loading/logic
layer (ANALYSES_DIR, is_remote_location/read_location_text/
resolve_readable_path, the manifest-driven analysis_paths, vetted_by_context/
sentence_status_warning, sentence_dropdown, selected_tokengraph/
selected_lm_info) was ALREADY identical between the two files -- the
user had apparently kept that part in sync themselves. The actual gap
was entirely in the *display* layer.

Ported into `reader.py`, verified against reader_w_graphviz.py's exact
current text:

- Replaced the old flat cluster of separate header/display cells
  ("## Selected text", "## Highlighted by verbal units", "## Diagram
  syntactic relations" headers; standalone `plaintext_html`/
  `show_lm_info`/`vuhtml`/`diagram_tool`/`diagram_display`/
  `diagram_download` cells) with the new accordion-based layout:
  `mo.accordion({"## Language model's comments": lm_info_display})`,
  `plaintext_html` and `maxdepth` still bare, `mo.accordion({"##
  Formatted text": mo.vstack([mo.hstack([vuhtml]), mo.md("###
  Indented..."), indentpsg])})`, and `mo.accordion({"## Diagrams":
  mo.vstack([diagram_tool, mo.Html(f"<div style='overflow-x: auto;
  max-width: 100%;'>{diagram_display}</div>"), diagram_download])})` --
  the last one including the horizontal-scroll fix from a couple turns
  ago, since without it a wide Mermaid/displaCy diagram would get
  clipped by the accordion's own `overflow: hidden` the same way it did
  in reader_w_graphviz.py before that fix.
- Moved `diagram_display`'s construction out of that display cluster
  (it used to build-and-bare-display itself in one cell) into its own
  construct-only cell (`return (diagram_display,)`, no bare display),
  positioned right after the "# Implementation" header -- matching
  where reader_w_graphviz.py now keeps it. Kept reader.py's own existing
  comment (mermaid/displaCy only, pointing to reader_w_graphviz.py for
  the graphviz option) rather than porting graphviz-specific wording.
- Dropped the `show_lm_info` checkbox cell entirely and removed its
  gating from `lm_info_display`'s construction (now shows whenever a
  sentence's LM info exists) -- reader_w_graphviz.py still has an
  orphaned, unused `show_lm_info` checkbox cell (dead code: nothing
  reads it any more, since the accordion itself is now the show/hide
  control), which looked like leftover from live experimentation rather
  than an intentional design choice, so I didn't propagate it.
- `plaintext_html`: added the `font-size: 1.15em` span (this had only
  been asked for in `reader_w_graphviz.py` a couple turns ago; porting
  it here since "work just like" now covers it).
- `vuhtml`: wrapped in a single `<div>` and dropped the `<i>` italic tag
  around "Highlighted by verbal unit", matching reader_w_graphviz.py's
  current wording exactly (the div-wrap is the fix for vstack's
  every-word-stacks bug from a couple turns ago).

Deliberately did NOT port two things from reader_w_graphviz.py that
looked like accidental leftovers rather than intended changes, and
should be confirmed with the user rather than silently copied:
1. Its status-display cell has the old working line commented out
   (`#status_display = mo.vstack(status_parts + [vetted_only,
   sentence_dropdown])`) replaced by one that drops `status_parts`
   entirely (`status_display = mo.vstack([vetted_only,
   sentence_dropdown])`) -- meaning the "N sentences loaded" message
   and any read-error/warning callouts never actually display any more
   in reader_w_graphviz.py, even though they're still computed.
   reader.py keeps its own current (uncommented, fully working) version.
2. Its `<hr/>` cell between "## Diagrams" and "# Implementation" is
   duplicated (two identical cells back to back) -- reader.py keeps
   just one.

Verified: `marimo check` clean; `app.run()` against real `public/`
data -- 17 sentences, 1 vetted, `diagram_tool.options` correctly
`{mermaid, displacy}` only (no graphviz), `diagram_display` populated,
`show_lm_info` no longer in `defs` at all; direct construction of
`plaintext_html`/`vuhtml` against a real sentence confirms the new
span/div wrapping shows up with real content, not just empty
placeholders; and a full `marimo export html-wasm --mode run --execute
-f` on the restructured file completes cleanly end to end.
