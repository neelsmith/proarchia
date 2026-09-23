# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "arsgrammatica>=0.11.2",
# ]
# ///

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Cicero, *Pro Archia*
    """)
    return


@app.cell(hide_code=True)
def _(
    analysis_paths,
    mo,
    read_error,
    read_warnings,
    sentence_dropdown,
    sentences,
    split_error,
):
    if read_error is not None:
        analysis_status = mo.callout(mo.md(f"Could not load any analyses: {read_error}"), kind="danger")
    elif split_error is not None:
        analysis_status = mo.callout(
            mo.md(f"Could not split the loaded analyses by sentence: {split_error}"),
            kind="danger",
        )
    else:
        analysis_status = mo.md(
            f"## Select a sentence\n\n"
            f"*{len(sentences)} sentence(s) loaded from {len(analysis_paths)} file(s) in `public/analyses/`.*"
        )

    if read_warnings:
        warnings_callout = mo.callout(
            mo.md("Some files could not be read and were skipped:\n\n" + "\n".join(f"- {w}" for w in read_warnings)),
            kind="warn",
        )
        status_display = mo.vstack([analysis_status, warnings_callout, sentence_dropdown])
    else:
        status_display = mo.vstack([analysis_status, sentence_dropdown])

    # A cell only ever displays a bare top-level expression as its last
    # statement -- the vstack() calls above are built inside an if/else, so
    # (unlike arsgrammatica's own marimo/latin_syntaxer_review.py, which
    # only ever has ONE unconditional vstack() as its literal last
    # statement) they have to be assigned to a name first and referenced
    # again here, or nothing renders at all: no status line, and no
    # sentence-selection menu.
    status_display
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Selected text
    """)
    return


@app.cell(hide_code=True)
def _(plaintext_html):
    plaintext_html
    return


@app.cell(hide_code=True)
def _(show_lm_info):
    show_lm_info
    return


@app.cell(hide_code=True)
def _(lm_info_display):
    lm_info_display
    return


@app.cell(hide_code=True)
def _(maxdepth):
    maxdepth
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Highlighted by verbal units
    """)
    return


@app.cell(hide_code=True)
def _(vuhtml):
    vuhtml
    return


@app.cell(hide_code=True)
def _(indentpsg, mo):
    mo.accordion({"***Fold/unfold passage indented by verbal unit***": indentpsg})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Diagram syntactic relations
    """)
    return


@app.cell(hide_code=True)
def _(diagram_tool):
    diagram_tool
    return


@app.cell(hide_code=True)
def _(diagram, diagram_tool, displacy_svg, displacy_warnings, mo):
    # displaCy needs no external dependency at all: displacy_svg is
    # already a complete, ready-to-display SVG string the moment it's
    # computed, same as tokengraph_to_mermaid()'s own diagram text. (See
    # reader_w_graphviz.py for a version of this notebook that also offers
    # Graphviz as a third diagram tool.)
    if diagram_tool.value == "displacy":
        diagram_display = mo.vstack(
            [mo.Html(displacy_svg)]
            + (
                [mo.callout(mo.md("\n".join(f"- {w}" for w in displacy_warnings)), kind="warn")]
                if displacy_warnings
                else []
            )
        )
    else:
        diagram_display = mo.mermaid(diagram)

    diagram_display
    return


@app.cell(hide_code=True)
def _(diagram_download):
    diagram_download
    return


