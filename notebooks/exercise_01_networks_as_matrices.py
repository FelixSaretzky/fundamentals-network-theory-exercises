# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.1",
#     "matplotlib",
#     "numpy",
#     "pandas",
#     "wigglystuff>=0.5.33",
#     "marimo-lens>=0.2.3; sys_platform != 'emscripten'",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    return mo, np, pd, plt


@app.cell
async def widgets():
    # Drawing widget. In the browser the package is installed on the fly, also when
    # the notebook is reopened from a saved link on marimo.app.
    import sys

    if sys.platform == "emscripten":
        import micropip

        await micropip.install("wigglystuff")
    from wigglystuff import GraphWidget

    return (GraphWidget,)


@app.cell(hide_code=True)
def intro(mo):
    mo.md(r"""
    # Exercise 1: Networks as matrices

    *Fundamentals of Network Theory*, University of Luxembourg, winter semester 2026/27.
    Lectures A2 to A4 (one question also uses walks, A6). We discuss this notebook in the
    exercise session on **Monday 26.10.2026**, and the quiz in that session builds on it.

    You turn three kinds of networks into matrices and read them:

    1. three toy networks and their eigenvalues (A2, A3),
    2. who writes emails to whom among the executives of Enron (A3),
    3. which hacker groups use which attack techniques (A4).

    **Three markers.**

    - ⚙️ **Given.** Context, and code you do not have to change.
    - ❓ **Question.** Think first, then write your answer into the answer cell right
      below it: double-click the text *Your answer*, write, then click outside the cell.
      One to three sentences are enough.
    - ✏️ **Task.** Code you write below `# TODO: your code goes here`, in place of the line
      `raise NotImplementedError(...)`. Where it helps, the task states a **target** value,
      so that you can check your result yourself. Function names in the tasks link to
      their documentation.

    **One rule of marimo.** Every name can be defined in one cell only, otherwise the
    notebook stops with an error. For helpers you would reuse in several cells, such as
    loop variables or a temporary matrix, use names that start with an underscore (`_i`,
    `_M`): they stay local to their cell.

    There are no automatic checks. In the session we discuss your answers, the wrong ones
    included: a wrong answer you can explain teaches more than a copied right one. Be
    ready to explain any line of your code in the session.

    Plan about four to five hours. Save and submit as in Exercise 0, see Section 5.
    """)
    return


@app.cell(hide_code=True)
def save_warning(mo):
    mo.callout(
        mo.md(r"""
        **Your work lives only in this browser tab.** Reloading or closing the tab deletes
        every edit, even after `Ctrl+S`.

        - Press `Ctrl+S` (`Cmd+S` on a Mac) often, and **export your file** before you stop
          (Section 5 shows how).
        - Need a break? `Ctrl+S`, then menu → **Share** → **Create WebAssembly link**, and
          keep the link. It restores your work on marimo.app.
        - Links to the documentation open in a new tab; this tab stays as it is.
        """),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1  Warm-up: what eigenvalues tell you about a network (A2, A3)

    ⚙️ **Given.** Three small networks. Edges are listed as pairs, nodes are labelled
    from 1 as in the lecture.

    - `STAR`, **undirected**: a hub with three clients.
    - `RING`, **directed**: three servers pass a token around, $1 \to 2 \to 3 \to 1$.
    - `CITES`, **directed**: five papers, where the pair $(j, i)$ means *paper $j$ cites
      paper $i$*. A paper can only cite older papers.

    Lecture A3 defines the adjacency matrix of an undirected network by
    $A_{ij} = 1$ if there is an edge between $i$ and $j$, and of a **directed** network by

    $$A_{ij} = \begin{cases} 1 & \text{if there is an edge from node } j \text{ to node } i\\
    0 & \text{otherwise.}\end{cases}$$

    Mind the order: the column is where the edge starts, the row is where it ends.
    """)
    return


@app.cell
def toy_networks():
    STAR = [(1, 2), (1, 3), (1, 4)]
    RING = [(1, 2), (2, 3), (3, 1)]
    CITES = [(4, 3), (3, 5), (5, 1), (3, 1), (1, 2), (5, 2)]
    return CITES, RING, STAR


@app.cell(hide_code=True)
def draw_toys(CITES, GraphWidget, RING, STAR, mo):
    def _draw(edges, n, directed):
        return mo.ui.anywidget(
            GraphWidget(
                nodes=[str(_k) for _k in range(1, n + 1)],
                edges=[(str(_j), str(_i)) for _j, _i in edges],
                directed=directed,
                height=220,
            )
        )

    mo.hstack(
        [
            mo.vstack([mo.md("**STAR**, undirected"), _draw(STAR, 4, False)]),
            mo.vstack([mo.md("**RING**, directed"), _draw(RING, 3, True)]),
            mo.vstack([mo.md("**CITES**, directed"), _draw(CITES, 5, True)]),
        ],
        widths="equal",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.1.** Complete `adjacency_matrix(edges, n, directed)` in the convention of
    lecture A3. For `directed=False` every edge sets two entries. Remember that lecture
    label $i$ is numpy index `i - 1`.

    **Target:** `A_star` is symmetric with row sums $(3, 1, 1, 1)$. The row sums of
    `A_cites` are $(2, 2, 1, 0, 1)$: the number of times each paper is cited.
    """)
    return


