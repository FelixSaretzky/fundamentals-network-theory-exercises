# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.25.2",
#     "matplotlib",
#     "numpy",
#     "pandas",
#     "scipy",
#     "wigglystuff>=0.5.40",
#     "marimo-lens>=0.2.4; sys_platform != 'emscripten'",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse.linalg import eigsh, splu

    return connected_components, eigsh, mo, np, pd, plt, sp, splu


@app.cell
async def widgets():
    # Drawing widget. In the browser the package is installed on the fly, also when
    # the notebook is reopened from a saved link on marimo.app.
    import sys

    if sys.platform == "emscripten":
        import micropip

        await micropip.install("wigglystuff")
    from wigglystuff import EdgeDraw, PlaySlider

    return EdgeDraw, PlaySlider


@app.cell(hide_code=True)
def intro(mo):
    mo.md(r"""
    # Exercise 3: Where is the bottleneck?

    *Fundamentals of Network Theory*, University of Luxembourg, winter semester 2026/27.
    Lecture A7 (graph Laplacian). We discuss this notebook in the exercise session on
    **Monday 23 November 2026**, and the quiz in that session builds on it.

    You work with the two networks of Exercise 2 from start to end:

    - the **Internet** at the level of autonomous systems (AS), 6474 nodes;
    - the **power grid** of the western United States, 4941 nodes.

    A third, tiny network is for warming up: **Zachary's karate club**, 34 members and
    their friendships. It is small enough to compute everything exactly and to draw it.

    In Exercise 2 you removed nodes and counted what was left. Now one matrix, the
    **Laplacian** $\mathbf{L} = \mathbf{D} - \mathbf{A}$ of lecture A7, answers three
    ⚙️ **practice questions** without removing anything:

    1. Does the network hold together, and how firmly? (eigenvalues of $\mathbf{L}$)
    2. Where is the bottleneck? (the eigenvector of the second smallest eigenvalue)
    3. How fast does something spread? (the diffusion equation)

    **Three markers**, as before.

    - ⚙️ **Given.** Context, and code you do not have to change.
    - ❓ **Question.** Write your answer into the answer cell right below it: double-click
      the text *Your answer*, write, then click outside the cell. One to three sentences
      are enough, a proof needs a few lines.
    - ✏️ **Task.** Code you write below `# TODO: your code goes here`, in place of the line
      `raise NotImplementedError(...)`. Each task states a **target**, for the karate club
      or the Internet. Compute the power grid yourself: there is no target for it. Until a
      task is done, its cell and every cell that uses its result show an error. That is
      normal.

    **One rule of marimo.** Every name can be defined in one cell only. Helpers you would
    reuse, such as loop variables, get a leading underscore (`_i`, `_M`).

    There are no automatic checks. In the session we discuss your answers, the wrong ones
    included. Be ready to explain any line of your code.

    Plan about four hours. Save and submit as before, see Section 4.
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
    ## 1  Does the network hold together, and how firmly? The Laplacian (A7)

    ⚙️ **Practice question.** In Exercise 2 you counted components after failures. An
    operator also wants to know *before* anything fails: is my network one piece, and is it
    one piece that holds firmly or one that hangs by a thread?

    ⚙️ **Given.** The three networks as edge lists with the columns `u` and `v`, and the
    function `adjacency` you wrote in Exercise 2, Task 1.1: a sparse, symmetric 0/1 matrix
    without self-loops. For the karate club there is also a table `members`: the `club`
    each member joined after the club split in two (more on that in Section 2), and
    coordinates `x`, `y` for drawing.
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
def load_data(np, read_csv, sp):
    def adjacency(edges, n):
        """Adjacency matrix of a simple undirected network, as a sparse 0/1 matrix."""
        _e = edges[edges["u"] != edges["v"]]  # drop self-loops
        _A = sp.coo_array((np.ones(len(_e), dtype=int), (_e["u"], _e["v"])), shape=(n, n))
        return ((_A + _A.T) > 0).astype(int)  # each edge in both directions, once

    members = read_csv("karate_members.csv")
    A_karate = adjacency(read_csv("karate_edges.csv"), len(members))
    _edges_as = read_csv("as_edges.csv")
    _edges_power = read_csv("power_edges.csv")
    A_as = adjacency(_edges_as, int(max(_edges_as["u"].max(), _edges_as["v"].max())) + 1)
    A_power = adjacency(_edges_power, int(max(_edges_power["u"].max(), _edges_power["v"].max())) + 1)
    {
        _name: f"{_A.shape[0]} nodes, {int(_A.sum()) // 2} edges"
        for _name, _A in [("karate club", A_karate), ("Internet (AS)", A_as), ("power grid", A_power)]
    }
    return A_as, A_karate, A_power, members


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.1.** Complete `laplacian(A)`: it returns the Laplacian
    $\mathbf{L} = \mathbf{D} - \mathbf{A}$ of lecture A7 as a sparse matrix, where
    $\mathbf{D}$ is the diagonal matrix of the degrees.
    [`sp.diags_array`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.diags_array.html)
    builds a sparse diagonal matrix from an array (pass `dtype=int` to keep whole numbers).

    Then compute `lam_karate`, **all** eigenvalues of the karate club's Laplacian in
    ascending order. With 34 nodes you can afford the full matrix: `L_karate.toarray()`
    turns it into a numpy array, and
    [`np.linalg.eigvalsh`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigvalsh.html)
    returns the eigenvalues of a symmetric matrix, sorted.

    **Target:** every row of `L_karate` sums to **0**, its diagonal sums to **156**
    (why?), and the two smallest eigenvalues are **0** and **0.4685**.
    """)
    return