@app.cell(hide_code=True)
def _(mo):
    mo.Html("<hr/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Implementation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Loading the saved analyses
    """)
    return


@app.cell
def _(mo):
    # Where arsgrammatica's own review notebook lets the user browse for a
    # single analysis file, this one always reads every one already saved
    # for this project -- see notes/project.md -- so there's no
    # file_browser widget here at all. `public/analyses/` (see
    # is_remote_location() below) holds a snapshot of this project's `data/` directory, kept in
    # sync by utilities/generate_public_manifest.py -- see that script's own
    # docstring for why reading goes through a manifest file rather than
    # a directory listing.
    # `marimo export html-wasm` only copies `public/` itself (with all
    # its subdirectories) next to the exported notebook, so the
    # analyses have to live somewhere under it.
    ANALYSES_DIR = mo.notebook_location() / "public" / "analyses"
    return (ANALYSES_DIR,)


@app.function
# `mo.notebook_location()` resolves correctly in both contexts this
# notebook runs in: a real local `pathlib.Path` when run natively
# (`marimo edit`/`marimo run`, or `uv run --sandbox`), and the
# notebook's own hosted URL -- wrapped in marimo's `URLPath`, a bare
# `pathlib.PurePosixPath` with none of `Path`'s filesystem methods
# (`.open()`/`.is_dir()`/`.glob()` all raise `AttributeError` on it) --
# when exported with `marimo export html-wasm` and loaded in a browser.
# `str(p)` contains "://" only in that second case (`URLPath.__str__` is
# written specifically to preserve it), so that's the one reliable,
# public-API-only way to tell which kind we were handed.
def is_remote_location(path):
    return "://" in str(path)


@app.function
# Read the text content at `path`, whether it's a real local path (plain
# `open()`) or a URL under Pyodide. `urllib.request` is what
# `pd.read_csv(str(mo.notebook_location() / "public" / "data.csv"))`
# relies on in marimo's own docs for `notebook_location()` -- Pyodide
# transparently proxies it through the browser's own `fetch()` for
# same-origin requests, so this works unmodified in the browser too.
def read_location_text(path):
    if is_remote_location(path):
        import urllib.request

        with urllib.request.urlopen(str(path)) as response:
            return response.read().decode("utf-8")
    else:
        return path.read_text(encoding="utf-8")


@app.function
# arsgrammatica's read_analyses() only ever does a plain local
# `open(path)` -- it has no idea about URLs -- so under Pyodide we can't
# just hand it `path` directly. Fetch the content ourselves instead and
# stash it in a real local tempfile (Pyodide's virtual filesystem
# supports normal reads/writes under /tmp, so this works unmodified in
# the browser too), then hand read_analyses() that tempfile's path.
# Locally this is a no-op passthrough -- read_analyses() already gets a
# real local path there.
def resolve_readable_path(path):
    if not is_remote_location(path):
        return str(path)

    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cex", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(read_location_text(path))
        return tmp.name


@app.function
# Files are named like "..._tokenized_<n>_...cex" -- <n> is each file's own
# place in the passage's reading order (1, 2, 3, ...), not necessarily its
# position in a plain alphabetical sort (which would put "_10" before "_2").
# Sorting on this number keeps sentences in citation order regardless of
# how many files there are or what else their names contain; a name
# without that pattern sorts after every one that has it, by name.
def analysis_sort_key(path):
    import re

    match = re.search(r"tokenized_(\d+)", path.name)
    return (0, int(match.group(1))) if match else (1, path.name)


@app.cell
def _(ANALYSES_DIR, json):
    manifest_error = None
    try:
        manifest_names = json.loads(read_location_text(ANALYSES_DIR / "manifest.json"))
    except (OSError, ValueError) as e:
        manifest_names = []
        manifest_error = str(e)

    analysis_paths = sorted((ANALYSES_DIR / name for name in manifest_names), key=analysis_sort_key)
    return analysis_paths, manifest_error


@app.cell
def _(analysis_paths, manifest_error, read_analyses):
    # Read every file and concatenate their (tokengraph, verbalunits,
    # sentences, lm_infos) in file order -- token ids are unique per
    # sentence's own citation context, so concatenating rather than
    # merging is enough (see combined_tokengraph() in arsgrammatica's own
    # pipeline.py for the same convention with freshly-analyzed results).
    # A single bad file becomes a warning, not a reason to show nothing --
    # read_error is reserved for the case where nothing could be loaded
    # at all.
    tokengraph, verbalunits, sentences, lm_infos = [], [], [], []
    read_warnings = []
    for _path in analysis_paths:
        try:
            _tokengraph, _verbalunits, _sentences, _lm_infos = read_analyses(resolve_readable_path(_path))
        except (ValueError, OSError) as e:
            read_warnings.append(f"{_path.name}: {e}")
            continue
        tokengraph.extend(_tokengraph)
        verbalunits.extend(_verbalunits)
        sentences.extend(_sentences)
        # lm_infos is [] whenever a file has no '#!lm' block at all (see
        # read_analyses()'s own docstring) -- pad so it stays aligned with
        # sentences/tokengraph/verbalunits position-for-position even when
        # some files carry '#!lm' and others don't.
        lm_infos.extend(_lm_infos if _lm_infos else [None] * len(_sentences))

    read_error = None
    if manifest_error is not None:
        read_error = f"Could not read public/analyses/manifest.json: {manifest_error}"
    elif not analysis_paths:
        read_error = "No analysis files listed in public/analyses/manifest.json."
    elif not sentences:
        read_error = "Found analysis files in public/analyses/manifest.json, but none could be read -- see the warnings below."
    return lm_infos, read_error, read_warnings, sentences, tokengraph, verbalunits


@app.cell
def _(sentences, split_analysis_by_sentence, tokengraph, verbalunits):
    # split_analysis_by_sentence() gives us each sentence's own tokengraph/
    # verbalunits slice out of the combined, whole-project flat lists --
    # see arsgrammatica/serialization.py -- so the rest of this notebook
    # only ever has to think about "the currently selected sentence's own
    # data", same as arsgrammatica's own marimo/latin_syntaxer_review.py.
    sentence_slices = []
    split_error = None
    if sentences:
        try:
            sentence_slices = split_analysis_by_sentence(tokengraph, verbalunits, sentences)
        except ValueError as e:
            split_error = str(e)
    return sentence_slices, split_error


@app.function
# The sentence-style identifier arsgrammatica writes as each '#!lm'
# block's CONTEXT= value: "<citation>.<id>-<citation>.<id>" for the
# sentence's own first and last token (see LMInfo's docstring and
# _sentence_context_identifier() in arsgrammatica/serialization.py --
# private there, so re-derived here). None for a sentence with no tokens.
def sentence_context_id(sentence):
    if not sentence.tokens:
        return None
    first, last = sentence.tokens[0], sentence.tokens[-1]
    return f"{first.citation}.{first.id}-{last.citation}.{last.id}"


@app.cell
def _(lm_infos):
    # Every loaded '#!lm' entry, keyed by its own CONTEXT= value, so the
    # selected sentence's entry is found by what it actually identifies
    # rather than by position alone (lm_infos is padded with None for
    # files lacking a '#!lm' block, so position still works as a
    # fallback -- see selected_lm_info below).
    lm_by_context = {info.context: info for info in lm_infos if info is not None and info.context}
    return (lm_by_context,)


@app.function
# Label one menu entry as "<n>. <citation>: <first six words>…" -- numbered
# so entries are always unique even when several sentences share (or lack)
# a citation, or happen to start with the same words.
def sentence_label(index, citation, sentence_tokengraph, tokengraph_to_text):
    preview_text = tokengraph_to_text(sentence_tokengraph)
    words = preview_text.split()
    preview = " ".join(words[:6])
    ellipsis = "…" if len(words) > 6 else ""
    # citation is a full CTS URN, e.g.
    # "urn:cts:latinLit:phi0474.phi016.omar:1" -- show just its passage
    # component (the part after the last colon, "1") rather than the
    # whole URN. rsplit's maxsplit=1 leaves a citation with no colon at
    # all unchanged, so this degrades gracefully for a non-URN citation.
    passage = citation.rsplit(":", 1)[-1] if citation else None
    prefix = f"{passage}: " if passage else ""
    return f"{index + 1}. {prefix}{preview}{ellipsis}"


@app.cell
def _(mo, sentence_slices, sentences, tokengraph_to_text):
    # Menu for selecting a sentence, across every file that was loaded.
    # Maps each label directly to that sentence's own index, so
    # sentence_dropdown.value is an int usable to index into
    # sentence_slices below -- zip() with sentences stops at whichever
    # list is shorter, so a split_analysis_by_sentence() failure
    # (sentence_slices left empty, sentences possibly not) can't produce a
    # mismatched, out-of-range index here.
    sentence_options = {}
    if sentence_slices:
        for i, (sentence, (sentence_tokengraph, _sentence_verbalunits)) in enumerate(
            zip(sentences, sentence_slices)
        ):
            citation = sentence.tokens[0].citation if sentence.tokens else None
            sentence_options[sentence_label(i, citation, sentence_tokengraph, tokengraph_to_text)] = i

    sentence_dropdown = mo.ui.dropdown(
        options=sentence_options,
        label="*Sentence*:",
    )
    return (sentence_dropdown,)


@app.cell
def _(lm_by_context, lm_infos, sentence_dropdown, sentence_slices, sentences):
    # The currently selected sentence's own tokengraph/verbalunits slice --
    # empty until a sentence is actually picked, which every rendering
    # utility below already handles gracefully (an empty diagram/string).
    # selected_citation rides along for the diagram download's filename
    # below -- pulled from the Sentence's own first Token, same source
    # sentence_label()'s own menu-entry citation comes from.
    selected_tokengraph, selected_verbalunits = [], []
    selected_citation = None
    selected_sentence = None
    selected_lm_info = None
    if sentence_dropdown.value is not None and 0 <= sentence_dropdown.value < len(sentence_slices):
        selected_tokengraph, selected_verbalunits = sentence_slices[sentence_dropdown.value]
        selected_sentence = sentences[sentence_dropdown.value]
        selected_citation = selected_sentence.tokens[0].citation if selected_sentence.tokens else None
        # Match on CONTEXT first; fall back to the positionally aligned
        # entry only if no '#!lm' block names this sentence at all.
        selected_lm_info = lm_by_context.get(sentence_context_id(selected_sentence))
        if selected_lm_info is None and sentence_dropdown.value < len(lm_infos):
            selected_lm_info = lm_infos[sentence_dropdown.value]
    return selected_citation, selected_lm_info, selected_tokengraph


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Format output display
    """)
    return


