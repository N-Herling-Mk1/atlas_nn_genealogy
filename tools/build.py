# -*- coding: utf-8 -*-
"""
build.py  --  atlas_nn_genealogy
================================

    python tools/build.py

  [1/4] INGEST   sources/  ->  one record per version (mk2, mk3, mk4)
                 mk2, mk3 : imported from the nn_features_*.py modules
                            (+ trailing # comments scraped as notes)
                 mk4      : parsed from Prof. Johns' sheet (2026-09-21)
  [2/4] VERIFY   canonical names, duplicates, typo map coverage
  [3/4] LOCK     registry/<mk>.json  (committed -- `git diff` is the audit)
  [4/4] EMIT     docs/data.js (embedded, so the page works from file://,
                 GitHub Pages, or a Flask static route) + docs/sources/

Adding a version: drop the source file in sources/, add a VERSIONS entry
and (if it is a new source kind) an ingest function. Nothing is hand-
transcribed; every name on the page traces to a source file.
"""
import datetime as _dt
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC, REG, DOCS = ROOT / "sources", ROOT / "registry", ROOT / "docs"

VERSIONS = [
    {"id": "mk2", "label": "June 2026", "date": "2026-06",
     "file": "nn_features_mk2_v3.py", "kind": "module",
     "summary": "Legacy set (Schott thesis 8.3.2) with audit-verified _raw "
                "alternates for the 2026 reprocessed vintage."},
    {"id": "mk3", "label": "July 2026", "date": "2026-07",
     "file": "nn_features_mk3_v3.py", "kind": "module",
     "summary": "Prof. Johns July sheet: 4 new barrel NN1 features; "
                "candidates and conceptual proposals tracked separately."},
    {"id": "mk4", "label": "Sep 2026", "date": "2026-09-21",
     "file": "nn_variables_2026-09-21.xlsx", "kind": "kj_sheet",
     "inherits": "mk3",
     "summary": "Prof. Johns Sep-21 review: per-feature barrel/endcap "
                "cross-check status, distribution comments, three NN1 "
                "isolation 'need' items."},
]

# KJ sheet spellings -> existing canonicals (never added as variants)
TYPO = {
    "track_scaler_sum_pt_barrel": "track_scalar_sum_pt_barrel",
    "nMSeg_BIBM_ratio_mine": "nMSeg_ratio_BIBM",
    "MS1Vtx_l3hecal": "MS1Vtx_l3hcal",
    "MS1VTx_nTracklet": "MS1Vtx_nTracklet",
}
# barrel name -> endcap analogue (used to place the sheet's endcap column)
ENDCAP_TWIN = {
    "nMSeg_ratio_BIBM": "nMSeg_ratio_EIEM",
    "track_scalar_sum_pt_barrel": "track_scalar_sum_pt_endcap",
    "MSeg_barrel_avg_dR": "MSeg_endcap_avg_dR",
    "MSeg_barrel_rms_dR": "MSeg_endcap_rms_dR",
    "MSTracklet_barrel_avg_dR": "MSTracklet_endcap_avg_dR",
    "MSTracklet_barrel_rms_dR": "MSTracklet_endcap_rms_dR",
    "MS1Vtx_barrel_hits_ntot": "MS1Vtx_endcap_hits_ntot",
    "msegUnAssoc_counts/nBIL": "msegUnAssoc_counts/nEIL",
    "msegUnAssoc_counts/nBML": "msegUnAssoc_counts/nEML",
    "msegUnAssoc_counts/nBOL": "msegUnAssoc_counts/nEOL",
}

REGIONS, NETS = ("barrel", "endcap"), ("NN1", "NN2")


def log(stage, msg):
    print(f"[{stage}] {msg}", flush=True)


# ---------------------------------------------------------------- INGEST
def _load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _scrape_comments(path):
    """(section, region, canonical) -> trailing comment text.
    Comment-only continuation lines append to the previous entry."""
    notes, section, region, last = {}, None, None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(NN_FEATURES|NN_CANDIDATES|NN_PROPOSED)\s*=", line)
        if m:
            section, region, last = m.group(1), None, None
            continue
        if re.match(r"^[A-Za-z_]+\s*=|^def ", line):   # any other top-level block
            section, region, last = None, None, None
            continue
        m = re.match(r'^\s{4}"(barrel|endcap)"\s*:', line)
        if m and section:
            region = m.group(1)
            continue
        if not (section and region):
            continue
        q = re.search(r'"([^"]+)"', line)
        c = line.split("#", 1)[1].strip() if "#" in line else ""
        if q and not line.strip().startswith(("#", '"NN1"', '"NN2"')):
            last = (section, region, q.group(1))
            if c:
                notes[last] = c
        elif line.strip().startswith("#") and last and line.index("#") > 40:
            notes[last] = (notes.get(last, "") + " " + c).strip()
    return notes


def _canon(e):
    return e if isinstance(e, str) else e[0]


def _variants(e):
    return [] if isinstance(e, str) else list(e[1:])