@app.cell
def task_1_1(CITES, RING, STAR, np):
    def adjacency_matrix(edges, n, directed=False):
        """Adjacency matrix in the convention of lecture A3, nodes labelled 1 to n."""
        # TODO: your code goes here
        raise NotImplementedError("Task 1.1: build the n x n adjacency matrix")

    A_star = adjacency_matrix(STAR, 4)
    A_ring = adjacency_matrix(RING, 3, directed=True)
    A_cites = adjacency_matrix(CITES, 5, directed=True)
    A_star, A_ring, A_cites
    return A_cites, A_ring, A_star


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.1.** Guess before you compute, from the drawings alone: which of the
    three networks has eigenvalues that are not real numbers? Which one has only the
    eigenvalue $0$? Give a reason for each guess in one sentence.
    """)
    return


@app.cell(hide_code=True)
def answer_1_1(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.2.** Compute the eigenvalues of the three matrices with
    [`np.linalg.eigvals`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigvals.html) and store them in the dictionary `eigenvalues`, in place of the
    empty lists. The cell after it draws them in the complex plane. numpy may print every
    eigenvalue in complex form: `1.732+0.j` has imaginary part 0 and is a real number,
    compare the plot.

    **Target:** the star has the eigenvalues $\pm\sqrt{3} \approx \pm 1.732$ and $0$ twice.
    """)
    return


@app.cell
def task_1_2(A_cites, A_ring, A_star, np):
    # TODO: your code goes here
    eigenvalues = {"STAR": [], "RING": [], "CITES": []}  # replace each [] by the eigenvalues
    eigenvalues
    return (eigenvalues,)


@app.cell(hide_code=True)
def eigenvalue_plot(eigenvalues, np, plt):
    _fig, _axes = plt.subplots(1, 3, figsize=(9, 3.2), sharex=True, sharey=True)
    _t = np.linspace(0, 2 * np.pi, 200)
    for _ax, (_name, _values) in zip(_axes, eigenvalues.items()):
        _values = np.asarray(_values, dtype=complex)
        _ax.plot(np.cos(_t), np.sin(_t), color="0.85", lw=1)
        _ax.axhline(0, color="0.6", lw=0.8)
        _ax.axvline(0, color="0.6", lw=0.8)
        _ax.scatter(_values.real, _values.imag, s=60, zorder=3)
        _ax.set_title(_name)
        _ax.set_xlabel("real part")
        _ax.set_aspect("equal")
    _axes[0].set_ylabel("imaginary part")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.2.** A fellow student computed by hand that
    $\mathbf{v} = (0, 1, -1, 0)^T$ is an eigenvector of `A_star` for $\lambda = 0$. But
    [`np.linalg.eig(A_star)`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html) prints other eigenvectors for $\lambda = 0$. Who is right? Use
    Task 1.3 to decide, and explain.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.3.** Check two things in code: (a) is $\mathbf{A}\mathbf{v} = 0\cdot\mathbf{v}$?
    (b) Let `V0` hold the eigenvectors that numpy returns for $\lambda \approx 0$, as
    columns. Does adding $\mathbf{v}$ as a further column raise the rank
    ([`np.linalg.matrix_rank`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html))?
    """)
    return


@app.cell
def task_1_3(A_star, np):
    v = np.array([0, 1, -1, 0])
    # TODO: your code goes here
    raise NotImplementedError("Task 1.3: check v against numpy's eigenvectors")
    return


@app.cell(hide_code=True)
def answer_1_2(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Given.** Lecture A3: a directed network is acyclic if and only if its nodes can
    be numbered so that every edge points from a higher to a lower number. With such a
    numbering, $A_{ij} = 0$ for all $i \geq j$: the matrix is *strictly upper triangular*.

    ✏️ **Task 1.4.** (a) Find such a numbering for `CITES`: write the paper labels into
    `order`, oldest paper first (`order[0]` is the label of the oldest paper), and reorder
    rows and columns of `A_cites` with it.
    Tip: [`np.ix_`](https://numpy.org/doc/stable/reference/generated/numpy.ix_.html) reorders rows and columns at once,
    `M[np.ix_(idx, idx)]`, whereas `M[idx, idx]` picks single entries only.
    (b) Compute the powers $\mathbf{A}^k$ of `A_cites` for $k = 1, \dots, 6$
    ([`np.linalg.matrix_power`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_power.html)) and find the smallest $k$ with $\mathbf{A}^k = \mathbf{0}$.

    **Target for (a):** `np.array_equal(A_sorted, np.triu(A_sorted, k=1))` is `True`
    (see [`np.triu`](https://numpy.org/doc/stable/reference/generated/numpy.triu.html) and [`np.array_equal`](https://numpy.org/doc/stable/reference/generated/numpy.array_equal.html)).
    """)
    return