@app.cell
def _(max_subordination_depth, mo, selected_tokengraph):
    # A slider bounding the diagrams and HTML displays below to a chosen
    # depth -- sits upstream of every consumer (both diagrams, both HTML
    # displays, and the depth-filtered AAT graph). None until a sentence
    # with at least one token is selected.
    maxdepth = None
    if selected_tokengraph:
        maxdepth = mo.ui.slider(
            start=0,
            stop=max_subordination_depth(selected_tokengraph),
            label="*Maximum depth of subordination to display*:",
            show_value=True,
            value=max_subordination_depth(selected_tokengraph),
        )
    return (maxdepth,)


@app.cell
def _(maxdepth):
    # Shared by every viz cell below (the Mermaid diagram, the Graphviz DOT
    # diagram, both HTML displays, and the depth-filtered AAT graph) --
    # computed once here rather than re-deriving the same "maxdepth can be
    # None before a sentence is selected" guard in each of them.
    depth = maxdepth.value if maxdepth is not None else None
    return (depth,)


@app.cell
def _(mo):
    # Off by default: the model/context/reasoning recorded in each
    # sentence's '#!lm' block is shown only on request.
    show_lm_info = mo.ui.checkbox(label="*Show language model details*", value=False)
    return (show_lm_info,)


@app.cell
def _(html, mo, selected_lm_info, selected_tokengraph, show_lm_info):
    lm_info_display = mo.md("")
    if show_lm_info.value and selected_tokengraph:
        if selected_lm_info is None:
            lm_info_display = mo.callout(
                mo.md("No `#!lm` information was recorded for this sentence."), kind="neutral"
            )
        else:
            def _field(value):
                return html.escape(value) if value else "<i>(not recorded)</i>"

            lm_info_display = mo.callout(
                mo.Html(
                    f"<p><b>Model</b>: <code>{_field(selected_lm_info.model)}</code></p>"
                    f"<p><b>Context</b>: <code>{_field(selected_lm_info.context)}</code></p>"
                    f"<p><b>Reasoning</b>: {_field(selected_lm_info.reasoning)}</p>"
                ),
                kind="info",
            )
    return (lm_info_display,)


