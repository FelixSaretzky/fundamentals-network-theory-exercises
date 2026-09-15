# Fundamentals of Network Theory: Exercises

Hands-on exercise notebooks for _Fundamentals of Network Theory_ (Prof. Dr. Thomas Engel, [SECAN-Lab](https://www.uni.lu/fstm-en/research-groups/security-and-networking-lab/), University of Luxembourg), Winter 2026/27.

**Open the exercises: https://felixsaretzky.github.io/fundamentals-network-theory-exercises/**

> **Status:** the notebooks currently on the site are generic examples. The course exercises are added during the semester.

## For students

1. Open the link above and choose an exercise.
2. The notebook runs entirely in your browser: nothing to install, no account needed. Everyone who opens the link works on their own private copy.
3. Solve the tasks and check your results against the target values stated in the notebook.
4. Download your notebook as `.py` after every session. Your progress is only stored in the browser you are using.
5. Submit the `.py` file together with a PDF export via Moodle before the exercise session.

**Requirements and common pitfalls**

- Use a current browser with WebAssembly enabled (Chrome, Firefox, Safari, Edge). Privacy browsers such as Tor or Mullvad block WebAssembly at stricter security levels.
- Private or incognito windows do not keep your progress.
- The first load takes a moment while the Python runtime is downloaded.

## Repository layout

| Path                           | Content                                                                    |
| ------------------------------ | -------------------------------------------------------------------------- |
| `notebooks/`                   | Exercise notebooks, exported in edit mode                                  |
| `apps/`                        | Lecture demos, exported in run mode (code hidden)                          |
| `notebooks/public/`, `apps/public/` | Data and assets, loaded via `mo.notebook_location() / "public" / "file"` |
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

Exercise track by [Felix Saretzky](https://felixsaretzky.github.io/). Built with [marimo](https://marimo.io), based on the [marimo-gh-pages-template](https://github.com/marimo-team/marimo-gh-pages-template) (Apache-2.0).