@app.cell
def task_1_1(A_as, A_karate, A_power, np, sp):
    def laplacian(A):
        """Graph Laplacian L = D - A of a simple undirected network, as a sparse matrix."""
        # TODO: your code goes here
        raise NotImplementedError("Task 1.1 (a): build the Laplacian")

    L_karate = laplacian(A_karate)
    L_as = laplacian(A_as)
    L_power = laplacian(A_power)
    # TODO: your code goes here
    raise NotImplementedError("Task 1.1 (b): all eigenvalues of the karate club's Laplacian")
    {
        "largest row sum (absolute value)": int(np.abs(L_karate.sum(axis=1)).max()),
        "sum of the diagonal": int(L_karate.diagonal().sum()),
        "smallest eigenvalues": lam_karate[:4].round(4),
        "largest eigenvalue": round(float(lam_karate[-1]), 3),
    }
    return L_as, L_karate, L_power, lam_karate, laplacian


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Explore: the Laplace lab.** What is the Laplacian good for, and why do we look at
    its *smallest* eigenvalues? Find out on a small network: two groups of four nodes,
    joined by the single link 4–5. Everything below is computed with your `laplacian` from
    Task 1.1, so the lab works once Task 1.1 is done.

    - **Click two nodes** to add a link between them, or to remove it again. **Click a
      link** to remove it. You can drag the nodes around. The plots below show the same
      network in a fixed layout, coloured by the sign of the eigenvector of $\lambda_2$.
    - **Remove the link 4–5.** How many eigenvalues are 0 now? How many components are
      there?
    - **Put it back, then add a second link** between the groups, say 3–6, then a third.
      What happens to the smallest eigenvalue above 0, $\lambda_2$?
    - **Cut node 8 off** by removing its links.
    - Watch the signs of the eigenvector of $\lambda_2$ below the plots: which nodes are
      positive, which negative?
    - Does any row of $\mathbf{L}$ ever sum to something else than 0?
    """)
    return


@app.cell(hide_code=True)
def lab_graph_cell(EdgeDraw, mo):
    LAB_NODES = [str(_i) for _i in range(1, 9)]
    lab_graph = mo.ui.anywidget(
        EdgeDraw(
            names=LAB_NODES,
            directed=False,
            links=[
                ("1", "2"), ("1", "3"), ("2", "3"), ("2", "4"), ("3", "4"),
                ("4", "5"),
                ("5", "6"), ("5", "7"), ("6", "7"), ("6", "8"), ("7", "8"),
            ],
        )
    )
    lab_graph
    return LAB_NODES, lab_graph


@app.cell(hide_code=True)
def lab_view(LAB_NODES, connected_components, lab_graph, laplacian, mo, np, plt, sp):
    _index = {_name: _k for _k, _name in enumerate(LAB_NODES)}
    _n = len(LAB_NODES)
    _A = np.zeros((_n, _n), dtype=int)
    for _link in lab_graph.value["links"]:
        _i, _j = _index[_link["source"]], _index[_link["target"]]
        if _i != _j:
            _A[_i, _j] = _A[_j, _i] = 1
    _L = laplacian(sp.csr_array(_A)).toarray()
    _lam, _V = np.linalg.eigh(_L)
    _lam = np.where(np.abs(_lam) < 1e-9, 0.0, _lam)  # rounding leaves values like 1e-16
    _components, _ = connected_components(sp.csr_array(_A), directed=False)
    _zeros = int((_lam == 0).sum())

    _f = _V[:, 1]
    _, _labels = connected_components(sp.csr_array(_A), directed=False)
    _fig, (_net, _mat, _bar) = plt.subplots(1, 3, figsize=(12, 3.8), width_ratios=[1.1, 1, 1.15])
    # the same network in a fixed layout: group 1-4 on the left, group 5-8 on the right
    _pos = np.array([[0, 1], [1, 1.8], [1, 0.2], [2, 1], [3, 1], [4, 1.8], [4, 0.2], [5, 1]])
    for _i, _j in zip(*np.nonzero(np.triu(_A))):
        _net.plot(*_pos[[_i, _j]].T, color="0.6", lw=1.5, zorder=1)
    if _zeros == 1:
        _node_colors = ["C0" if _v > 0 else "C1" for _v in _f]
        _net.set_title("colour: sign of the eigenvector of $\\lambda_2$", fontsize=10)
    else:
        _node_colors = [plt.cm.tab10(_c % 10) for _c in _labels]
        _net.set_title("colour: component", fontsize=10)
    _net.scatter(*_pos.T, s=420, c=_node_colors, edgecolors="k", zorder=2)
    for _k, _name in enumerate(LAB_NODES):
        _net.annotate(_name, _pos[_k], ha="center", va="center", color="white", fontsize=10, zorder=3)
    _net.set_xlim(-0.5, 5.5)
    _net.set_ylim(-0.3, 2.3)
    _net.axis("off")
    _limit = max(1, int(np.abs(_L).max()))
    _mat.imshow(_L, cmap="RdBu_r", vmin=-_limit, vmax=_limit)
    for _i in range(_n):
        for _j in range(_n):
            if _L[_i, _j] != 0:
                _mat.text(
                    _j, _i, str(int(_L[_i, _j])), ha="center", va="center", fontsize=9,
                    color="white" if abs(_L[_i, _j]) > 0.6 * _limit else "black",
                )
    _mat.set_xticks(range(_n), LAB_NODES)
    _mat.set_yticks(range(_n), LAB_NODES)
    _mat.set_title(f"L = D - A, largest row sum: {int(np.abs(_L.sum(axis=1)).max())}", fontsize=10)
    _colors = ["C3" if _v == 0 else ("C1" if _k == _zeros else "C0") for _k, _v in enumerate(_lam)]
    _bar.bar(range(1, _n + 1), _lam, color=_colors)
    _bar.scatter(  # a bar of height 0 is invisible, so mark the zeros
        [_k + 1 for _k in range(_n) if _lam[_k] == 0], [0] * _zeros, color="C3", s=60, zorder=3, clip_on=False
    )
    for _k, _v in enumerate(_lam):
        _bar.text(_k + 1, _v, f"{_v:.2f}", ha="center", va="bottom", fontsize=8)
    _bar.set_xticks(range(1, _n + 1))
    _bar.set(xlabel="eigenvalues, sorted", ylabel="value")
    _bar.set_title("eigenvalues of L (red: 0, orange: smallest above 0)", fontsize=10)
    _fig.tight_layout()

    if _zeros > 1:
        _split = "The network is already in pieces, so there is nothing left to split."
    else:
        _plus = ", ".join(LAB_NODES[_k] for _k in range(_n) if _f[_k] > 0)
        _minus = ", ".join(LAB_NODES[_k] for _k in range(_n) if _f[_k] <= 0)
        _split = f"Signs of its eigenvector: positive {_plus}, negative {_minus}."
    mo.vstack(
        [
            mo.md(
                f"**{_components}** component(s) and **{_zeros}** eigenvalue(s) equal to 0. "
                f"$\\lambda_2 = {_lam[1]:.3f}$. {_split}"
            ),
            _fig,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.1: a short proof.** Lecture A7 shows
    $\mathbf{L} = \mathbf{B}^T\mathbf{B}$ with the edge incidence matrix $\mathbf{B}$: the
    row of an edge $\{i, j\}$ has a $+1$ in column $i$, a $-1$ in column $j$ and zeros
    elsewhere. Show that for every vector $\mathbf{x}$

    $$\mathbf{x}^T\mathbf{L}\,\mathbf{x} = \sum_{\{i,j\}\,\in\,\text{edges}} (x_i - x_j)^2 .$$

    Conclude (a) that no eigenvalue of $\mathbf{L}$ is negative, and (b) that
    $\mathbf{L}\mathbf{x} = \mathbf{0}$ holds exactly when $\mathbf{x}$ has the same value
    on all nodes of each component.
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
    ⚙️ **Given.** The Internet's Laplacian has 6474 eigenvalues, and the full matrix would
    not fit into the browser (Exercise 2, Task 1.1). We only need the few **smallest**
    ones. `smallest_eigenpairs(L, k)` computes them with
    [`eigsh`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.eigsh.html),
    which works on the sparse matrix. It returns the `k` smallest eigenvalues in ascending
    order and the matching eigenvectors as the columns of a matrix. Both networks are
    connected, so this works here. On a network with many components, `eigsh` can miss
    some of the zero eigenvalues: that is why Task 1.3 counts them on the small karate
    club, with all eigenvalues.
    """)
    return