def ingest_module(v):
    path = SRC / v["file"]
    mod = _load_module(path)
    notes = _scrape_comments(path)
    feats = []
    for sec, status in (("NN_FEATURES", "confirmed"),
                        ("NN_CANDIDATES", "candidate"),
                        ("NN_PROPOSED", "proposed")):
        block = getattr(mod, sec, {})
        for region in REGIONS:
            for net in NETS:
                for i, e in enumerate(block.get(region, {}).get(net, [])):
                    feats.append({
                        "canonical": _canon(e), "variants": _variants(e),
                        "net": net, "region": region, "status": status,
                        "position": i + 1 if status == "confirmed" else None,
                        "note": notes.get((sec, region, _canon(e)), ""),
                    })
    return {
        "features": feats,
        "selection": {r: [list(t) for t in mod.SELECTION[r]] for r in REGIONS},
        "target": {"column": mod.TARGET, "signal": mod.TARGET_SIGNAL,
                   "background": mod.TARGET_BACKGROUND},
        "provenance": mod.NN_PROVENANCE,
    }


def _sheet_canon(name):
    raw = name.endswith("_raw")
    base = name[:-4] if raw else name
    return TYPO.get(base, base), raw


def ingest_kj_sheet(v, parent):
    import openpyxl
    ws = openpyxl.load_workbook(SRC / v["file"], data_only=True).active
    date = ws["H1"].value
    check_date = date.strftime("%Y-%m-%d") if isinstance(date, _dt.datetime) else str(date)

    def val(c):
        x = ws[c].value
        return x.strip() if isinstance(x, str) else x

    rows = []
    for r in range(3, ws.max_row + 1):
        name = val(f"E{r}")
        if not name:
            continue
        rows.append({"row": r, "nn1_n": val(f"A{r}"), "nn2_n": val(f"B{r}"),
                     "nh": val(f"C{r}") or "", "kj": val(f"D{r}") or "",
                     "name": name, "comment": val(f"G{r}") or "",
                     "barrel": val(f"H{r}") or "", "endcap": val(f"I{r}") or ""})
    log("ingest", f"  sheet rows with a name: {len(rows)}  (check date {check_date})")

    # start from the parent version; the sheet annotates and amends it
    feats = [dict(f) for f in parent["features"]]
    idx = {(f["net"], f["region"], f["canonical"]): f for f in feats}
    unmatched, sheet_order = [], {"NN1": [], "NN2": []}

    for row in rows:
        is_nn1 = isinstance(row["nn1_n"], int) or row["kj"] == "nn1"
        net = "NN1" if is_nn1 else "NN2"
        num = row["nn1_n"] if is_nn1 else row["nn2_n"]
        looks_like_column = re.fullmatch(r"[A-Za-z0-9_/]+", row["name"]) is not None
        canon, raw = _sheet_canon(row["name"]) if looks_like_column else (row["name"], False)
        tag = row["kj"]
        if not looks_like_column and canon.endswith(" - need"):
            canon, tag = canon[:-len(" - need")], (tag + " / need").strip(" /")
        kj_meta = {"kj_row": row["row"], "kj_n": num, "kj_tag": tag,
                   "kj_comment": row["comment"], "nh_note": row["nh"],
                   "sheet_name": row["name"]}

        if not looks_like_column or (net, "barrel", canon) in idx and \
                idx[(net, "barrel", canon)]["status"] == "proposed":   # concepts
            key = (net, "barrel", canon)
            if key not in idx:
                f = {"canonical": canon, "variants": [], "net": net,
                     "region": "barrel", "status": "proposed",
                     "position": None, "note": ""}
                feats.append(f)
                idx[key] = f
            idx[key].update(kj_meta)
            continue

        hit = False
        for region, status_col in (("barrel", "barrel"), ("endcap", "endcap")):
            rc = canon if region == "barrel" else ENDCAP_TWIN.get(canon, canon)
            f = idx.get((net, region, rc))
            if not f:
                continue
            hit = True
            f.update(kj_meta)
            f["check"] = row[status_col] or "unchecked"
            f["check_date"] = check_date
            if region == "endcap" and rc != canon:
                f["check_note"] = f"sheet lists barrel name {canon}; status read from endcap column"
            if raw and f"{rc}_raw" not in f["variants"]:
                f["unverified_variant"] = f"{rc}_raw"
        if not hit:
            unmatched.append(row["name"])
        elif row["kj"] in ("nn1", "nn2"):
            sheet_order[net].append(canon)

    if unmatched:
        log("ingest", f"  !! sheet names with no parent feature: {unmatched}")
    return {
        "features": feats,
        "selection": parent["selection"], "target": parent["target"],
        "provenance": parent["provenance"],
        "sheet_order": sheet_order, "check_date": check_date,
    }


# ---------------------------------------------------------------- VERIFY
def verify(rec):
    seen, problems = set(), []
    for f in rec["features"]:
        k = (f["net"], f["region"], f["canonical"], f["status"])
        if k in seen:
            problems.append(f"duplicate {k}")
        seen.add(k)
        if f["status"] != "proposed" and re.search(r"\s", f["canonical"]):
            problems.append(f"whitespace in column name {f['canonical']!r}")
    for region in REGIONS:
        for net in NETS:
            pos = [f["position"] for f in rec["features"]
                   if f["region"] == region and f["net"] == net
                   and f["status"] == "confirmed"]
            if pos != list(range(1, len(pos) + 1)):
                problems.append(f"{region}/{net} positions not contiguous: {pos}")
    return problems