@app.cell
def task_1_4(A_cites, np):
    # TODO: your code goes here
    order = []  # paper labels, oldest paper first
    raise NotImplementedError("Task 1.4: reorder the papers and compute the matrix powers")
    A_sorted, np.array_equal(A_sorted, np.triu(A_sorted, k=1)), smallest_k
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.3.** All eigenvalues of `A_cites` are $0$. (a) Is `A_cites` therefore
    the zero matrix? (b) In one sentence: why does the triangular form of Task 1.4 show
    that every eigenvalue is $0$? (Question 4.2 asks for the full proof.) (c) What is the smallest $k$ with $\mathbf{A}^k = \mathbf{0}$, and what does it
    tell you about the drawing? Hint for (c): $[\mathbf{A}^k]_{ij}$ counts the walks of
    length $k$ from $j$ to $i$ (lecture A6).
    """)
    return


@app.cell(hide_code=True)
def answer_1_3(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2  Who writes to whom? The Enron email network (A3)

    ⚙️ **Given.** Enron was a large US energy company that collapsed in an accounting
    scandal in December 2001. During the investigation, the emails of its staff were made
    public. We use the emails among **149 executives and employees**, November 1998 to
    June 2002.

    - `people`: `id`, `name`, `title`. The `id` runs from 0 to 148 and is directly the
      row and column index in numpy, no shift this time.
    - `emails`: one row per ordered pair: `emails` is the number of emails that `sender`
      sent to `recipient` over the whole period. Some people sent emails to themselves,
      then `sender == recipient`.
    """)
    return


@app.cell
def data_folder(mo, pd):
    # Where the CSV files are. On the exercise site they sit next to the notebook. Opened
    # anywhere else (a saved WebAssembly link on marimo.app, molab, your own laptop), the
    # notebook loads them from the exercise site, which needs an internet connection.
    import pathlib

    _site = "https://felixsaretzky.github.io/fundamentals-network-theory-exercises/notebooks/public/"
    _here = mo.notebook_location()
    if isinstance(_here, pathlib.Path):  # Python on a computer
        DATA = f"{_here / 'public'}/" if (_here / "public").is_dir() else _site
    else:  # Python in the browser
        _url = str(_here)
        _next_to_notebook = any(_host in _url for _host in ("felixsaretzky.github.io", "localhost", "127.0.0.1"))
        DATA = f"{_url}/public/" if _next_to_notebook else _site

    def read_csv(name):
        """Read one CSV file of this exercise, in the browser or on a computer."""
        import sys

        if sys.platform == "emscripten":
            # In the browser, fetch the text first: GitHub Pages sends the files compressed,
            # and pandas would try to unpack them a second time.
            from pyodide.http import open_url

            return pd.read_csv(open_url(DATA + name))
        return pd.read_csv(DATA + name)

    return (read_csv,)


@app.cell
def enron_data(read_csv):
    people = read_csv("enron_people.csv")
    emails = read_csv("enron_emails.csv")
    n_people = len(people)
    NAME = people["name"].tolist()
    return NAME, emails, n_people, people