@app.cell
def given_eigenpairs(eigsh, np):
    def smallest_eigenpairs(L, k):
        """The k smallest eigenvalues of a sparse Laplacian, and their eigenvectors as columns."""
        _start = np.random.default_rng(0).standard_normal(L.shape[0])  # same result on every run
        # sigma: search near -0.01, just below the smallest eigenvalue 0
        _values, _vectors = eigsh(L.astype(float), k=k, sigma=-0.01, which="LM", v0=_start)
        _order = np.argsort(_values)
        return _values[_order], _vectors[:, _order]

    return (smallest_eigenpairs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.2.** Compute the two smallest eigenvalues and their eigenvectors for the
    Internet (`lam_as`, `V_as`) and for the power grid (`lam_power`, `V_power`). The second
    smallest eigenvalue $\lambda_2$ is the **algebraic connectivity** or *Fiedler
    eigenvalue* of lecture A7. Store it as `lam2_as` and `lam2_power`.

    Why only the smallest ones? The lab above shows it: the number of eigenvalues equal to
    0 counts the components, and $\lambda_2$ tells how firmly the network holds together.
    Its eigenvector is what Section 2 needs. The large eigenvalues mostly reflect single
    nodes with many links: the largest is at least the largest degree plus 1.

    **Target:** for the Internet, the smallest eigenvalue is $0$ (up to rounding, around
    $10^{-15}$) and $\lambda_2$ is **0.0880**.
    """)
    return


@app.cell
def task_1_2(L_as, L_power, smallest_eigenpairs):
    # TODO: your code goes here
    raise NotImplementedError("Task 1.2: the smallest eigenvalues of both networks")
    {
        "Internet (AS)": lam_as.round(5),
        "power grid": lam_power.round(5),
        "ratio of the two lambda_2": round(lam2_as / lam2_power),
    }
    return V_as, V_power, lam2_as, lam2_power


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 1.3.** Question 1.1 (b) says: the number of zero eigenvalues of $\mathbf{L}$
    is the number of components. Check it on the karate club, where you can compute all
    eigenvalues. Complete `components_and_zeros(A, removed)`: remove the nodes in `removed`
    with all their edges (the submatrix `A[keep][:, keep]`, as in Exercise 2), then return
    two numbers:

    - the number of components, from
      [`connected_components`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.connected_components.html)
      with `directed=False`;
    - the number of eigenvalues of the Laplacian that are zero. Rounding leaves values
      like $10^{-15}$, so count the eigenvalues below $10^{-9}$.

    The cell removes the two leaders of the club: member 0, the instructor, and member 33,
    the administrator.

    **Target:** without members 0 and 33 the club has **3** components, and the Laplacian
    has **3** zero eigenvalues.
    """)
    return


