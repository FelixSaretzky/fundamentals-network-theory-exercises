# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.2",
#     "matplotlib",
#     "numpy",
#     "pandas",
#     "scipy",
#     "marimo-lens>=0.2.4; sys_platform != 'emscripten'",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def imports():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components, shortest_path

    return connected_components, math, mo, np, pd, plt, shortest_path, sp


@app.cell(hide_code=True)
def intro(mo):
    mo.md(r"""
    # Exercise 2: How robust is a network?

    *Fundamentals of Network Theory*, University of Luxembourg, winter semester 2026/27.
    Lecture A6 (degrees, paths, components). We discuss this notebook in the exercise
    session on **Monday 9 November 2026**, and the quiz in that session builds on it.

    You compare two real networks of about the same size:

    - the **Internet** at the level of autonomous systems (AS): providers, universities and
      companies that exchange traffic, 6474 nodes;
    - the **power grid** of the western United States: generators, transformers and
      substations linked by high-voltage lines, 4941 nodes.

    Each section starts with a ⚙️ **practice question** that an operator of such a network
    would ask, and ends with a ❓ **decision** you have to justify with your results:

    1. Who are the critical nodes? (degrees)
    2. How far does something travel, and is there a way around a failure? (paths)
    3. What happens when nodes fail or are attacked? (components)

    **Three markers**, as in Exercise 1.

    - ⚙️ **Given.** Context, and code you do not have to change.
    - ❓ **Question.** Write your answer into the answer cell right below it: double-click
      the text *Your answer*, write, then click outside the cell. One to three sentences
      are enough, a proof needs a few lines.
    - ✏️ **Task.** Code you write below `# TODO: your code goes here`, in place of the line
      `raise NotImplementedError(...)`. Each task states a **target** for the Internet.
      Compute the power grid yourself: there is no target for it. Until a task is done,
      its cell and every cell that uses its result show an error. That is normal.

    **One rule of marimo.** Every name can be defined in one cell only. Helpers you would
    reuse, such as loop variables, get a leading underscore (`_i`, `_M`).

    There are no automatic checks. In the session we discuss your answers, the wrong ones
    included. Be ready to explain any line of your code.

    Plan about four hours. Save and submit as in Exercise 1, see Section 4.
    """)
    return


@app.cell(hide_code=True)
def save_warning(mo):
    mo.callout(
        mo.md(r"""
        **Your work lives only in this browser tab.** Reloading or closing the tab deletes
        every edit, even after `Ctrl+S`.

        - Press `Ctrl+S` (`Cmd+S` on a Mac) often, and **export your file** before you stop
          (Section 4 shows how).
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
    ## 1  Who are the critical nodes? Degrees (A6)

    ⚙️ **Practice question.** You are responsible for the security of one of the two
    networks and have the budget to protect a few nodes: DDoS protection for an AS, or
    physical protection for a substation. Which nodes do you pick? A first answer: the nodes
    with the most connections, that is, with the largest **degree**.

    ⚙️ **Given.** Two edge lists with the columns `u` and `v`. The node ids run from $0$ to
    $n-1$, so an id is directly a row and column index. The Internet data are the
    connections between ASes seen in the routing tables on 2 January 2000. The file is
    copied unchanged from the source, with all its quirks.
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
def load_data(read_csv):
    edges_as = read_csv("as_edges.csv")
    edges_power = read_csv("power_edges.csv")
    n_as = int(max(edges_as["u"].max(), edges_as["v"].max())) + 1
    n_power = int(max(edges_power["u"].max(), edges_power["v"].max())) + 1
    {"Internet (AS)": f"{n_as} nodes, {len(edges_as)} rows", "power grid": f"{n_power} nodes, {len(edges_power)} rows"}
    return edges_as, edges_power, n_as, n_power


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.1.** Complete `adjacency(edges, n)`: it returns the adjacency matrix of a
    **simple undirected** network as a sparse matrix of 0 and 1, symmetric, with no
    self-loops (lecture A6). A full $6474 \times 6474$ matrix would hold 42 million numbers,
    335 MB, too much for the browser; only 25144 of them are not zero. So store only those:
    build a [`sp.coo_array`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.coo_array.html)
    from `(data, (rows, columns))` with `shape=(n, n)`, make it symmetric, and turn it into
    a [`csr_array`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_array.html)
    with `.tocsr()`. Sparse matrices support `A + A.T`, `A > 0`, `.astype(int)`, `A.sum()`
    and `A @ B` much like numpy arrays. Use these *array* classes, not the older
    `coo_matrix` and `csr_matrix`, and keep the entries integers: Task 1.3 counts degrees
    with `np.bincount`, which accepts integers only.

    **Target:** for the Internet, `A_as.sum()` is **25144**. If you get 26467 or 27790,
    look at the rows with `u == v` again.
    """)
    return


@app.cell
def task_1_1(edges_as, edges_power, n_as, n_power, np, sp):
    def adjacency(edges, n):
        """Adjacency matrix of a simple undirected network, as a sparse 0/1 matrix."""
        # TODO: your code goes here
        raise NotImplementedError("Task 1.1: build the sparse adjacency matrix")

    A_as = adjacency(edges_as, n_as)
    A_power = adjacency(edges_power, n_power)
    int(A_as.sum()), int(A_power.sum())
    return A_as, A_power


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.2.** Compute the degree of every node as the arrays `k_as` and `k_power`,
    and the number of edges `m_as` and `m_power`. The table below then compares mean,
    median and maximum degree.

    **Target:** the Internet has $m = 12572$ edges, mean degree $3.88$ and maximum degree
    **1458**.
    """)
    return


@app.cell
def task_1_2(A_as, A_power, np, pd):
    # TODO: your code goes here
    raise NotImplementedError("Task 1.2: degrees and number of edges")
    pd.DataFrame(
        {
            "edges m": [m_as, m_power],
            "mean degree": [round(float(np.mean(k_as)), 2), round(float(np.mean(k_power)), 2)],
            "median degree": [float(np.median(k_as)), float(np.median(k_power))],
            "max degree": [int(np.max(k_as)), int(np.max(k_power))],
        },
        index=["Internet (AS)", "power grid"],
    )
    return k_as, k_power, m_as, m_power


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.1: a short proof.** Show that in a simple undirected network with $m$
    edges the degrees add up to $\sum_i k_i = 2m$ (*handshake lemma*, lecture A6). Conclude
    the formula for the mean degree, and check it on both networks: count the edges directly
    in the edge list (rows with $u \neq v$) and compare twice this number with the sum of the
    degrees from Task 1.2. One line of code in a new cell is enough.
    """)
    return


