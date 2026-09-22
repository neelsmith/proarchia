# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "arsgrammatica",
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
    # Review the Pro Archia syntax analyses
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    > No LM access needed, and nothing to browse for -- every analysis file
    > (the format `write_analyses()` produces) already saved in `data/` is
    > loaded automatically, in citation order, as soon as this notebook
    > opens. Pick one sentence below and inspect it.
    """)
    return


@app.cell(hide_code=True)
def _(mo, analysis_paths, read_error, read_warnings, sentence_dropdown, sentences, split_error):
    if read_error is not None:
        analysis_status = mo.callout(mo.md(f"Could not load any analyses: {read_error}"), kind="danger")
    elif split_error is not None:
        analysis_status = mo.callout(
            mo.md(f"Could not split the loaded analyses by sentence: {split_error}"),
            kind="danger",
        )
    else:
        analysis_status = mo.md(
            f"## Sentence selection\n\n"
            f"*{len(sentences)} sentence(s) loaded from {len(analysis_paths)} file(s) in `data/`.*"
        )

    if read_warnings:
        warnings_callout = mo.callout(
            mo.md("Some files could not be read and were skipped:\n\n" + "\n".join(f"- {w}" for w in read_warnings)),
            kind="warn",
        )
        mo.vstack([analysis_status, warnings_callout, sentence_dropdown])
    else:
        mo.vstack([analysis_status, sentence_dropdown])
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
def _(mo):
    mo.md("""
    ## Highlighted by verbal units
    """)
    return


@app.cell(hide_code=True)
def _(maxdepth):
    maxdepth
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
def _(
    diagram,
    diagram_tool,
    displacy_svg,
    displacy_warnings,
    dot_source,
    dot_warnings,
    graphviz,
    mo,
):
    # Same two failure modes to degrade visibly from as arsgrammatica's own
    # marimo/latin_syntaxer_review.py, which this cell is copied from
    # unchanged: diagram_tool's own options only ever offer "graphviz" when
    # graphviz_available is True, so the only failure actually reachable
    # here is the `dot` executable itself missing from PATH
    # (graphviz.ExecutableNotFound) -- not the graphviz package being
    # absent, which would instead just leave "graphviz" off the radio's
    # options entirely. displaCy needs neither check: displacy_svg is
    # already a complete, ready-to-display SVG string the moment it's
    # computed, same as tokengraph_to_mermaid()'s own diagram text.
    if diagram_tool.value == "graphviz":
        try:
            svg_bytes = graphviz.Source(dot_source).pipe(format="svg")
            diagram_display = mo.vstack(
                [mo.Html(svg_bytes.decode("utf-8"))]
                + (
                    [mo.callout(mo.md("\n".join(f"- {w}" for w in dot_warnings)), kind="warn")]
                    if dot_warnings
                    else []
                )
            )
        except graphviz.ExecutableNotFound:
            diagram_display = mo.callout(
                mo.md(
                    "The `graphviz` package is installed, but the Graphviz "
                    "`dot` command itself isn't on your system's PATH -- "
                    "install Graphviz separately (e.g. `brew install "
                    "graphviz` on macOS, `apt install graphviz` on Linux), "
                    "or switch back to *Mermaid* above."
                ),
                kind="warn",
            )
    elif diagram_tool.value == "displacy":
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
    mo.md("""
    ## Reduction to AAT graph
    """)
    return


@app.cell(hide_code=True)
def _(aat_display):
    aat_display
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
def _(Path):
    # Where arsgrammatica's own review notebook lets the user browse for a
    # single analysis file, this one always reads every one already saved
    # in this project's own `data/` directory -- see notes/project.md --
    # so there's no file_browser widget here at all.
    DATA_DIR = Path(__file__).parent.parent / "data"
    return (DATA_DIR,)


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
def _(DATA_DIR, analysis_sort_key):
    analysis_paths = sorted(DATA_DIR.glob("*.cex"), key=analysis_sort_key) if DATA_DIR.is_dir() else []
    return (analysis_paths,)


@app.cell
def _(analysis_paths, read_analyses):
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
            _tokengraph, _verbalunits, _sentences, _lm_infos = read_analyses(str(_path))
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
    if not analysis_paths:
        read_error = "No analysis files (*.cex) found in data/."
    elif not sentences:
        read_error = "Found analysis files in data/, but none could be read -- see the warnings below."
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
# Label one menu entry as "<n>. <citation>: <first six words>…" -- numbered
# so entries are always unique even when several sentences share (or lack)
# a citation, or happen to start with the same words.
def sentence_label(index, citation, sentence_tokengraph, tokengraph_to_text):
    preview_text = tokengraph_to_text(sentence_tokengraph)
    words = preview_text.split()
    preview = " ".join(words[:6])
    ellipsis = "…" if len(words) > 6 else ""
    prefix = f"{citation}: " if citation else ""
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
def _(sentence_dropdown, sentence_slices, sentences):
    # The currently selected sentence's own tokengraph/verbalunits slice --
    # empty until a sentence is actually picked, which every rendering
    # utility below already handles gracefully (an empty diagram/string).
    # selected_citation rides along for the diagram download's filename
    # below -- pulled from the Sentence's own first Token, same source
    # sentence_label()'s own menu-entry citation comes from.
    selected_tokengraph, selected_verbalunits = [], []
    selected_citation = None
    selected_sentence = None
    if sentence_dropdown.value is not None and 0 <= sentence_dropdown.value < len(sentence_slices):
        selected_tokengraph, selected_verbalunits = sentence_slices[sentence_dropdown.value]
        selected_sentence = sentences[sentence_dropdown.value]
        selected_citation = selected_sentence.tokens[0].citation if selected_sentence.tokens else None
    return (
        selected_citation,
        selected_sentence,
        selected_tokengraph,
        selected_verbalunits,
    )


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
def _(graphviz_available, mo):
    # "graphviz" is only ever offered as a choice when the graphviz PyPI
    # package actually imported successfully above. This can't rule out
    # the OTHER failure mode (the package installed but the `dot`
    # executable missing from PATH), which is why diagram_display still
    # has to handle graphviz.ExecutableNotFound even though this list is
    # filtered. "displacy" is always offered, unlike "graphviz" -- it has
    # no external dependency to check for at all.
    diagram_tool = mo.ui.radio(
        options=["mermaid", "graphviz", "displacy"] if graphviz_available else ["mermaid", "displacy"],
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
def _(depth, selected_tokengraph, tokengraph_to_dot):
    # Cheap to always compute regardless of which tool is currently
    # selected -- tokengraph_to_dot() is pure string building, unlike
    # actually rendering it, which needs the graphviz package and the
    # `dot` executable (handled in diagram_display above).
    dot_source, dot_warnings = tokengraph_to_dot(selected_tokengraph, aat_depth=depth)
    return dot_source, dot_warnings


@app.cell
def _(depth, selected_tokengraph, tokengraph_to_displacy_svg):
    # Cheap to always compute regardless of which tool is currently
    # selected, same reasoning as dot_source above -- but unlike
    # dot_source, tokengraph_to_displacy_svg() has no external dependency
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
    dot_source,
    mo,
    selected_tokengraph,
):
    # Downloads whichever diagram is currently selected/displayed above,
    # not both -- a reactive "follows the widget" convention. Mermaid and
    # Graphviz sources are saved raw, as .mmd/.dot -- both renderable
    # elsewhere without needing this notebook. displaCy's own output is
    # ALREADY a rendered picture (an SVG string), so its download is the
    # .svg itself.
    if diagram_tool.value == "graphviz":
        diagram_download = mo.download(
            data=dot_source.encode("utf-8"),
            filename=f"{diagram_filename_stem}_dot.dot",
            label="Download Graphviz DOT source (.dot)",
            mimetype="text/plain",
            disabled=not selected_tokengraph,
        )
    elif diagram_tool.value == "displacy":
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
def _(mo, selected_tokengraph, tokengraph_to_text):
    # Plain, uncolored text -- tokengraph_to_text() never emits HTML, but
    # the underlying surface text is still escaped before going into
    # mo.Html().
    import html as _html

    plaintext_html = mo.Html(
        "<b><i>Passage text</i></b>: " + _html.escape(tokengraph_to_text(selected_tokengraph))
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


@app.cell
def _(depth, filter_tokengraph_by_aat_depth, selected_tokengraph):
    # Filter the selected sentence's own tokengraph to the SAME depth
    # cutoff the Mermaid/Graphviz diagrams and HTML displays above use,
    # BEFORE building the AAT graph from it below.
    aat_tokengraph = filter_tokengraph_by_aat_depth(selected_tokengraph, depth)
    return (aat_tokengraph,)


@app.cell
def _(
    SimpleNamespace,
    aat_available,
    aat_tokengraph,
    aatgraph,
    graph_to_mermaid,
    selected_sentence,
    selected_verbalunits,
):
    # Build the AAT (Agent-Action-Target) graph for just the currently
    # selected sentence, limited to the depth cutoff above -- aatgraph()
    # takes (sentences, results) in analyze_sources()'s own shape, so a
    # one-element list of each is enough here.
    aat_diagram = None
    aat_warnings = []
    if aat_available and aat_tokengraph and selected_sentence is not None:
        result = SimpleNamespace(tokengraph=aat_tokengraph, verbalunits=selected_verbalunits)
        graph, aatgraph_warnings = aatgraph([selected_sentence], [result])
        aat_diagram, aat_mermaid_warnings = graph_to_mermaid(graph)
        aat_warnings = aatgraph_warnings + aat_mermaid_warnings
    return aat_diagram, aat_warnings


@app.cell
def _(aat_available, aat_diagram, aat_warnings, mo):
    if not aat_available:
        aat_display = mo.callout(
            mo.md(
                "The `aat` package isn't installed, so the AAT "
                "(Agent-Action-Target) graph can't be built here."
            ),
            kind="warn",
        )
    elif aat_diagram is None:
        aat_display = mo.md("*Choose a sentence above to see its AAT (Agent-Action-Target) graph.*")
    else:
        aat_display = mo.vstack(
            [mo.md("**AAT (Agent-Action-Target) graph**"), mo.mermaid(aat_diagram)]
            + (
                [mo.callout(mo.md("\n".join(f"- {w}" for w in aat_warnings)), kind="warn")]
                if aat_warnings
                else []
            )
        )
    return (aat_display,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Imports
    """)
    return