@app.cell
def task_1_3(A_karate, connected_components, laplacian, np):
    def components_and_zeros(A, removed):
        """Number of components, and number of zero eigenvalues of L, after removing `removed`."""
        # TODO: your code goes here
        raise NotImplementedError("Task 1.3: components and zero eigenvalues")

    {
        "whole club": components_and_zeros(A_karate, []),
        "without members 0 and 33": components_and_zeros(A_karate, [0, 33]),
        "without members 0, 32 and 33": components_and_zeros(A_karate, [0, 32, 33]),
    }
    return (components_and_zeros,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Explore.** Remove members of the club yourself, with your `components_and_zeros`
    from Task 1.3. Who holds the club together? Start with the two leaders 0 and 33, then
    add 32. Each colour is one component, and each component brings one eigenvalue 0.
    """)
    return


@app.cell(hide_code=True)
def removal_picker(members, mo):
    removed_members = mo.ui.multiselect(
        options=[str(_i) for _i in members["id"]], value=[], label="remove members"
    )
    removed_members
    return (removed_members,)


@app.cell(hide_code=True)
def removal_view(
    A_karate, components_and_zeros, connected_components, laplacian, members, np, plt, removed_members
):
    _removed = sorted(int(_s) for _s in removed_members.value)
    _components, _zeros = components_and_zeros(A_karate, _removed)
    _keep = np.ones(A_karate.shape[0], dtype=bool)
    _keep[_removed] = False
    _rest = A_karate[_keep][:, _keep]
    _, _labels = connected_components(_rest, directed=False)
    _lam = np.linalg.eigvalsh(laplacian(_rest).toarray())
    _label_of = dict(zip(np.flatnonzero(_keep), _labels))

    _fig, (_net, _bar) = plt.subplots(1, 2, figsize=(10, 4), width_ratios=[1.2, 1])
    _x, _y = members["x"].to_numpy(), members["y"].to_numpy()
    _rows, _cols = A_karate.nonzero()
    for _i, _j in zip(_rows, _cols):
        if _i < _j:
            _alive = _keep[_i] and _keep[_j]
            _net.plot([_x[_i], _x[_j]], [_y[_i], _y[_j]], color="0.75" if _alive else "0.93", lw=0.8, zorder=1)
    for _i in range(len(members)):
        if _keep[_i]:
            _net.scatter(_x[_i], _y[_i], s=150, color=plt.cm.tab10(_label_of[_i] % 10), edgecolors="k", linewidths=0.6, zorder=2)
            _net.annotate(str(_i), (_x[_i], _y[_i]), ha="center", va="center", fontsize=7, color="white", zorder=3)
        else:
            _net.scatter(_x[_i], _y[_i], s=90, marker="x", color="0.5", zorder=2)
    _net.set_title(f"{_components} component(s), one colour each", fontsize=10)
    _net.axis("off")
    _small = _lam[:10]
    _bar.bar(range(1, len(_small) + 1), _small, color=["C3" if _v < 1e-9 else "C0" for _v in _small])
    _bar.scatter(  # a bar of height 0 is invisible, so mark the zeros
        [_k + 1 for _k in range(len(_small)) if _small[_k] < 1e-9], [0] * int((_small < 1e-9).sum()),
        color="C3", s=60, zorder=3, clip_on=False,
    )
    _bar.set_xticks(range(1, len(_small) + 1))
    _bar.set(xlabel="the 10 smallest eigenvalues of L, sorted", ylabel="value")
    _bar.set_title(f"{_zeros} eigenvalue(s) equal to 0 (red)", fontsize=10)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 1.2.** (a) Both large networks have exactly one zero eigenvalue. What does
    that tell you, and how did you find the same fact in Exercise 2? (b) The two values of
    $\lambda_2$ differ by a factor of more than 100. Lecture A7 calls $\lambda_2$ the
    algebraic connectivity: which of the two networks holds together more firmly? Name
    one result of Exercise 2 that fits.
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
    ## 2  Where is the bottleneck? The Fiedler vector (A7)

    ⚙️ **Practice question.** If the network had to fall into two large parts, where would
    it break? An operator wants to know these few links: they are the ones to watch and to
    reinforce. In an emergency, a grid can even be split on purpose at such a place, so
    that a blackout stays on one side.

    ⚙️ **Why an eigenvector?** The obvious way is to try every split of the nodes into two
    groups and keep the one with the fewest links between them. But a network with $n$
    nodes has $2^{n-1}$ such splits: about 8.6 billion for the 34 members of the karate
    club, and a number with almost 1500 digits for the 4941 stations of the power grid. No
    computer can try them all. One eigenvector of $\mathbf{L}$ replaces this search and is
    computed in a fraction of a second. It finds a good split, not always the very best
    one.

    ⚙️ **Given.** Lecture A7 says that $\lambda_2$ *is used to partition the graph*. The
    recipe: take the eigenvector $\mathbf{v}_2$ of $\lambda_2$, the **Fiedler vector**. It
    has one entry per node. Put the nodes with a **positive** entry on one side and all
    others on the other side. Question 1.1 shows why this is reasonable:
    $\lambda_2 = \sum_{\text{edges}} (v_i - v_j)^2$ is small, so linked nodes get similar
    entries and only few edges join a positive to a negative entry. An eigenvector is only
    fixed up to its sign, so the two sides may come out swapped. That does not matter.

    The karate club is the classic test. In the 1970s the sociologist Wayne Zachary
    recorded the friendships among its 34 members. Then the instructor (member 0, "Mr. Hi")
    and the administrator (member 33, "Officer") fell out, and the club split in two. The
    column `club` says who followed whom. Can the Laplacian predict the split from the
    friendships alone?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.1.** Compute the Fiedler vector of the karate club as `fiedler_karate`.
    [`np.linalg.eigh`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html)
    returns the eigenvalues in ascending order **and** the eigenvectors as the columns of a
    matrix: the Fiedler vector is the column with index 1. Then `side_karate` is the
    boolean array of the members with a positive entry, and `agree_karate` the number of
    members that the Laplacian puts with the right leader. Mind the sign: if fewer than 17
    agree, the two sides are swapped, and the right number is 34 minus that. The cell after
    it draws the result.

    **Target:** the two sides have **15** and **19** members, and **32** of the 34 members
    are on the side of the leader they really followed.
    """)
    return


@app.cell
def task_2_1(L_karate, members, np):
    # TODO: your code goes here
    raise NotImplementedError("Task 2.1: split the karate club with the Fiedler vector")
    {
        "sizes of the two sides": sorted([int(side_karate.sum()), int((~side_karate).sum())]),
        "members on the right side": agree_karate,
    }
    return fiedler_karate, side_karate


