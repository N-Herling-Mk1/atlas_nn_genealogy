<p align="center"><img src="docs/assets/social_card.png" alt="NN Feature Genealogy" width="100%"></p>

# atlas_nn_genealogy

**Live page:** https://n-herling-mk1.github.io/atlas_nn_genealogy/

Version history of the MSVtx ABCD neural-network input features (NN1 / NN2, barrel / endcap).
Static browse page + per-selection downloads (.txt / .csv / .py).

## Versions

| id  | label     | source                                   | kind |
|-----|-----------|------------------------------------------|------|
| mk2 | June 2026 | `sources/nn_features_mk2_v3.py`          | module |
| mk3 | July 2026 | `sources/nn_features_mk3_v3.py`          | module (KJ July sheet) |
| mk4 | Sep 2026  | `sources/nn_variables_2026-09-21.xlsx`   | KJ sheet, applied on top of mk3 |

## Layout

```
sources/    original files, never edited
tools/      build.py: ingest -> verify -> lock -> emit (with progress prints)
registry/   <mk>.json, generated and committed (git diff is the audit trail)
docs/       index.html + generated data.js + copies of sources (the site)
docs/assets header badge, favicon PNGs (16-64), apple-touch-icon, icon_192/512, social_card.png
docs/favicon.svg  vector icon (master) -> python tools/render_icons.py -> favicon.ico + PNGs
assets/     badge.png + favicon_src.png (full-res originals)
tools/card/ social_card.html + render_card.py (re-render the card after edits)
```

## Social card

`docs/assets/social_card.png` (1280x640) is wired into the page's Open Graph / Twitter tags.
For the GitHub repo preview, upload the same file under Settings -> General -> Social preview
(GitHub can't read it from the repo). Re-render after editing the HTML:
```
python tools/card/render_card.py
```

## Build

```
python tools/build.py        # needs openpyxl for the xlsx ingest
```
Then open `docs/index.html`. It works from `file://` because the data is embedded in `data.js`.

## Adding a version

1. Drop the source into `sources/`.
2. Add an entry to `VERSIONS` in `tools/build.py`. A new source *kind* needs an ingest function.
3. Rebuild, review `git diff registry/`, then commit.

## Rules carried from nn_features.py

- Variants are observation-only. Sheet spellings map to canonicals through `TYPO` and are never added as variants.
- Names the sheet uses that the Jul-02 header audit did not see are flagged `unverified_variant`. They are not adopted.
- Module order is canonical. The sheet's row order is kept as `kj_row` / `sheet_order`.
- mk4 endcap check status is read from the sheet's endcap column onto the endcap analogue (`ENDCAP_TWIN`), with a `check_note`.

## Downloads

- **.txt**: canonical names grouped by net / region / status.
- **.csv**: one row per feature: version, net, region, status, position, canonical, variants, first_seen, check, notes.
- **.py**: same entry convention as `nn_features.py` (`"name"` or `["canonical", *alternates]`) plus a `features()` accessor.
  This covers feature lists only. Selection, target and `resolve_columns()` stay in the real module.
- The original source file for each version is linked on the page.
