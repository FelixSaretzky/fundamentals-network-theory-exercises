# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.0",
#     "numpy",
#     "wigglystuff>=0.5.32",
#     "marimo-lens>=0.2.3; sys_platform != 'emscripten'",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import numpy as np

    def pmatrix(matrix):
        """LaTeX source of a matrix, to be placed inside mo.md."""
        _rows = [" & ".join(f"{_x:g}" for _x in _row) for _row in np.asarray(matrix)]
        return r"\begin{pmatrix}" + r" \\ ".join(_rows) + r"\end{pmatrix}"

    return mo, np


@app.cell
async def widgets():
    # Drawing widgets. Kept apart from the imports above, so that the tasks still
    # run if the widgets cannot load. In the browser the package is installed on
    # the fly, also when the notebook is reopened from a saved link on marimo.app.
    import sys

    if sys.platform == "emscripten":
        import micropip

        await micropip.install("wigglystuff")
    from wigglystuff import CellTour, GraphWidget

    return CellTour, GraphWidget


@app.cell(hide_code=True)
def intro(mo):
    mo.md(r"""
    # Exercise 0: Getting started

    *Fundamentals of Network Theory*, University of Luxembourg, winter semester 2026/27.
    Practice run on Monday 05.10.2026. We work through it together in class, and it
    counts 0 percent.

    This notebook rehearses the full workflow of the exercises: open the page, solve the
    tasks, check your results, save, export, upload on Moodle, take a short quiz. The
    example comes from lecture A3, the adjacency matrix.

    **Four cell types. The marker always comes first.**

    - ⚙️ **Given.** Context, and code you do not have to touch.
    - ❓ **Question N.** A guess you record in a variable before you compute. In the
      graded exercises a guess counts for being submitted, not for being right.
    - ⇨ **Task N.** Code you write. The code cell below it carries
      `# TODO: your code goes here`.
    - ✅ **Check.** The self-test of the task above. It states the target value, asserts
      it and prints `✅ ... passed.`

    Every section runs the same rhythm: ⚙️ then ❓ then ⇨ then ✅. A marker may be
    skipped, the order never changes. Longer sections run the rhythm more than once.
    """)
    return


@app.cell(hide_code=True)
def how_it_works(mo):
    mo.md(r"""
    ## 0  How this notebook works

    ⚙️ **Given.** The whole page is one Python program, cut into cells.

    - **Run a cell** with `Ctrl+Enter` (`Cmd+Enter` on a Mac). `Shift+Enter` runs it and
      moves to the next cell. `Ctrl+K` (`Cmd+K`) opens the command palette.
    - **Reactivity.** When a cell runs, every cell that uses its variables runs again by
      itself. The order of the cells on the page does not matter.
    - **One home per variable.** A global name may be defined in one cell only. Names
      that start with an underscore, like `_x`, stay local to their cell.
    - **Save often** with `Ctrl+S` (`Cmd+S`). Section 2 explains why the export needs it.
    - Python runs inside your browser. Nothing is installed on your laptop, and your code
      is not sent to a server. A reload or closing the tab loses your edits, so export
      before you leave.
    """)
    return