@app.cell(hide_code=True)
def karate_plot(A_karate, fiedler_karate, members, np, plt, side_karate):
    _fig, (_net, _bar) = plt.subplots(1, 2, figsize=(10, 4.2), width_ratios=[1.1, 1])
    _x, _y = members["x"].to_numpy(), members["y"].to_numpy()
    _rows, _cols = A_karate.nonzero()
    for _i, _j in zip(_rows, _cols):
        if _i < _j:
            _net.plot([_x[_i], _x[_j]], [_y[_i], _y[_j]], color="0.8", lw=0.8, zorder=1)
    _hi = (members["club"] == "Mr. Hi").to_numpy()
    for _mask, _marker, _label in [(_hi, "o", "followed Mr. Hi (0)"), (~_hi, "s", "followed Officer (33)")]:
        _net.scatter(
            _x[_mask], _y[_mask], c=np.where(side_karate[_mask], "C0", "C1"), marker=_marker,
            s=150, edgecolors="k", linewidths=0.6, zorder=2, label=_label,
        )
    for _i in range(len(members)):
        _net.annotate(str(_i), (_x[_i], _y[_i]), ha="center", va="center", fontsize=7, color="white", zorder=3)
    _net.set_title("colour: side of the Fiedler vector, shape: real club")
    _legend = _net.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False)
    for _handle in _legend.legend_handles:  # the legend explains the shape only
        _handle.set_facecolor("white")
    _net.axis("off")
    _order = np.argsort(fiedler_karate)
    _bar.bar(range(len(_order)), fiedler_karate[_order], color=np.where(side_karate[_order], "C0", "C1"))
    _bar.set_xticks(range(len(_order)), _order, fontsize=6)
    _bar.axhline(0, color="k", lw=0.6)
    _bar.set(xlabel="member, sorted by entry", ylabel="entry of the Fiedler vector")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.1.** Which two members does the Fiedler vector put on the "wrong" side?
    Look at their entries in the right plot and at their friends in the left plot: why
    exactly these two? Is the Laplacian wrong about them?
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
    ✏️ **Task 2.2.** Now the two large networks. Complete `cut_size(A, side)`: the number
    of edges with one end on each side, where `side` is a boolean array with one entry per
    node. Tip: `A[side][:, ~side]` holds exactly the entries between the two sides. Then
    split the Internet and the power grid by the sign of their Fiedler vectors from
    Task 1.2 (`side_as`, `side_power`).

    **Target:** for the karate club the cut has **10** edges. The Internet falls into
    **1310** and **5164** nodes, and **493** links join the two sides.
    """)
    return


@app.cell
def task_2_2(A_as, A_karate, A_power, V_as, V_power, side_karate):
    def cut_size(A, side):
        """Number of edges between the nodes in `side` and all other nodes."""
        # TODO: your code goes here
        raise NotImplementedError("Task 2.2 (a): count the edges between the two sides")

    # TODO: your code goes here
    raise NotImplementedError("Task 2.2 (b): split both networks by the sign of the Fiedler vector")
    {
        _name: {
            "sizes": sorted([int(_side.sum()), int((~_side).sum())]),
            "cut": cut_size(_A, _side),
            "share of all edges": f"{cut_size(_A, _side) / (_A.sum() // 2):.2%}",
        }
        for _name, _A, _side in [
            ("karate club", A_karate, side_karate),
            ("Internet (AS)", A_as, side_as),
            ("power grid", A_power, side_power),
        ]
    }
    return cut_size, side_as, side_power


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Explore: move the dividing line.** The Fiedler vector gives every member a position
    on a line: the bars in the right plot of Task 2.1. Every way of cutting this line into a
    left and a right part is a possible split. Move the slider: the $k$ members with the
    smallest entries go to one side, all others to the other. Your `cut_size` from Task 2.2
    counts the edges between the two sides.

    - Start at the dotted line, where the entries change sign: that is the split of
      Task 2.1, with 10 edges cut.
    - Try $k = 1$ and $k = 33$. Only 2 edges are cut. Why is that still a useless split?
    - Try $k = 5$: 4 edges cut off five members. Who are they? You have met them in the
      explorer after Task 1.3.
    - So the sign split is not the smallest cut. What does it find instead? Think of
      Question 2.2: it relaxes "a split into two large groups with few edges between them",
      it does not search all splits.
    """)
    return


@app.cell(hide_code=True)
def split_slider(mo):
    split_at = mo.ui.slider(1, 33, value=8, step=1, label="members on the first side, k", show_value=True)
    split_at
    return (split_at,)


