# Notes on export to WASM

## Before exporting

Must re-run `python3 utilities/generate_public_manifest.py` any time you add, remove, or rename a file in `marimo/public/analyses`, before the next `marimo export html-wasm`. See full writeup in `notes/session-log.md`.


## Exporting

```bash
marimo export html-wasm marimo/reader.py -o scratch/reader
```


Then

```bash
cd scratch
scp -r reader/ nsmith@shotaws.holycross.edu:xfer
```

> (Maybe better to keep a subdir of xfer and use rsync?)



then on shotaws.holycross.edu:

```bash
cd xfer/reader
sudo cp -r . $HOME/web/readers/proarchia
```


cleanup on shot:

```
rm -r reader
```