@app.cell
def _(mo):
    diagram_tool = mo.ui.radio(
        options=["mermaid", "displacy"],
        value="mermaid",
        inline=True,
        label="*Diagram tool*:",
    )
    return (diagram_tool,)


@app.cell
def _(depth, selected_tokengraph, tokengraph_to_mermaid):
    diagram, mermaid_warnings = tokengraph_to_mermaid(selected_tokengraph, aat_depth=depth)
    return (diagram,)


@app.cell
def _(depth, selected_tokengraph, tokengraph_to_displacy_svg):
    # Cheap to always compute regardless of which tool is currently
    # selected -- tokengraph_to_displacy_svg() has no external dependency
    # at all, so this is already a complete, ready-to-display SVG string.
    displacy_svg, displacy_warnings = tokengraph_to_displacy_svg(selected_tokengraph, aat_depth=depth)
    return displacy_svg, displacy_warnings


@app.cell
def _(selected_citation, sentence_dropdown):
    # The sentence's own 1-based menu number goes first (matching
    # sentence_label()'s "<n>. ..." prefix) so every download gets a
    # distinct, stable name even across sentences that share (or lack) a
    # citation.
    diagram_filename_stem = "sentence"
    if sentence_dropdown.value is not None:
        raw = f"{sentence_dropdown.value + 1}_{selected_citation or ''}"
        diagram_filename_stem = "".join(c if c.isalnum() else "_" for c in raw).strip("_") or "sentence"
    return (diagram_filename_stem,)