@app.cell(hide_code=True)
def enron_tables(emails, mo, people):
    mo.hstack(
        [
            mo.vstack([mo.md("`people`"), mo.ui.table(people, page_size=8)]),
            mo.vstack([mo.md("`emails`"), mo.ui.table(emails, page_size=8)]),
        ],
        widths="equal",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.1.** Row $i$ of $\mathbf{A}$ belongs to person $i$. In the convention
    of lecture A3, does row $i$ mark the people who wrote **to** $i$, or the people $i$
    wrote to? Which is therefore the in-degree $k_i^{\text{in}}$: the row sum or the column
    sum? Careful: many libraries, networkx for example, store the matrix the other way
    round.
    """)
    return


@app.cell(hide_code=True)
def answer_2_1(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.1.** Build the unweighted adjacency matrix `A` of the email network: a
    $149 \times 149$ array of 0 and 1 in the convention of lecture A3, with $A_{ij} = 1$
    if person $j$ sent at least one email to person $i$. We study a **simple** network:
    no self-edges. The cell starts from a matrix of zeros for you to fill, and shows the
    three target values below.

    **Target:** $m$ = `A.sum()` = **2604** arcs, the largest row sum of `A` is **48** and
    the largest column sum is **84**.
    """)
    return


@app.cell
def task_2_1(emails, n_people, np):
    A = np.zeros((n_people, n_people), dtype=int)
    # TODO: your code goes here
    # fill A here: lecture A3 convention, no self-edges
    int(A.sum()), int(A.sum(axis=1).max()), int(A.sum(axis=0).max())
    return (A,)


@app.cell(hide_code=True)
def enron_matrix_plot(A, plt):
    _fig, _ax = plt.subplots(figsize=(4.2, 4.2))
    _ax.spy(A, markersize=1.2)
    _ax.set_title("A: a dot where column j wrote to row i", fontsize=9)
    _ax.set_xlabel("sender j")
    _ax.set_ylabel("recipient i")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.2 (a).** Build the undirected version `U` of `A`, with $U_{ij} = 1$ if
    $A_{ij} = 1$ or $A_{ji} = 1$ (Question 2.2 needs it too). Then count:

    - `m_undirected`: pairs $\{i, j\}$ with an email in at least one direction.
      **Target: 1788.**
    - `m_mutual`: pairs with emails in both directions.
    - `reciprocity` $= 2\,m_{\text{mutual}} / m$, the share of arcs whose reverse arc
      also exists.
    """)
    return


@app.cell
def task_2_2(A):
    # TODO: your code goes here
    raise NotImplementedError("Task 2.2 (a): undirected edges and mutual pairs")
    {"m_undirected": int(m_undirected), "m_mutual": int(m_mutual), "reciprocity": float(reciprocity)}
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.2 (b).** Compute the arrays `k_in` and `k_out`, and the names of everyone
    with $k^{\text{in}} = 0$ (`no_incoming`) and with $k^{\text{out}} = 0$ (`no_outgoing`).
    Tip: [`np.flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html) returns the
    indices of the nonzero (or `True`) entries.
    """)
    return


@app.cell
def task_2_2b(A, NAME, np):
    # TODO: your code goes here
    raise NotImplementedError("Task 2.2 (b): degrees, and who has no incoming or no outgoing emails")
    {"no_incoming": no_incoming, "no_outgoing": no_outgoing}
    return k_in, k_out


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.2.** A classmate says: *"The sum of all entries of an adjacency matrix
    is twice the number of edges."* Check it on `A` and on its undirected version
    $U_{ij} = 1$ if $A_{ij} = 1$ or $A_{ji} = 1$. When is the claim right, and why?
    """)
    return


@app.cell(hide_code=True)
def answer_2_2(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.3.** Make three small tables with name, title, `k_in` and `k_out`: the five
    people with the highest in-degree (`top_in`), the five with the highest out-degree
    (`top_out`), and everyone with the title `CEO` (`ceos`). Tip: [`people.assign(...)`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.assign.html) adds
    columns, [`DataFrame.nlargest`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nlargest.html) picks the
    rows with the largest values.
    """)
    return


