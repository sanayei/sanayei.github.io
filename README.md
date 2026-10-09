# sanayei.github.io

Amir Sanayei's personal site, built with [Quarto](https://quarto.org) and published to GitHub Pages on every push to `main`.

## Write

```bash
cp -r writing/_template writing/<slug>     # set title, date, description, categories: [essay] or [note]
quarto preview                              # live preview while writing
quarto render                               # runs Python locally; results saved in _freeze/
git add -A && git commit -m "..." && git push   # pre-push hook runs the blocklist check
```

## One-time setup on a new machine

```bash
git config core.hooksPath .githooks
```
The blocklist check reads `~/projects/content-engine/config/blocklist.yaml` (override with `BLOCKLIST_PATH`). It fails if the file is missing.
