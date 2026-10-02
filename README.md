# Fundamentals of Network Theory: Exercises

Hands-on exercise notebooks for _Fundamentals of Network Theory_ (Prof. Dr. Thomas Engel, [SECAN-Lab](https://www.uni.lu/fstm-en/research-groups/security-and-networking-lab/), University of Luxembourg), Winter 2026/27.

**Open the exercises: https://felixsaretzky.github.io/fundamentals-network-theory-exercises/**

> **Status:** Exercise 0 (getting started) is online. The other exercises are added during the semester.

## For students

1. Open the link above and choose an exercise. Use Chrome or Firefox on a laptop.
2. The notebook runs entirely in your browser: nothing to install, no account needed. Everyone who opens the link works on their own private copy.
3. Solve the tasks and check your results against the target values stated in the notebook.
4. Export your work often: press `Ctrl+S` (`Cmd+S` on Mac), then open the menu (round button with three lines, top right) → `Export…` → `Python` → `Export notebook source`. Without `Ctrl+S`/`Cmd+S` first, the downloaded file is empty.
5. The downloaded file is always called `notebook.py`. Rename it, e.g. to `exercise00_<lastname>.py`.
6. Submit only this `.py` file on Moodle by Sunday 23:59 before the exercise session in which it is discussed: `Add submission`, upload the file, `Save changes`, then `Submit assignment` and confirm. A draft that is never submitted does not count.

**Requirements and common pitfalls**

- Use Chrome or Firefox on a laptop, in a normal window (not private or incognito, not a tablet or phone). Privacy browsers such as Tor or Mullvad block WebAssembly at stricter security levels.
- Reloading or closing the tab loses all your edits, even after `Ctrl+S`/`Cmd+S`. Only the downloaded `.py` file keeps your work.
- To continue later, open your `.py` file locally with `uvx --with numpy --with wigglystuff marimo edit exercise00_<lastname>.py` (needs [uv](https://docs.astral.sh/uv/)). Do not paste it into a cell of the exercise page: marimo then adds only the changed cells, as duplicates.
- The Stop button does not work on this site. Code that runs forever forces a reload, so export before you run long loops.
- The first load takes a moment while the Python runtime (tens of MB) is downloaded.

## Repository layout

| Path                           | Content                                                                    |
| ------------------------------ | -------------------------------------------------------------------------- |
| `notebooks/`                   | Exercise notebooks, exported in edit mode                                  |
| `apps/`                        | Lecture demos, exported in run mode (code hidden)                          |
| `notebooks/public/`, `apps/public/` | Data and assets, loaded via `mo.notebook_location() / "public" / "file"` |
| `examples/`                    | Generic marimo template examples, not published (the build only reads `notebooks/` and `apps/`) |
| `templates/tailwind.html.j2`   | Index page (title, logos, texts)                                           |
| `.github/scripts/build.py`     | Exports all notebooks to WebAssembly and generates the index page          |
| `.github/workflows/deploy.yml` | Builds and deploys to GitHub Pages on every push to `main`                 |

## Local preview

```bash
uv run .github/scripts/build.py
python -m http.server -d _site
```

The site is then available at http://localhost:8000.

## Credits

Exercise track by [Dr.-Ing. Felix Saretzky](https://felixsaretzky.github.io/). Built with [marimo](https://marimo.io), based on the [marimo-gh-pages-template](https://github.com/marimo-team/marimo-gh-pages-template) (Apache-2.0).
