# src — the Second Language pipeline

Four files, pure standard library, no dependencies.

```bash
python fetch.py            # ~96 MB of inputs into raw/ (skips what is already there)
python build_payload.py    # raw/ -> payload.json   (~2 MB, about a minute)
python inject.py           # payload.json + template.html -> ../index.html
```

| file | what it does |
|---|---|
| `fetch.py` | downloads the xd clue and metadata archives, the ENABLE lexicon and Norvig's word counts into `raw/` |
| `build_payload.py` | reads `raw/`, filters to the 2,457,203 New York Times rows, and writes every number the page shows to `payload.json` |
| `template.html` | the page, with a single `__DATA__` marker where the payload goes |
| `inject.py` | splices the two, then runs `wrap_for_pages.py` and `add_catalog_link.py` |

`raw/` and `payload.json` are git-ignored — the clue archive alone is 93 MB and `fetch.py`
refetches it.

**`inject.py` must run the two catalog tools as its last steps.** Without
`wrap_for_pages.py` the page is an Artifact fragment and GitHub Pages serves it in quirks
mode with no charset, turning every en dash into mojibake; without `add_catalog_link.py`
there is no breadcrumb back to the catalog. Regenerating `index.html` by hand drops both
silently.

The xd archives are regenerated periodically. This build used the generation dated
28 April 2026; a later one will move the figures slightly. `../REBUILD.md` carries a
verification table to check a rebuild against, plus the methodological trap that the first
version of this analysis fell into.