@app.cell(hide_code=True)
def section0_tour(CellTour, mo):
    tour = mo.ui.anywidget(
        CellTour(
            steps=[
                {
                    "cell_name": "intro",
                    "title": "Four markers",
                    "description": "Every cell starts with one of four markers: Given, Question, Task, Check. Let us walk through one example.",
                },
                {
                    "cell_name": "data_a3",
                    "title": "Given: the data",
                    "description": "The network of lecture A3 as an edge list, plus the matrix from the slides. You read this, you do not change it.",
                },
                {
                    "cell_name": "draw_a3",
                    "title": "Given: the picture",
                    "description": "The same network as a drawing. You can drag the nodes.",
                },
                {
                    "cell_name": "question2",
                    "title": "Question: guess first",
                    "description": "Before you compute, write down a guess. Then run the cell with Ctrl+Enter (Cmd+Enter on a Mac).",
                },
                {
                    "cell_name": "task2_adjacency",
                    "title": "Task: your code",
                    "description": "Your code goes below the TODO line. Usually 1 to 5 lines.",
                },
                {
                    "cell_name": "task2_check",
                    "title": "Check: are you right?",
                    "description": "This cell tests your Task. A message that starts with ✅ means passed. If not, read the hint and fix your code.",
                },
                {
                    "cell_name": "a3_editor",
                    "title": "Reactivity",
                    "description": "Change an entry of the matrix. The drawing and the numbers below update by themselves.",
                },
                {
                    "cell_name": "submit_steps",
                    "title": "Save and submit",
                    "description": "At the end: Ctrl+S (Cmd+S), export as Python, rename the file, upload it on Moodle.",
                },
            ]
        )
    )
    mo.vstack(
        [
            mo.md("⚙️ **Given.** A guided tour through the example below. Click **Start Tour**."),
            tour,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1  A3: the adjacency matrix of an undirected network

    ⚙️ **Given.** The six-node network of lecture A3, as a list of edges $(i, j)$:

    $$(1,2),\ (1,5),\ (2,3),\ (2,4),\ (3,4),\ (3,5),\ (3,6)$$

    For an undirected, simple network (no multi-edges, no self-edges) lecture A3 defines

    $$A_{ij} = \begin{cases} 1 & \text{if there is an edge between nodes } i \text{ and } j\\
    0 & \text{otherwise.}\end{cases}$$

    The lecture numbers the nodes from 1, numpy counts rows and columns from 0. So
    $A_{ij}$ of the lecture is `A[i - 1, j - 1]` in numpy.
    """)
    return


@app.cell
def data_a3(np):
    # Edge list of the undirected network in lecture A3, nodes 1 to 6.
    EDGES_A3 = [(1, 2), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5), (3, 6)]

    # The adjacency matrix printed in lecture A3 for this network.
    A_LECTURE = np.array(
        [
            [0, 1, 0, 0, 1, 0],
            [1, 0, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 1],
            [0, 1, 1, 0, 0, 0],
            [1, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
        ]
    )
    return A_LECTURE, EDGES_A3


@app.cell(hide_code=True)
def draw_a3(EDGES_A3, GraphWidget, mo):
    mo.vstack(
        [
            mo.md("⚙️ **Given.** The same network as a drawing. You can drag the nodes."),
            mo.ui.anywidget(
                GraphWidget(
                    nodes=[str(_k) for _k in range(1, 7)],
                    edges=[(str(_i), str(_j)) for _i, _j in EDGES_A3],
                    directed=False,
                    height=260,
                )
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.** How many edges $m$ does this network have? And what will the sum of
    all entries of $\mathbf{A}$ be? Record both in `m_guess` and `sum_guess` before you
    run Task 1.
    """)
    return


@app.cell
def question2():
    # TODO: your code goes here
    m_guess = None  # a whole number
    sum_guess = None  # a whole number
    return m_guess, sum_guess


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✅ **Check.** Both guesses are recorded.
    """)
    return


@app.cell
def question2_check(m_guess, sum_guess):
    assert isinstance(m_guess, int) and isinstance(sum_guess, int), (
        "record two whole numbers in m_guess and sum_guess"
    )
    "✅ Question 1 recorded."
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⇨ **Task 1.** Complete `adjacency_matrix(edges, n)`. Start from
    `np.zeros((n, n), dtype=int)` and set two entries per edge, because the network is
    undirected. Mind the shift from lecture labels to numpy indices. Target: the matrix
    printed in A3, with row sums $(2, 3, 4, 2, 2, 1)$.
    """)
    return