@app.cell(hide_code=True)
def answer_1_1(mo):
    mo.md(r"""
    **Your proof.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.3.** Compute the **degree distribution** of both networks: `p_as[k]` and
    `p_power[k]` are the fractions of nodes with degree $k$, for $k = 0, 1, 2, \dots$ up to
    the maximum degree.
    Tip: [`np.bincount`](https://numpy.org/doc/stable/reference/generated/numpy.bincount.html)
    counts how often each value occurs. The cell after it plots both distributions, once
    with linear axes and once with logarithmic axes.

    **Target:** for the Internet, `p_as[1]` is $0.368$: 37 % of all ASes have exactly one
    connection.
    """)
    return


@app.cell
def task_1_3(k_as, k_power, n_as, n_power, np):
    # TODO: your code goes here
    raise NotImplementedError("Task 1.3: degree distributions")
    p_as[:4].round(3), p_power[:4].round(3)
    return p_as, p_power


@app.cell(hide_code=True)
def degree_plot(np, p_as, p_power, plt):
    _fig, (_lin, _log) = plt.subplots(1, 2, figsize=(9, 3.4))
    for _p, _label in [(p_as, "Internet (AS)"), (p_power, "power grid")]:
        _k = np.flatnonzero(_p)
        _lin.plot(_k[_k <= 20], _p[_k[_k <= 20]], "o-", label=_label, ms=4)
        _log.loglog(_k[_k > 0], _p[_k[_k > 0]], "o", label=_label, ms=3)
    _lin.set(xlabel="degree $k$", ylabel="fraction of nodes $p_k$", title="linear axes, $k \\leq 20$")
    _log.set(xlabel="degree $k$", ylabel="$p_k$", title="logarithmic axes, all $k$")
    _lin.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.2.** Both mean degrees are below 4. A classmate concludes: *"The two
    networks are built alike: every node has about three connections."* What does the mean
    degree hide? Use the table of Task 1.2 and both plots.
    """)
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
    ✏️ **Task 1.4.** Back to the practice question: you may protect **1 % of the nodes**,
    rounded up, and you take the ones with the largest degree. The cell already picks them
    for you: [`math.ceil`](https://docs.python.org/3/library/math.html#math.ceil) rounds up,
    and [`np.argsort`](https://numpy.org/doc/stable/reference/generated/numpy.argsort.html)
    of `-k` with `kind="stable"` sorts by degree, ties by node id. Your part: complete
    `share_of_edges_touched(A, nodes)`, the fraction of all edges that have at least one end
    in `nodes`. Why edges? A node that fails takes all its connections with it. A protected
    node does not fail, so the share of edges touched tells you how much of the network
    depends on the nodes you protect. Tip: count the edges that touch **none** of them, in
    the submatrix of the other nodes, `A[keep][:, keep]` with a boolean array `keep`.

    **Target:** for the Internet, the 65 largest ASes touch **0.645** of all edges.
    """)
    return