@app.cell
def _(
    diagram,
    diagram_filename_stem,
    diagram_tool,
    displacy_svg,
    mo,
    selected_tokengraph,
):
    # Downloads whichever diagram is currently selected/displayed above,
    # not both -- a reactive "follows the widget" convention. Mermaid
    # source is saved raw, as .mmd -- renderable elsewhere without needing
    # this notebook. displaCy's own output is ALREADY a rendered picture
    # (an SVG string), so its download is the .svg itself.
    if diagram_tool.value == "displacy":
        diagram_download = mo.download(
            data=displacy_svg.encode("utf-8"),
            filename=f"{diagram_filename_stem}_displacy.svg",
            label="Download displaCy-style diagram (.svg)",
            mimetype="image/svg+xml",
            disabled=not selected_tokengraph,
        )
    else:
        diagram_download = mo.download(
            data=diagram.encode("utf-8"),
            filename=f"{diagram_filename_stem}_mermaid.mmd",
            label="Download Mermaid diagram (.mmd)",
            mimetype="text/plain",
            disabled=not selected_tokengraph,
        )
    return (diagram_download,)


@app.cell
def _(html, mo, selected_tokengraph, tokengraph_to_text):
    # Plain, uncolored text -- tokengraph_to_text() never emits HTML, but
    # the underlying surface text is still escaped before going into
    # mo.Html().
    plaintext_html = mo.Html(
        "<b><i>Passage text</i></b>: " + html.escape(tokengraph_to_text(selected_tokengraph))
    )
    return (plaintext_html,)


@app.cell
def _(depth, mo, selected_tokengraph, tokengraph_to_html):
    vuhtml = mo.Html(
        "<b><i>Highlighted by verbal unit</i></b>: " + tokengraph_to_html(selected_tokengraph, depth=depth)
    )
    return (vuhtml,)


@app.cell
def _(depth, mo, selected_tokengraph, tokengraph_to_depth_html):
    indenthtml, indentwarnings = tokengraph_to_depth_html(selected_tokengraph, depth=depth)
    indentpsg = mo.Html(indenthtml)
    return (indentpsg,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Imports
    """)
    return


@app.cell
def _():
    import html
    import json

    from arsgrammatica import (
        max_subordination_depth,
        read_analyses,
        split_analysis_by_sentence,
        tokengraph_to_depth_html,
        tokengraph_to_displacy_svg,
        tokengraph_to_html,
        tokengraph_to_mermaid,
        tokengraph_to_text,
    )

    return (
        html,
        json,
        max_subordination_depth,
        read_analyses,
        split_analysis_by_sentence,
        tokengraph_to_depth_html,
        tokengraph_to_displacy_svg,
        tokengraph_to_html,
        tokengraph_to_mermaid,
        tokengraph_to_text,
    )


if __name__ == "__main__":
    app.run()