@app.cell(hide_code=True)
def split_view(A_karate, cut_size, fiedler_karate, members, np, plt, split_at):
    _n = len(fiedler_karate)
    _order = np.argsort(fiedler_karate)
    _cuts = []
    for _k in range(1, _n):
        _first = np.zeros(_n, dtype=bool)
        _first[_order[:_k]] = True
        _cuts.append(cut_size(A_karate, _first))
    _k = split_at.value
    _side = np.zeros(_n, dtype=bool)
    _side[_order[:_k]] = True
    _sign_change = int((fiedler_karate < 0).sum()) + 0.5  # between the last negative and the first positive

    _fig, (_net, _curve) = plt.subplots(1, 2, figsize=(10, 4), width_ratios=[1.1, 1])
    _x, _y = members["x"].to_numpy(), members["y"].to_numpy()
    _rows, _cols = A_karate.nonzero()
    for _i, _j in zip(_rows, _cols):
        if _i < _j:
            _crossing = _side[_i] != _side[_j]
            _net.plot(
                [_x[_i], _x[_j]], [_y[_i], _y[_j]], zorder=1,
                color="C3" if _crossing else "0.8", lw=2 if _crossing else 0.8,
            )
    _net.scatter(_x, _y, s=150, c=np.where(_side, "C1", "C0"), edgecolors="k", linewidths=0.6, zorder=2)
    for _i in range(_n):
        _net.annotate(str(_i), (_x[_i], _y[_i]), ha="center", va="center", fontsize=7, color="white", zorder=3)
    _net.set_title(f"{_k} and {_n - _k} members, {_cuts[_k - 1]} edges cut (red)", fontsize=10)
    _net.axis("off")
    _curve.plot(range(1, _n), _cuts, "o-", color="0.5", ms=3)
    _curve.plot(_k, _cuts[_k - 1], "o", color="C3", ms=9)
    _curve.axvline(_sign_change, color="k", ls=":", lw=1)
    _curve.text(_sign_change, max(_cuts), " sign changes", fontsize=8, va="top")
    _curve.set(xlabel="k, members on the first side", ylabel="edges cut")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.2: a short proof.** Describe a split by a vector $\mathbf{s}$ with
    $s_i = +1$ for the nodes on one side and $s_i = -1$ for the others. Show that the
    number of edges between the two sides is

    $$\text{cut} = \tfrac14\, \mathbf{s}^T\mathbf{L}\,\mathbf{s} .$$

    Check the formula on the karate club in one line of code in a new cell. Hint:
    Question 1.1, and `np.where(side_karate, 1, -1)`.
    """)
    return


@app.cell(hide_code=True)
def answer_2_2(mo):
    mo.md(r"""
    **Your proof.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def fiedler_plot(V_as, V_power, np, plt):
    _fig, _axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for _ax, _V, _name, _color in [(_axes[0], V_as, "Internet (AS)", "C0"), (_axes[1], V_power, "power grid", "C1")]:
        _f = np.sort(_V[:, 1])
        _f = _f if (_f > 0).sum() >= len(_f) / 2 else np.sort(-_V[:, 1])  # larger side positive
        _ax.plot(_f, color=_color)
        _ax.axhline(0, color="k", lw=0.6)
        _ax.set(title=_name, xlabel="nodes, sorted by entry", ylabel="entry of the Fiedler vector")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 2.3.** Is 493 a small number? Compare with a split that knows nothing about
    the network. Complete `random_cut(A, side)`: the cut of a **random** split with the
    same two sizes. Take `a`, the size of the smaller side, and put the nodes with
    `np.random.default_rng(0).permutation(n) < a` on one side: that picks `a` nodes at
    random, the same ones on every run.

    **Target:** for the Internet, a random split into 1310 and 5164 nodes cuts **3554**
    links.
    """)
    return


@app.cell
def task_2_3(A_as, A_power, cut_size, np, side_as, side_power):
    def random_cut(A, side):
        """Cut size of a random split with the same two sizes as `side`."""
        # TODO: your code goes here
        raise NotImplementedError("Task 2.3: a random split of the same sizes")

    {
        "Internet (AS)": {"Fiedler cut": cut_size(A_as, side_as), "random cut": random_cut(A_as, side_as)},
        "power grid": {"Fiedler cut": cut_size(A_power, side_power), "random cut": random_cut(A_power, side_power)},
    }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Explore: cut the bottleneck.** Below is the power grid, drawn so that linked
    stations sit close together. The data have no coordinates, so this is a drawing, not a
    map. The colours are the two sides of your split from Task 2.2, the red lines join them.
    Choose which lines to cut and watch how much of the grid still holds together.

    - First cut the same number of lines, but chosen at random.
    - Then cut the lines between the two sides.
    - The same number of lines both times: why such a different result? And what does
      this tell you about the Fiedler vector?
    """)
    return


@app.cell(hide_code=True)
def grid_layout(read_csv):
    # positions for drawing only, computed beforehand with Graphviz (see Sources)
    pos_power = read_csv("power_layout.csv")[["x", "y"]].to_numpy()
    return (pos_power,)


@app.cell(hide_code=True)
def bottleneck_choice(A_power, cut_size, mo, side_power):
    _n_between = cut_size(A_power, side_power)
    cut_choice = mo.ui.radio(
        options={
            "nothing": "nothing",
            f"{_n_between} random lines": "random",
            f"the {_n_between} lines between the two sides": "between",
        },
        value="nothing",
        label="cut",
        inline=True,
    )
    cut_choice
    return (cut_choice,)