@app.cell
def task_1_4(A_as, A_power, k_as, k_power, math, n_as, n_power, np):
    def share_of_edges_touched(A, nodes):
        """Fraction of all edges with at least one end in `nodes`."""
        # TODO: your code goes here
        raise NotImplementedError("Task 1.4: share of edges touched by the protected nodes")

    protect_as = np.argsort(-k_as, kind="stable")[: math.ceil(n_as / 100)]
    protect_power = np.argsort(-k_power, kind="stable")[: math.ceil(n_power / 100)]
    {
        "Internet (AS)": (len(protect_as), round(share_of_edges_touched(A_as, protect_as), 3)),
        "power grid": (len(protect_power), round(share_of_edges_touched(A_power, protect_power), 3)),
    }
    return (share_of_edges_touched,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.3: your decision.** In which network does protecting the 1 % of nodes with
    the largest degree pay off, and why? In the other network, what would you do with the
    budget instead?
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
    ## 2  How far does something travel, and is there a way around? Paths (A6)

    ⚙️ **Practice question.** A data packet crosses the Internet from AS to AS; a disturbance
    in the grid travels from line to line. How many steps lie between two nodes? And if one
    link fails, is there a short way around it?

    ⚙️ **Given.** Lecture A6: $[\mathbf{A}^r]_{ij}$ counts the sequences of $r$ steps along
    edges from $j$ to $i$. The lecture notes call them *paths of length $r$*, and the closed
    ones *loops*. Here we call them **walks**, as most textbooks do, because they may visit a
    node more than once; a **path** in the strict sense never does (the notes:
    *self-avoiding*). The shortest walk between two nodes is always such a path; its length
    is their **distance** (the notes: *geodesic distance*).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.1.** Complete two functions.

    - `triangles(A)`: the number of triangles, $\operatorname{tr}(\mathbf{A}^3) / 6$. Do not
      compute $\mathbf{A}^3$, it is far denser than $\mathbf{A}$. Use
      $\operatorname{tr}(\mathbf{A}^3) = \sum_{ij} [\mathbf{A}^2]_{ij} A_{ji}$ instead, with
      the elementwise product `(A @ A).multiply(A)` (for a symmetric $\mathbf{A}$, $A_{ji} = A_{ij}$).
      Careful: for sparse arrays, `*` and `**` act elementwise; the matrix product is `@`.
    - `detour_share(A)`: the fraction of edges $\{i, j\}$ that have a **detour of length
      2**, a third node linked to both $i$ and $j$. That is the case exactly when
      $[\mathbf{A}^2]_{ij} > 0$.

    **Target:** the Internet has **6584** triangles, and **0.506** of its edges have a
    detour of length 2.
    """)
    return


@app.cell
def task_2_1(A_as, A_power):
    def triangles(A):
        """Number of triangles of a simple undirected network, tr(A^3) / 6."""
        # TODO: your code goes here
        raise NotImplementedError("Task 2.1 (a): count the triangles")

    def detour_share(A):
        """Fraction of edges {i, j} with a common neighbour, a detour of length 2."""
        # TODO: your code goes here
        raise NotImplementedError("Task 2.1 (b): share of edges with a detour of length 2")

    {
        "Internet (AS)": (triangles(A_as), round(detour_share(A_as), 3)),
        "power grid": (triangles(A_power), round(detour_share(A_power), 3)),
    }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.1.** What does the diagonal entry $[\mathbf{A}^3]_{ii}$ count? Why is
    the trace divided by 6 and not by 3? And why does Task 2.1 go wrong if the self-loops
    of the Internet data are left in $\mathbf{A}$?
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
    ❓ **Question 2.2: a short proof.** Let $\mathbf{A}$ be symmetric with eigenvalues
    $\lambda_1, \dots, \lambda_n$. Show that $\operatorname{tr}(\mathbf{A}^r) =
    \sum_i \lambda_i^r$ for every $r \geq 1$, so that the number of triangles is
    $\frac16 \sum_i \lambda_i^3$ (lecture A6). Hint: the eigendecomposition
    $\mathbf{A} = \mathbf{Q}\boldsymbol{\Lambda}\mathbf{Q}^T$ with an orthogonal
    $\mathbf{Q}$, and $\operatorname{tr}(\mathbf{X}\mathbf{Y}) =
    \operatorname{tr}(\mathbf{Y}\mathbf{X})$.
    """)
    return