# ---------------------------------------------------------------- QUESTIONS
def open_questions(rec, vid):
    q = []
    if vid == "mk3":
        q = ["Barrel NN2: adopt met_met_NOSYS ('add?') and msvtx_nRPC (untagged)?",
             "Endcap NN1: adopt msvtx_caloClusterSumPtScalar + nEIL/nEML/nEOL twins?",
             "'NSW segment variables' -- endcap hardware? which columns?",
             "msvtx_nRPC is barrel trigger hardware -- intended for endcap at all?"]
    if vid == "mk4":
        F = rec["features"]
        diff = sorted({f["canonical"] for f in F
                       if f.get("check", "").startswith("sign")})
        unch = sorted({f["canonical"] for f in F if f.get("check") == "unchecked"
                       and f["status"] != "proposed"})
        unv = sorted({f["unverified_variant"] for f in F if f.get("unverified_variant")})
        if diff:
            q.append(f"Cross-check 'significantly different' for {', '.join(diff)} "
                     "(both regions): whose definition is right? Blocks NN2 retrain?")
        if unch:
            q.append(f"No barrel/endcap check recorded for {', '.join(unch)}.")
        q.append("Endcap column reads 'ok' on the nBIL/nBML/nBOL rows: does that "
                 "promote the nEIL/nEML/nEOL twins from candidate to confirmed?")
        q.append("NN1 'need' rows (low-pT track iso, high-pT track iso, jet iso): "
                 "MS1Vtx_sumTrackPt0p2Cone and MS1Vtx_mindR_jetcut already target "
                 "these -- what is missing?")
        if unv:
            q.append(f"Sheet uses _raw on {len(unv)} region-tagged names "
                     f"(e.g. {unv[0]}); the Jul-02 header audit found those WITHOUT "
                     "_raw. Re-audit before adding as variants.")
        q.append("Sheet row order differs from module order (NN1 rows 1/2 swapped; "
                 "NN2 reordered). Module order kept -- only matters if a saved "
                 "model depends on column order.")
        q.append("Carried from mk3, still open: met_met_NOSYS, msvtx_nRPC, "
                 "NSW segment variables.")
    return q


# ---------------------------------------------------------------- EMIT
def genealogy(records):
    """(net, region, canonical) -> {version: status}."""
    g = {}
    for vid, rec in records.items():
        for f in rec["features"]:
            key = f"{f['net']}|{f['region']}|{f['canonical']}"
            g.setdefault(key, {})[vid] = f["status"]
    return g


def main():
    print("=" * 64)
    print(" atlas_nn_genealogy build")
    print("=" * 64)
    records = {}
    for i, v in enumerate(VERSIONS, 1):
        log("1/4 ingest", f"({i}/{len(VERSIONS)}) {v['id']}  <-  sources/{v['file']}")
        if v["kind"] == "module":
            rec = ingest_module(v)
        else:
            rec = ingest_kj_sheet(v, records[v["inherits"]])
        rec.update({k: v[k] for k in ("id", "label", "date", "summary")})
        rec["source"] = f"sources/{v['file']}"
        rec["questions"] = open_questions(rec, v["id"])
        n = {s: sum(f["status"] == s for f in rec["features"])
             for s in ("confirmed", "candidate", "proposed")}
        log("1/4 ingest", f"      confirmed={n['confirmed']}  candidate={n['candidate']}  "
                          f"proposed={n['proposed']}")
        records[v["id"]] = rec

    bad = 0
    for vid, rec in records.items():
        p = verify(rec)
        bad += len(p)
        log("2/4 verify", f"{vid}: " + ("OK" if not p else f"{len(p)} problem(s)"))
        for x in p:
            log("2/4 verify", f"   !! {x}")
    if bad:
        sys.exit("[2/4 verify] FAILED -- registry not written")

    REG.mkdir(exist_ok=True)
    for vid, rec in records.items():
        out = REG / f"{vid}.json"
        out.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        log("3/4 lock", f"wrote {out.relative_to(ROOT)}")

    payload = {"built": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
               "versions": [records[v["id"]] for v in VERSIONS],
               "genealogy": genealogy(records)}
    (DOCS / "sources").mkdir(parents=True, exist_ok=True)
    (DOCS / "data.js").write_text(
        "// generated by tools/build.py -- do not edit\nwindow.NN_GENEALOGY = "
        + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")
    log("4/4 emit", "wrote docs/data.js")
    for v in VERSIONS:
        shutil.copy2(SRC / v["file"], DOCS / "sources" / v["file"])
    log("4/4 emit", f"copied {len(VERSIONS)} source files -> docs/sources/")
    print("=" * 64)
    print(" done -- open docs/index.html")
    print("=" * 64)


if __name__ == "__main__":
    main()