@app.cell(hide_code=True)
def bottleneck_view(A_power, connected_components, cut_choice, np, plt, pos_power, side_power, sp):
    from matplotlib.collections import LineCollection

    _U = sp.triu(A_power, 1).tocoo()
    _between = side_power[_U.row] != side_power[_U.col]
    _cut = np.zeros(len(_U.row), dtype=bool)
    if cut_choice.value == "between":
        _cut = _between
    elif cut_choice.value == "random":
        _cut[np.random.default_rng(0).choice(len(_U.row), size=int(_between.sum()), replace=False)] = True
    _n = A_power.shape[0]
    _rest = sp.coo_array((np.ones(int((~_cut).sum())), (_U.row[~_cut], _U.col[~_cut])), shape=(_n, _n))
    _pieces, _labels = connected_components(_rest + _rest.T, directed=False)
    _sizes = np.bincount(_labels)
    _rank = np.argsort(-_sizes)  # piece numbers, largest first

    _fig, _ax = plt.subplots(figsize=(7, 6))
    _segs = np.stack([pos_power[_U.row], pos_power[_U.col]], axis=1)
    _ax.add_collection(LineCollection(_segs[~_cut & ~_between], colors="0.8", linewidths=0.3, zorder=1))
    _ax.add_collection(LineCollection(_segs[~_cut & _between], colors="C3", linewidths=2, zorder=3))
    _ax.add_collection(
        LineCollection(_segs[_cut], colors="k", linewidths=2.5, linestyles=(0, (1, 1)), zorder=3)
    )
    _colors = np.where(side_power, "C0", "C1")  # always the two sides of Task 2.2
    if cut_choice.value == "nothing":
        _title = f"two sides of the Fiedler vector, {int(_between.sum())} lines between them (red)"
    else:
        _colors[~np.isin(_labels, _rank[:2])] = "0.3"  # small pieces that broke off: dark grey
        _title = (
            f"{int(_cut.sum())} lines cut (dotted): largest piece holds {_sizes.max() / _n:.1%} "
            f"of all stations, {_pieces} pieces"
        )
    _ax.scatter(pos_power[:, 0], pos_power[:, 1], s=3, c=_colors, linewidths=0, zorder=2)
    _ax.autoscale()
    _ax.set_aspect("equal")
    _ax.axis("off")
    _ax.set_title(_title, fontsize=10)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 2.3: your decision.** Compare the two networks: the sizes of the two
    sides, the cut and the plots of the sorted Fiedler vectors. Which network has a
    bottleneck, and which has none? What do you recommend to the operator of the network
    with the bottleneck, and why would the same advice make no sense for the other one?
    Use the hubs of Exercise 2 in your explanation.
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
    ## 3  How fast does something spread? Diffusion (A7)

    ⚙️ **Practice question.** Something enters the network at one node and spreads along
    the links: load that is balanced between routers, a rumour, heat. How long until it has
    reached the whole network evenly?

    ⚙️ **Given.** The diffusion equation of lecture A7, here with the constant $C = 1$:

    $$\frac{\mathrm{d}\boldsymbol{\psi}}{\mathrm{d}t} + \mathbf{L}\,\boldsymbol{\psi} = \mathbf{0}.$$

    $\psi_i(t)$ is the amount at node $i$ at time $t$. The lecture solves it with the
    eigenvalues $\lambda_i$ and normalised eigenvectors $\mathbf{v}_i$ of $\mathbf{L}$:

    $$\boldsymbol{\psi}(t) = \sum_i a_i(0)\, e^{-\lambda_i t}\, \mathbf{v}_i,
    \qquad a_i(0) = \mathbf{v}_i^T \boldsymbol{\psi}(0).$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.1.** Complete `diffusion_exact(L, psi0, t)` for a small network: it returns
    $\boldsymbol{\psi}(t)$ by the formula above, for a full (numpy) matrix `L`. With the
    eigenvalues `lam` and the matrix of eigenvectors `V` from `np.linalg.eigh`, the
    coefficients are `V.T @ psi0`, and the sum over $i$ is one matrix product. The cell
    starts with the whole amount 1 at the instructor, member 0.

    **Target:** at $t = 1$ the instructor still holds **0.0414**, and the amounts of all
    members add up to **1**.
    """)
    return


@app.cell
def task_3_1(L_karate, np):
    def diffusion_exact(L, psi0, t):
        """Solution psi(t) of d psi/dt + L psi = 0 with psi(0) = psi0, for a full matrix L."""
        # TODO: your code goes here
        raise NotImplementedError("Task 3.1: diffusion with the eigenvalues and eigenvectors")

    psi0_karate = np.zeros(L_karate.shape[0])
    psi0_karate[0] = 1.0
    _psi = diffusion_exact(L_karate.toarray(), psi0_karate, 1.0)
    {"instructor at t = 1": round(float(_psi[0]), 4), "sum over all members": round(float(_psi.sum()), 10)}
    return diffusion_exact, psi0_karate


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Explore: watch the solution formula at work.** Choose where the amount starts and
    press ▶. Left, the amount at every member (the area of a dot). Right, the formula of
    lecture A7, term by term: one bar per eigenvector, of height
    $|a_i(0)\, e^{-\lambda_i t}|$.

    - Which bars disappear first: those of the small or of the large eigenvalues?
    - Which bar never changes? Its term is the final, even state: $1/34$ at every member.
    - Start at the instructor: at $t = 0$ the bars of the *largest* eigenvalues are the
      highest. A spike at one well-connected node is made of exactly the terms that decay
      fastest.
    - Which bar is the last one left before everything is even? That is why $\lambda_2$
      sets the time scale.
    - Start at member 11 or 16, at the edge of the club, instead of a leader. Does it take
      longer?
    """)
    return


@app.cell(hide_code=True)
def diffusion_controls(PlaySlider, mo):
    start_member = mo.ui.dropdown(
        options={
            "member 0, the instructor": 0,
            "member 33, the administrator": 33,
            "member 11, one friend only": 11,
            "member 16, at the edge": 16,
        },
        value="member 0, the instructor",
        label="start",
    )
    time_karate = mo.ui.anywidget(PlaySlider(min_value=0, max_value=6, step=0.05, interval_ms=120))
    mo.vstack([start_member, mo.hstack([mo.md("time $t$:"), time_karate], justify="start", align="center")])
    return start_member, time_karate


@app.cell(hide_code=True)
def diffusion_view(A_karate, L_karate, diffusion_exact, members, np, plt, start_member, time_karate):
    _t = float(time_karate.value["value"])
    _start = start_member.value
    _psi0 = np.zeros(L_karate.shape[0])
    _psi0[_start] = 1.0
    _psi = diffusion_exact(L_karate.toarray(), _psi0, _t)
    _lam, _V = np.linalg.eigh(L_karate.toarray())
    _a0 = _V.T @ _psi0
    _terms = np.abs(_a0 * np.exp(-_lam * _t))

    _fig, (_ax, _bar) = plt.subplots(1, 2, figsize=(10.5, 4), width_ratios=[1, 1.1])
    _x, _y = members["x"].to_numpy(), members["y"].to_numpy()
    _rows, _cols = A_karate.nonzero()
    for _i, _j in zip(_rows, _cols):
        if _i < _j:
            _ax.plot([_x[_i], _x[_j]], [_y[_i], _y[_j]], color="0.85", lw=0.8, zorder=1)
    _ax.scatter(_x, _y, s=20 + 2500 * _psi, color="C3", alpha=0.75, edgecolors="k", linewidths=0.5, zorder=2)
    _ax.set_title(
        f"t = {_t:.2f}: member {_start} holds {_psi[_start]:.3f}, even share {1 / len(_psi):.3f}",
        fontsize=10,
    )
    _ax.axis("off")
    _colors = ["C2"] + ["C1"] + ["C0"] * (len(_lam) - 2)
    _bar.bar(range(1, len(_lam) + 1), _terms, color=_colors)
    _bar.set_ylim(0, 1.05 * np.abs(_a0).max())
    _bar.set(xlabel="eigenvector i, sorted by eigenvalue (small to large)", ylabel="$|a_i(0)\\, e^{-\\lambda_i t}|$")
    _bar.set_title("green: eigenvalue 0, orange: $\\lambda_2$", fontsize=10)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 3.1.** (a) Why does the total amount $\sum_i \psi_i(t)$ never change? Use
    the diffusion equation and $\mathbf{L}\mathbf{1} = \mathbf{0}$ (lecture A7). (b) What
    is the state for $t \to \infty$ in a connected network, and which term of the solution
    formula is it? (c) Which eigenvalue decides how long it takes to get there?
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
    ⚙️ **Given.** For the large networks the formula would need all eigenvalues and
    eigenvectors, which does not fit into the browser. `diffuse(L, psi0, t)` solves the
    same equation numerically, in 200 small time steps on the sparse matrix. It is an
    approximation, accurate enough for what follows.
    """)
    return


@app.cell
def given_diffuse(sp, splu):
    def diffuse(L, psi0, t, steps=200):
        """Approximate psi(t) for d psi/dt + L psi = 0, psi(0) = psi0, on a sparse matrix L."""
        _dt = t / steps
        # one implicit step: (1 + dt L) psi_new = psi_old; factorise once, then solve 200 times
        _solver = splu(sp.eye_array(L.shape[0], format="csc") + _dt * L)
        _psi = psi0.astype(float)
        for _ in range(steps):
            _psi = _solver.solve(_psi)
        return _psi

    return (diffuse,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ✏️ **Task 3.2.** Complete two things.

    - `distance_to_even(psi)`: how far a state is from the even one, as
      $\tfrac12 \sum_i |\psi_i - 1/n|$. It is the share of the total amount that would
      still have to move: close to 1 at the start, 0 at the end.
    - `spreading_curve(L, A, times)`: put the whole amount 1 on the node with the largest
      degree, and return the array of `distance_to_even(diffuse(L, psi0, t))` for every
      `t` in `times`.

    The cell after it plots both curves and marks the time $1/\lambda_2$.

    **Target:** for the Internet the distance is **0.344** at $t = 1$ and **0.055** at
    $t = 10$.
    """)
    return