@app.cell(hide_code=True)
def answer_2_2(mo):
    mo.md(r"""
    **Your proof.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.2.** Distances between all pairs would be $6474^2 \approx 42$ million
    numbers, again too many for the browser. Take a sample instead: complete
    `sampled_distances(A, sources)`, which returns all finite distances from the nodes in
    `sources` to all other nodes as one flat array, without the distance 0 of a node to
    itself. Use [`shortest_path`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html)
    with `unweighted=True`, `directed=False` and `indices=sources`: it computes the number
    of steps on a shortest path from every source (on a network without weights, this gives
    the same distances as a breadth-first search). The sources are 200 nodes drawn with a fixed seed, so that
    everybody gets the same numbers. The cell after it plots both distributions.

    **Target:** for the Internet, the mean distance is **3.74**.
    """)
    return


@app.cell
def task_2_2(A_as, A_power, n_as, n_power, np, shortest_path):
    def sampled_distances(A, sources):
        """All finite distances > 0 from the nodes in `sources`, as a flat array."""
        # TODO: your code goes here
        raise NotImplementedError("Task 2.2: distances from a sample of sources")

    d_as = sampled_distances(A_as, np.random.default_rng(0).choice(n_as, size=200, replace=False))
    d_power = sampled_distances(A_power, np.random.default_rng(0).choice(n_power, size=200, replace=False))
    {
        "Internet (AS)": (round(float(d_as.mean()), 2), int(d_as.max())),
        "power grid": (round(float(d_power.mean()), 2), int(d_power.max())),
    }
    return d_as, d_power


@app.cell(hide_code=True)
def distance_plot(d_as, d_power, np, plt):
    _fig, _ax = plt.subplots(figsize=(8, 3.2))
    for _d, _label in [(d_as, "Internet (AS)"), (d_power, "power grid")]:
        _counts = np.bincount(_d.astype(int))
        _ax.plot(np.arange(len(_counts)), _counts / _counts.sum(), "o-", ms=3, label=_label)
    _ax.set(xlabel="distance (steps)", ylabel="fraction of pairs", title="distances from 200 sampled sources")
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.3: your decision.** One link fails: an AS connection, or a
    transmission line. In which network is it harder to route around the failure, and why?
    Use the two numbers of Task 2.1, the distances of Task 2.2 and the degrees of Section 1.
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
    ## 3  What happens when nodes fail or are attacked? Components (A6)

    ⚙️ **Practice question.** Nodes fail at random, through hardware faults or
    maintenance, or they are attacked on purpose: a DDoS on large ASes, sabotage on
    substations. When does the network fall apart?

    ⚙️ **Given.** Lecture A6: a **component** is a maximal set of nodes in which every node
    can reach every other one. As long as one **giant component** holds almost all nodes,
    nearly everybody can still reach nearly everybody. Both networks start as a single
    component.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.1.** Complete `giant_fraction(A, removed)`: remove the nodes in `removed`
    (with all their edges) and return the size of the largest remaining component as a
    fraction of **all** $n$ nodes. Use
    [`connected_components`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.connected_components.html)
    with `directed=False` on the submatrix of the remaining nodes; it returns the number of
    components and a label per node, and `np.bincount` of the labels gives the component
    sizes. The cell then removes the single node with the largest degree.

    **Target:** without the AS with 1458 connections, the giant component still holds
    **0.955** of all ASes.
    """)
    return


@app.cell
def task_3_1(A_as, A_power, connected_components, k_as, k_power, np):
    def giant_fraction(A, removed):
        """Size of the largest component after removing `removed`, as a fraction of n."""
        # TODO: your code goes here
        raise NotImplementedError("Task 3.1: largest component after removing nodes")

    {
        "Internet (AS)": (giant_fraction(A_as, []), round(giant_fraction(A_as, [int(np.argmax(k_as))]), 3)),
        "power grid": (giant_fraction(A_power, []), round(giant_fraction(A_power, [int(np.argmax(k_power))]), 4)),
    }
    return (giant_fraction,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.2.** Remove nodes step by step, up to 20 % of all nodes, in two orders:

    - **targeted attack:** largest degree first, `np.argsort(-k, kind="stable")`;
    - **random failure:** a random order, `np.random.default_rng(1).permutation(n)`.

    Complete `robustness_curve(A, order)`: for every fraction $f$ in `fractions`, remove the
    first `round(f * n)` nodes of `order` and record `giant_fraction`. The cell after it
    plots the four curves.

    **Target:** for the Internet under targeted attack, the curve is $0.518$ at $f = 0.01$.
    """)
    return