@app.cell
def task2_adjacency(EDGES_A3, np):
    def adjacency_matrix(edges, n):
        """Adjacency matrix of a simple undirected network with nodes 1 to n."""
        # TODO: your code goes here
        raise NotImplementedError("Task 1: build the n x n adjacency matrix from the edge list")

    A_undirected = adjacency_matrix(EDGES_A3, 6)
    A_undirected
    return (A_undirected,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✅ **Check.** Symmetric, zero diagonal, all entries add up to 14, and equal to the
    matrix printed in A3.
    """)
    return


@app.cell
def task2_check(A_LECTURE, A_undirected, m_guess, np, sum_guess):
    _A = np.asarray(A_undirected)
    assert _A.shape == (6, 6), f"6 nodes give a 6 x 6 matrix, got shape {_A.shape}"
    assert np.array_equal(_A, _A.T), (
        "A is not symmetric. An undirected edge (i, j) sets A[i - 1, j - 1] and A[j - 1, i - 1]."
    )
    assert np.all(np.diag(_A) == 0), "the diagonal must be zero: this network has no self-edges"
    assert _A.sum() == 14, f"the entries should add up to 14, got {_A.sum()}"
    assert np.array_equal(_A, A_LECTURE), (
        "symmetric with the right total, but not the matrix of A3. Did you shift every label by one?"
    )
    f"✅ Task 1 passed: m = 7 edges, and the entries add up to 14 = 2m, because every edge appears twice, as A_ij and A_ji. Your guesses: m = {m_guess}, sum = {sum_guess}."
    return


@app.cell(hide_code=True)
def a3_editor(A_LECTURE, mo, np):
    A_editor = mo.ui.matrix(
        A_LECTURE,
        min_value=0,
        max_value=1,
        step=1,
        disabled=np.eye(6, dtype=bool),
        symmetric=True,
        row_labels=[str(_k) for _k in range(1, 7)],
        column_labels=[str(_k) for _k in range(1, 7)],
    )
    mo.vstack(
        [
            mo.md(r"""
            ⚙️ **Given.** Now change the network. Every entry of $\mathbf{A}$ below is a
            small slider from 0 to 1: drag it sideways, or double-click it and type. The
            network is undirected, so $A_{ij}$ and $A_{ji}$ change together. The diagonal
            is locked, because a simple network has no self-edges. The drawing and the
            numbers below follow every change.
            """),
            A_editor,
        ]
    )
    return (A_editor,)


@app.cell(hide_code=True)
def a3_editor_view(A_editor, GraphWidget, mo, np):
    _A = np.rint(np.asarray(A_editor.value)).astype(int)
    _edges = [
        (str(_i + 1), str(_j + 1))
        for _i in range(6)
        for _j in range(_i + 1, 6)
        if _A[_i, _j]
    ]
    mo.hstack(
        [
            mo.ui.anywidget(
                GraphWidget(
                    nodes=[str(_k) for _k in range(1, 7)],
                    edges=_edges,
                    directed=False,
                    height=260,
                )
            ),
            mo.md(rf"""
            - sum of all entries: **{_A.sum()}**
            - number of edges $m$: **{_A.sum() // 2}**
            - row sums: **{tuple(int(_r) for _r in _A.sum(axis=1))}**
            - symmetric: **{bool(np.array_equal(_A, _A.T))}**
            """),
        ],
        widths=[2, 1],
        align="center",
    )
    return


@app.cell(hide_code=True)
def submit_steps(mo):
    mo.md(r"""
    ## 2  Save and submit

    ⚙️ **Given.** The same steps close every exercise. Do them in this order.

    1. Press `Ctrl+S` (`Cmd+S` on a Mac). **Without this step the export below is an
       empty file.**
    2. Open the menu: the round button with three lines at the top right. Choose
       **Export…**.
    3. In the dialog **Export notebook**, open the tab **Python**. Keep the format
       **Notebook source** and click **Export notebook source**.
    4. Your browser downloads a file called `notebook.py`, for every exercise. Rename it
       to `exercise00_<lastname>.py`, for example `exercise00_lovelace.py`.
    5. On Moodle, course MICS2-7, open the assignment **Exercise 0 (practice)**. Click
       **Add submission**, drag your file into the box, then **Save changes**. The status
       now reads "Draft (not submitted)".
    6. Click **Submit assignment** and confirm. The status must read **Submitted for
       grading**. A draft that is never submitted does not count.

    Submit the `.py` file only, no PDF. The graded exercises use the same steps, with file
    names such as `exercise01_<lastname>.py`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md(r"""
        **Your work lives only in this browser tab.** A reload, or closing the tab, loses
        every edit, even after `Ctrl+S`. Only the downloaded `.py` file keeps your work.

        - Finish a session in one go. To continue later, open your `.py` file on your own
          laptop: `uvx --with numpy --with wigglystuff marimo edit exercise00_<lastname>.py`
          (this needs the tool `uv`). There, marimo saves your work automatically.
        - The Stop button does not work on this site. A cell that never ends needs a
          reload, which loses your work. Export before you try anything long.
        - Use Chrome or Firefox on a laptop, in a normal window (not private or
          incognito), not on a tablet or phone. The first load downloads the Python
          runtime, tens of MB.
        """),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Given.** After the upload we take the practice quiz on Moodle together. It has the
    format of the real quizzes: 9 questions with several statements each,
    every statement answered **Correct** or **Wrong**. In the real quizzes you work alone, with 30 minutes and one
    attempt, and you cannot go back to a previous statement.
    """)
    return


if __name__ == "__main__":
    app.run()