@app.cell
def _():
    from pathlib import Path
    from types import SimpleNamespace

    from arsgrammatica import (
        aatgraph,
        filter_tokengraph_by_aat_depth,
        max_subordination_depth,
        read_analyses,
        split_analysis_by_sentence,
        tokengraph_to_depth_html,
        tokengraph_to_displacy_svg,
        tokengraph_to_dot,
        tokengraph_to_html,
        tokengraph_to_mermaid,
        tokengraph_to_text,
    )

    # aatgraph() (above) is always importable from arsgrammatica -- it only
    # raises when actually CALLED without the separate `aat` package
    # installed. graph_to_mermaid() -- aat's own Mermaid renderer for the
    # AATGraph aatgraph() builds -- has no such fallback, so its import is
    # what actually detects whether `aat` is installed at all; the AAT
    # display cells below check aat_available rather than calling either
    # function and catching ImportError themselves.
    try:
        from aat.core import graph_to_mermaid

        aat_available = True
    except ImportError:
        graph_to_mermaid = None
        aat_available = False

    # graphviz (the PyPI package -- a thin subprocess wrapper around the
    # separately-installed Graphviz `dot` executable) is optional: checked
    # once here rather than every display cell catching ImportError
    # itself. Whether the `dot` executable is actually on PATH is a
    # SEPARATE check (graphviz.ExecutableNotFound), made only when a
    # diagram is actually rendered -- see the diagram_display cell above.
    try:
        import graphviz

        graphviz_available = True
    except ImportError:
        graphviz = None
        graphviz_available = False
    return (
        Path,
        SimpleNamespace,
        aat_available,
        aatgraph,
        filter_tokengraph_by_aat_depth,
        graph_to_mermaid,
        graphviz,
        graphviz_available,
        max_subordination_depth,
        read_analyses,
        split_analysis_by_sentence,
        tokengraph_to_depth_html,
        tokengraph_to_displacy_svg,
        tokengraph_to_dot,
        tokengraph_to_html,
        tokengraph_to_mermaid,
        tokengraph_to_text,
    )


if __name__ == "__main__":
    app.run()