@app.cell
def task_3_2(A_as, A_power, giant_fraction, k_as, k_power, n_as, n_power, np):
    fractions = np.round(np.arange(0, 0.201, 0.01), 2)

    def robustness_curve(A, order):
        """Giant component fraction after removing the first round(f * n) nodes of `order`."""
        # TODO: your code goes here
        raise NotImplementedError("Task 3.2: the robustness curve")

    curves = {
        ("Internet (AS)", "targeted"): robustness_curve(A_as, np.argsort(-k_as, kind="stable")),
        ("Internet (AS)", "random"): robustness_curve(A_as, np.random.default_rng(1).permutation(n_as)),
        ("power grid", "targeted"): robustness_curve(A_power, np.argsort(-k_power, kind="stable")),
        ("power grid", "random"): robustness_curve(A_power, np.random.default_rng(1).permutation(n_power)),
    }
    {_key: _curve[[1, 2, 5, 10, 20]].round(3) for _key, _curve in curves.items()}
    return curves, fractions


@app.cell(hide_code=True)
def robustness_plot(curves, fractions, plt):
    _fig, _ax = plt.subplots(figsize=(8, 3.6))
    _style = {"targeted": "-", "random": "--"}
    _color = {"Internet (AS)": "C0", "power grid": "C1"}
    for (_net, _kind), _curve in curves.items():
        _ax.plot(fractions, _curve, _style[_kind], color=_color[_net], marker="o", ms=3, label=f"{_net}, {_kind}")
    _ax.set(xlabel="fraction of nodes removed", ylabel="giant component / n", ylim=(0, 1.02))
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Explore.** Remove the largest ASes one by one and watch the giant component.
    """)
    return


@app.cell(hide_code=True)
def hub_slider(mo):
    hubs_removed = mo.ui.slider(0, 130, value=0, step=1, label="largest ASes removed", show_value=True)
    hubs_removed
    return (hubs_removed,)


@app.cell(hide_code=True)
def hub_view(A_as, giant_fraction, hubs_removed, k_as, mo, n_as, np):
    _removed = np.argsort(-k_as, kind="stable")[: hubs_removed.value]
    _share = giant_fraction(A_as, _removed)
    mo.md(
        f"Removed **{hubs_removed.value}** of {n_as} ASes ({hubs_removed.value / n_as:.1%}): "
        f"the giant component holds **{_share:.1%}** of all ASes."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 3.1.** Which network is more robust? Answer for both kinds of failure,
    with numbers from the curves. Why does removing the single largest AS change so little,
    while removing 1 % of the ASes changes so much?
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
    ❓ **Question 3.2: your decision.** What do you recommend to the operator of each
    network? And name two things this model of removing nodes ignores that matter for a
    real Internet or a real power grid.
    """)
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
    ## 4  Save and submit

    ⚙️ **Given.** The same steps as in Exercise 1.

    1. Press `Ctrl+S` (`Cmd+S` on a Mac). Without this step the export is an empty file.
    2. Menu (round button with three lines, top right) → **Export…** → tab **Python** →
       **Export notebook source**.
    3. Rename the downloaded `notebook.py` to `exercise02_<lastname>.py`.
    4. On Moodle, assignment **Exercise 2**: **Add submission**, drag in the file,
       **Save changes**, then **Submit assignment** and confirm. The status must read
       **Submitted for grading**. The deadline is on Moodle.

    Need a break? `Ctrl+S`, then menu → **Share** → **Create WebAssembly link**, and keep
    the link: it restores your work on marimo.app. A reload of this page loses every edit.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Sources.** Internet: SNAP dataset AS-733, snapshot of 2 January 2000, from the
    University of Oregon Route Views Project; J. Leskovec, J. Kleinberg and C. Faloutsos,
    *Graphs over Time*, KDD 2005. Power grid: D. J. Watts and S. H. Strogatz, *Collective
    dynamics of 'small-world' networks*, Nature 393 (1998), via the Netzschleuder
    collection. The comparison of random failures and targeted attacks follows R. Albert,
    H. Jeong and A.-L. Barabási, *Error and attack tolerance of complex networks*, Nature
    406 (2000).
    """)
    return


if __name__ == "__main__":
    app.run()