@app.cell
def task_3_2(A_as, A_power, L_as, L_power, diffuse, np):
    times = np.array([0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000])

    def distance_to_even(psi):
        """Share of the total amount that still has to move to reach the even state."""
        # TODO: your code goes here
        raise NotImplementedError("Task 3.2 (a): distance to the even state")

    def spreading_curve(L, A, times):
        """Distance to the even state at every time, starting at the node with the largest degree."""
        # TODO: your code goes here
        raise NotImplementedError("Task 3.2 (b): the spreading curve")

    curve_as = spreading_curve(L_as, A_as, times)
    curve_power = spreading_curve(L_power, A_power, times)
    {"times": times, "Internet (AS)": curve_as.round(3), "power grid": curve_power.round(3)}
    return curve_as, curve_power, times


@app.cell(hide_code=True)
def spreading_plot(curve_as, curve_power, lam2_as, lam2_power, plt, times):
    _fig, _ax = plt.subplots(figsize=(8, 3.6))
    for _curve, _lam2, _name, _color in [
        (curve_as, lam2_as, "Internet (AS)", "C0"),
        (curve_power, lam2_power, "power grid", "C1"),
    ]:
        _ax.semilogx(times, _curve, "o-", color=_color, ms=4, label=_name)
        _ax.axvline(1 / _lam2, color=_color, ls=":", label=f"$1/\\lambda_2$ = {1 / _lam2:.0f}")
    _ax.set(xlabel="time t", ylabel="distance to the even state", ylim=(0, 1.02))
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ❓ **Question 3.2.** Read from your curves: roughly when is each network within 0.1 of
    the even state? Compare with $1/\lambda_2$ from Task 1.2. Does the eigenvalue predict
    the time scale? And where did you see the same contrast between the two networks in
    Exercise 2?
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
    ❓ **Question 3.3: your decision.** A local disturbance appears at one node. For which
    of the two operators is slow spreading good news, and for which is it bad news? Think
    of a fault that should stay local, and of load that should be shared quickly. And name
    two things this diffusion model ignores that matter for a real Internet or a real
    power grid.
    """)
    return


@app.cell(hide_code=True)
def answer_3_3(mo):
    mo.md(r"""
    **Your answer.** Double-click here to write.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4  Save and submit

    ⚙️ **Given.** The same steps as before.

    1. Press `Ctrl+S` (`Cmd+S` on a Mac). Without this step the export is an empty file.
    2. Menu (round button with three lines, top right) → **Export…** → tab **Python** →
       **Export notebook source**.
    3. Rename the downloaded `notebook.py` to `exercise03_<lastname>.py`.
    4. On Moodle, assignment **Exercise 3**: **Add submission**, drag in the file,
       **Save changes**, then **Submit assignment** and confirm. The status must read
       **Submitted for grading**. The deadline is on Moodle.

    Need a break? `Ctrl+S`, then menu → **Share** → **Create WebAssembly link**, and keep
    the link: it restores your work on marimo.app. A reload of this page loses every edit.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ⚙️ **Sources.** Internet and power grid: as in Exercise 2 (SNAP dataset AS-733,
    snapshot of 2 January 2000; D. J. Watts and S. H. Strogatz, Nature 393, 1998). Karate
    club: W. W. Zachary, *An information flow model for conflict and fission in small
    groups*, Journal of Anthropological Research 33 (1977). The drawing of the power grid
    uses positions computed with the stress layout of Graphviz (`neato -Gmode=sgd`).

    ⚙️ **Further reading.** M. E. J. Newman, *Networks*, 2nd edition, Oxford University
    Press 2018: Section 6.14 on the graph Laplacian (graph partitioning, eigenvalues and
    components) and Section 14.7.4 on the Fiedler vector. Splitting a network with the
    eigenvector of $\lambda_2$ goes back to M. Fiedler, *Algebraic connectivity of graphs*,
    Czechoslovak Mathematical Journal 23 (1973), and A. Pothen, H. Simon and K.-P. Liou,
    *Partitioning sparse matrices with eigenvectors of graphs*, SIAM Journal on Matrix
    Analysis and Applications 11 (1990).
    """)
    return


if __name__ == "__main__":
    app.run()