@app.cell
def task_2_3(k_in, k_out, mo, people):
    # TODO: your code goes here
    raise NotImplementedError("Task 2.3: top receivers, top senders, CEOs")
    mo.vstack([top_in, top_out, ceos])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.3.** Is the person who receives emails from the most colleagues also
    the most senior one? Compare $k^{\text{in}}$ and $k^{\text{out}}$ of the CEOs: who
    writes to far more colleagues than write to them (largest ratio
    $k^{\text{out}} / k^{\text{in}}$)? Suggest an explanation, and say what data you would
    need to test it. (Context: Kenneth Lay chaired the whole company and was also its CEO,
    except from February to August 2001, when Jeffery Skilling (spelled so in the data) was; David Delainey and
    John Lavorato were CEOs of divisions.)
    """)
    return


@app.cell(hide_code=True)
def answer_2_3(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.4.** Compute the cocitation matrix $\mathbf{C} = \mathbf{A}\mathbf{A}^T$ and
    the bibliographic coupling matrix $\mathbf{A}^T\mathbf{A}$ (A3; we call it `Bib` here,
    because Section 3 needs the letter $\mathbf{B}$). In this network $C_{ij}$ counts the
    people who wrote to both $i$ and $j$, and $\text{Bib}_{ij}$ the people both $i$ and $j$
    wrote to. For each matrix, find the pair $i \neq j$ with the largest entry: names and
    value. If several pairs tie for the largest value, give all of them. Tip: set the
    diagonal of a copy `_M` to $-1$, then use `np.unravel_index(_M.argmax(), _M.shape)`
    (see [`np.unravel_index`](https://numpy.org/doc/stable/reference/generated/numpy.unravel_index.html) and [`argmax`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.argmax.html)).
    """)
    return


@app.cell
def task_2_4(A, NAME, np):
    # TODO: your code goes here
    raise NotImplementedError("Task 2.4: cocitation and bibliographic coupling")
    top_cocitation, top_coupling
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.4.** (a) What does $C_{ii}$ count? Check it for one person in your
    data. (b) A classmate stores the matrix the networkx way, `A_nx[sender, recipient] = 1`,
    and computes `A_nx @ A_nx.T`. Which of the two matrices of lecture A3 did they get?
    """)
    return


@app.cell(hide_code=True)
def answer_2_4(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3  Hacker groups and their techniques: a bipartite network (A4)

    ⚙️ **Given.** [MITRE ATT&CK](https://attack.mitre.org) is a public knowledge base that
    security teams use worldwide. From incident reports it records which **techniques**
    (for example *Phishing*, T1566) each known **threat actor** (for example *APT28*) has
    used. Our file `uses` has one row per pair: 172 actors, 203 techniques
    (sub-techniques count as their parent technique), ATT&CK version 19.2.

    Lecture A4 stores a bipartite network in the **incidence matrix** $\mathbf{B}$
    ($g \times n$), with $B_{ij} = 1$ if node $j$ belongs to group $i$. Here the threat
    actors are the $n$ nodes and the techniques are the $g$ groups: $B_{ij} = 1$ if actor
    $j$ uses technique $i$. Rows follow `TECHNIQUES`, columns follow `ACTORS`.

    <small>© 2026 The MITRE Corporation. This work is reproduced and distributed with the
    permission of The MITRE Corporation. License: see `public/DATA_SOURCES.md`.</small>
    """)
    return


@app.cell
def attack_data(read_csv):
    uses = read_csv("attack_uses.csv")
    ACTORS = sorted(uses["actor"].unique(), key=str.lower)
    TECHNIQUES = sorted(uses["technique_id"].unique())
    TECHNIQUE_NAME = dict(zip(uses["technique_id"], uses["technique"]))
    uses
    return ACTORS, TECHNIQUES, TECHNIQUE_NAME, uses


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.1.** Build the incidence matrix `B`. Tip: first build two dictionaries,
    actor name to column index and technique id to row index, for example with
    `enumerate(ACTORS)` and `enumerate(TECHNIQUES)`.

    **Target:** `B.shape` is $(203, 172)$, `B.sum()` is **3726**, and the first column
    (actor `admin@338`) sums to **12**.
    """)
    return


@app.cell
def task_3_1(ACTORS, TECHNIQUES, np, uses):
    # TODO: your code goes here
    raise NotImplementedError("Task 3.1: build the incidence matrix B")
    B.shape, int(B.sum())
    return (B,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.2.** Compute the one-mode projection onto the actors,
    $\mathbf{P} = \mathbf{B}^T\mathbf{B}$, and the projection onto the techniques,
    $\mathbf{P}' = \mathbf{B}\mathbf{B}^T$ (A4). Find:

    - the pair of actors $i \neq j$ with the largest $P_{ij}$, and that value,
    - the five actors with the largest $P_{ii}$,
    - the technique with the largest $P'_{ii}$, by name.
    """)
    return


@app.cell
def task_3_2(ACTORS, B, TECHNIQUES, TECHNIQUE_NAME, np):
    # TODO: your code goes here
    raise NotImplementedError("Task 3.2: the two one-mode projections")
    top_actor_pair, largest_actors, most_used
    return (P,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 3.1.** What does $P_{ii}$ count? And which information does
    $\mathbf{P}$ lose that $\mathbf{B}$ still has?
    """)
    return


@app.cell(hide_code=True)
def answer_3_1(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 3.2.** Look at the two actors of your top pair in $\mathbf{P}$ and at
    their repertoires $P_{ii}$. Does a large $P_{ij}$ show that two actors are closely
    related, for example the same team? Decide with Task 3.3.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.3.** Normalise the overlap: $J_{ij} = P_{ij} / (P_{ii} + P_{jj} - P_{ij})$
    is the share of shared techniques among all techniques that $i$ or $j$ use (the
    *Jaccard index*). Consider only actors with $P_{ii} \geq 10$, because with few known
    techniques the share is noisy. Find the pair $i \neq j$ with the largest $J_{ij}$,
    and report $J_{ij}$ and $P_{ij}$ for it. A double loop over the actors is fine; name its loop
    variables `_a`, `_b` (see the marimo rule at the top).
    """)
    return


@app.cell
def task_3_3(ACTORS, P, np):
    # TODO: your code goes here
    raise NotImplementedError("Task 3.3: Jaccard overlap of the actors")
    top_jaccard_pair
    return


@app.cell(hide_code=True)
def answer_3_2(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4  Wrap-up

    ❓ **Question 4.1.** Which of these matrices are symmetric: `A_star`, `A_ring`,
    `A_cites`, the Enron `A`, `C`, `Bib`, the ATT&CK `B`, `P`? For each one that is not,
    give the reason in a few words.
    """)
    return


@app.cell(hide_code=True)
def answer_4_1(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 4.2: two short proofs.** Write them into the answer cell below; Markdown
    and LaTeX work as in the lecture notes. A few lines each are enough.

    1. If a directed network has no cycle, all eigenvalues of $\mathbf{A}$ are $0$.
       (Hint: Task 1.4, and the determinant of a triangular matrix.)
    2. The directed ring with $n$ nodes has the $n$-th roots of unity,
       $e^{2\pi i k / n}$ for $k = 0, \dots, n-1$, as eigenvalues. (Hint: compute
       $\mathbf{A}^n$. For the converse, check that the vector with entries
       $x_j = \omega^{-j}$ is an eigenvector for every $n$-th root of unity $\omega$.)
    """)
    return


@app.cell(hide_code=True)
def answer_4_2(mo):
    mo.md(r"""
    **Your proofs.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5  Save and submit

    ⚙️ **Given.** The same steps as in Exercise 0.

    1. Press `Ctrl+S` (`Cmd+S` on a Mac). Without this step the export is an empty file.
    2. Menu (round button with three lines, top right) → **Export…** → tab **Python** →
       **Export notebook source**.
    3. Rename the downloaded `notebook.py` to `exercise01_<lastname>.py`.
    4. On Moodle, assignment **Exercise 1**: **Add submission**, drag in the file,
       **Save changes**, then **Submit assignment** and confirm. The status must read
       **Submitted for grading**. The deadline is on Moodle.

    Need a break? `Ctrl+S`, then menu → **Share** → **Create WebAssembly link**, and keep
    the link: it restores your work on marimo.app. A reload of this page loses every edit.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Sources.** Enron data: C. E. Priebe, J. M. Conroy, D. J. Marchette, Y. Park,
    *Scan Statistics on Enron Graphs*, Computational and Mathematical Organization Theory
    11 (2005), from the email corpus released by the US Federal Energy Regulatory
    Commission. Threat actors and techniques: MITRE ATT&CK Enterprise 19.2. The questions
    of Section 2 follow an idea of the course ECE 442 *Network Science Analytics*
    (G. Mateos, University of Rochester).
    """)
    return


if __name__ == "__main__":
    app.run()
