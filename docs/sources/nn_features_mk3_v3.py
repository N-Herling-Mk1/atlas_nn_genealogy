# -*- coding: utf-8 -*-
"""
nn_features.py  (mk3_v3)
=========================

Single source of truth for the MSVtx ABCD neural-network INPUT columns
(NN1 / NN2, barrel / endcap), plus the per-region preselection and the target.

WHAT CHANGED FROM mk3_v2  (mk3_v3, 2026-07-10)
----------------------------------------------
write_reference_csvs() added at the bottom -- running this file now also
writes kj_nn/kj_Jul_26_NN1.csv and kj_nn/kj_Jul_26_NN2.csv: canonical
feature names only, two columns ('barrel', 'endcap'), confirmed
NN_FEATURES only (candidates / proposed excluded). All provenance stays
HERE in the .py. Nothing else changed.

WHAT CHANGED FROM mk2_v2  (mk3_v2, 2026-07-10)
----------------------------------------------
Amended with Prof. Johns' July-2026 sheet (nn_variables.xlsx, barrel-only):
  * 4 NEW confirmed barrel NN1 features appended (sheet rows 17-20):
    msvtx_caloClusterSumPtScalar + msegUnAssoc_counts/nBIL, nBML, nBOL.
  * NN_CANDIDATES added: sheet entries listed but not yet adopted
    (met_met_NOSYS "add?", msvtx_nRPC), plus endcap analogues of KJ's new
    barrel features -- ALL candidates await KJ's endcap sheet / decision.
  * NN_PROPOSED added: KJ's 7 conceptual NN2 items (no ntuple columns yet).
  * KJ sheet TYPOS documented in comments, NOT added as variants (variants
    remain observation-only): 'track_scaler...' -> track_scalar_sum_pt_barrel,
    'nMSeg_BIBM_ratio_mine' -> nMSeg_ratio_BIBM, 'l3hecal' -> l3hcal,
    'MS1VTx_nTracklet' -> MS1Vtx_nTracklet.
  * Endcap NN_FEATURES unchanged (KJ's sheet is barrel-only); supersedes
    nn_features_mk3_v1.py, which lacked the endcap block entirely.

WHAT CHANGED FROM mk1
---------------------
Feature entries may now be either:

    "name"                       -- exactly one known physical column name
    ["canonical", "alt", ...]    -- multiple KNOWN names for the same quantity;
                                    first entry is canonical, the rest are
                                    audit-verified alternates (never guesses)

The 2026 reprocessed vintage (data24VR + mc23) carries every region-agnostic
feature as canonical+"_raw", while region-tagged features kept their mk1 names.
Verified 2026-07-02 by check_nn_features_v3.py: 26/26 features resolved in all
10 files, both regions, unanimous, zero collisions (mk2_column_audit.json).
The "_raw" alternates below record exactly that finding -- nothing is listed
that was not observed in a real header.

Downstream code always works in CANONICAL names (first element), identical to
mk1. resolve_columns() maps a real header onto canonical names using only the
listed variants:

    import nn_features as nnf
    df = nnf.canonicalize(pd.read_csv(path), region)   # raises if incomplete
    X = df[nnf.all_features(region)]

TARGET POLARITY  (unchanged, still important)
---------------------------------------------
bdt_target == 0  ->  SIGNAL (H->ss MC)
bdt_target == 1  ->  BACKGROUND (data VR)
Inverted from the usual 1=signal convention. NOTE: bdt_target and HTmiss are
NOT present in the 2026 raw CSVs -- they are DERIVED. The mk2 build step must
construct bdt_target (0 for mc23 files, 1 for data24VR files) and locate /
compute HTmiss before required_columns() can be satisfied.

PRESELECTION CAVEAT
-------------------
Selection columns (hits_nRPC / hits_nTGC, nMSeg_BO / nMSeg_EO, trigger flags)
are still single-name entries: they have NOT yet been audited against the 2026
headers. If a "_raw" (or other) variant is confirmed, promote the entry to a
list here -- same convention as the features.
"""

# ----------------------------------------------------------------------
# NN INPUT FEATURES
#   str  = single known physical name
#   list = [canonical, *verified_alternates]   (2026 audit, 2026-07-02)
# ----------------------------------------------------------------------
NN_FEATURES = {
    "barrel": {
        # NN1 -- energy / isolation (Schott 8.3.2)        [index-verified mk1]
        "NN1": [
            "nMSeg_ratio_BIBM",                                  # inner/middle MDT segment ratio
            "track_scalar_sum_pt_barrel",                        # scalar sum ID track pT in cone
            ["MS1Vtx_clusE",             "MS1Vtx_clusE_raw"],    # total calo topocluster E (dR<0.4)
            ["MS1Vtx_avg_clusE",         "MS1Vtx_avg_clusE_raw"],
            ["MS1Vtx_rms_clusE",         "MS1Vtx_rms_clusE_raw"],
            ["MS1Vtx_maxclusE",          "MS1Vtx_maxclusE_raw"],
            ["MS1Vtx_l1ecal",            "MS1Vtx_l1ecal_raw"],   # calo cluster E, 4 EM + 4 HAD layers
            ["MS1Vtx_l1hcal",            "MS1Vtx_l1hcal_raw"],
            ["MS1Vtx_l2ecal",            "MS1Vtx_l2ecal_raw"],
            ["MS1Vtx_l2hcal",            "MS1Vtx_l2hcal_raw"],
            ["MS1Vtx_l3ecal",            "MS1Vtx_l3ecal_raw"],
            ["MS1Vtx_l3hcal",            "MS1Vtx_l3hcal_raw"],
            ["MS1Vtx_l4ecal",            "MS1Vtx_l4ecal_raw"],
            ["MS1Vtx_l4hcal",            "MS1Vtx_l4hcal_raw"],
            ["MS1Vtx_mindR_jetcut",      "MS1Vtx_mindR_jetcut_raw"],       # high-pT track+jet isolation
                                                                          #   KJ: why peak at pi? 2-jet events; investigate
            ["MS1Vtx_sumTrackPt0p2Cone", "MS1Vtx_sumTrackPt0p2Cone_raw"],  # low-pT track isolation (dR<0.2)
            # --- KJ July-2026 additions (sheet rows 17-20) -------------
            "msvtx_caloClusterSumPtScalar",                      # [KJ row 17]
            "msegUnAssoc_counts/nBIL",                           # [KJ row 18] unassoc-seg / chamber-count ratio
            "msegUnAssoc_counts/nBML",                           # [KJ row 19]
            "msegUnAssoc_counts/nBOL",                           # [KJ row 20]
        ],
        # NN2 -- spatial dR / timing / hits (Schott 8.3.2) [index-verified mk1]
        "NN2": [
            "MSTracklet_barrel_avg_dR",                          # avg dR(MSVtx, tracklets)
            "MSTracklet_barrel_rms_dR",                          # rms dR(MSVtx, tracklets)
            "MSeg_barrel_avg_dR",                                # avg dR(MSVtx, muon segments)
            "MSeg_barrel_rms_dR",                                # rms dR(MSVtx, muon segments)
            "MS1Vtx_barrel_hits_ntot",                           # total MDT + trigger hits
            ["MSVtx_MET_dphi",           "MSVtx_MET_dphi_raw"],  # dphi(MSVtx, MET)
            ["MS1Vtx_maxclustime",       "MS1Vtx_maxclustime_raw"],   # calo topocluster time (dR<0.4)
            ["MS1Vtx_avg_clustime",      "MS1Vtx_avg_clustime_raw"],
            ["MS1Vtx_rms_clustime",      "MS1Vtx_rms_clustime_raw"],
            ["MS1Vtx_nTracklet",         "MS1Vtx_nTracklet_raw"],     # # tracklets in cone
        ],
    },
    "endcap": {
        # NN1 -- 2026 audit: existence-verified in all endcap files
        "NN1": [
            "nMSeg_ratio_EIEM",
            "track_scalar_sum_pt_endcap",
            ["MS1Vtx_clusE",             "MS1Vtx_clusE_raw"],
            ["MS1Vtx_avg_clusE",         "MS1Vtx_avg_clusE_raw"],
            ["MS1Vtx_rms_clusE",         "MS1Vtx_rms_clusE_raw"],
            ["MS1Vtx_maxclusE",          "MS1Vtx_maxclusE_raw"],
            ["MS1Vtx_l1ecal",            "MS1Vtx_l1ecal_raw"],
            ["MS1Vtx_l1hcal",            "MS1Vtx_l1hcal_raw"],
            ["MS1Vtx_l2ecal",            "MS1Vtx_l2ecal_raw"],
            ["MS1Vtx_l2hcal",            "MS1Vtx_l2hcal_raw"],
            ["MS1Vtx_l3ecal",            "MS1Vtx_l3ecal_raw"],
            ["MS1Vtx_l3hcal",            "MS1Vtx_l3hcal_raw"],
            ["MS1Vtx_l4ecal",            "MS1Vtx_l4ecal_raw"],
            ["MS1Vtx_l4hcal",            "MS1Vtx_l4hcal_raw"],
            ["MS1Vtx_mindR_jetcut",      "MS1Vtx_mindR_jetcut_raw"],
            ["MS1Vtx_sumTrackPt0p2Cone", "MS1Vtx_sumTrackPt0p2Cone_raw"],
        ],
        # NN2 -- 2026 audit: existence-verified in all endcap files
        "NN2": [
            "MSTracklet_endcap_avg_dR",
            "MSTracklet_endcap_rms_dR",
            "MSeg_endcap_avg_dR",
            "MSeg_endcap_rms_dR",
            "MS1Vtx_endcap_hits_ntot",
            ["MSVtx_MET_dphi",           "MSVtx_MET_dphi_raw"],
            ["MS1Vtx_maxclustime",       "MS1Vtx_maxclustime_raw"],
            ["MS1Vtx_avg_clustime",      "MS1Vtx_avg_clustime_raw"],
            ["MS1Vtx_rms_clustime",      "MS1Vtx_rms_clustime_raw"],
            ["MS1Vtx_nTracklet",         "MS1Vtx_nTracklet_raw"],
        ],
    },
}

# ----------------------------------------------------------------------
# CANDIDATES -- on KJ's sheet (or endcap analogues of his additions) but
# adoption NOT decided. Excluded from features()/required_columns() unless
# include_candidates=True. Endcap entries are analogues awaiting KJ's
# endcap sheet -- flagged, never silently promoted.
# ----------------------------------------------------------------------
NN_CANDIDATES = {
    "barrel": {
        "NN1": [],
        "NN2": [
            "met_met_NOSYS",                     # KJ: "add?"          [sheet NN2 row 1]
            "msvtx_nRPC",                        # listed, no nn2 tag  [sheet NN2 row 2]
        ],
    },
    "endcap": {
        "NN1": [
            "msvtx_caloClusterSumPtScalar",      # region-agnostic; KJ barrel row 17
            "msegUnAssoc_counts/nEIL",           # endcap twin of KJ barrel row 18
            "msegUnAssoc_counts/nEML",           # endcap twin of KJ barrel row 19
            "msegUnAssoc_counts/nEOL",           # endcap twin of KJ barrel row 20
        ],
        "NN2": [
            "met_met_NOSYS",                     # region-agnostic candidate
            "msvtx_nRPC",                        # barrel-hardware count; endcap use = KJ question
        ],
    },
}

# ----------------------------------------------------------------------
# PROPOSED -- KJ's July-2026 wishlist. Concepts, NOT physical columns;
# each needs an ntuple variable (or a build-step derivation) first.
# ----------------------------------------------------------------------
NN_PROPOSED = {
    "barrel": {
        "NN2": [
            "number of clusters in dR",          # [sheet NN2 row 13]
            "eta-phi of pt weighted clusters",   # [sheet NN2 row 14]
            "number of clusters < 300 MeV",      # [sheet NN2 row 15]
            "% of clusters < 300 MeV",           # [sheet NN2 row 16]
            "NSW segment variables",             # [sheet NN2 row 17] (endcap hardware? -- KJ)
            "njets",                             # [sheet NN2 row 18]
            "pt of closest dr jet",              # [sheet NN2 row 19]
        ],
    },
}

# ----------------------------------------------------------------------
# NN PROVENANCE  (Schott Sec. 8.3.2 + KJ extended list, July 2026)
# ----------------------------------------------------------------------
NN_PROVENANCE = {
    "NN1": {
        "family": "Energy / Isolation",
        "detail": "calo topocluster energy (total/avg/rms/max + per-layer "
                  "ECAL/HCAL), track/jet isolation, segment-ratio activity",
        "ref": "Schott thesis Sec. 8.3.2 (NN1 feature set)",
    },
    "NN2": {
        "family": "Spatial-dR / Timing / Hits",
        "detail": "dR(MSVtx, tracklets & muon segments), total MDT+trigger hits, "
                  "topocluster timing, dphi(MSVtx,MET), tracklet multiplicity",
        "ref": "Schott thesis Sec. 8.3.2 (NN2 feature set)",
    },
}

# ----------------------------------------------------------------------
# TARGET  (derived in mk2: 0 for mc23 files, 1 for data24VR files)
# ----------------------------------------------------------------------
TARGET = "bdt_target"          # 0 = SIGNAL, 1 = BACKGROUND
TARGET_SIGNAL = 0
TARGET_BACKGROUND = 1

# ----------------------------------------------------------------------
# PRESELECTION  (single names; audit vs 2026 headers still pending)
# ----------------------------------------------------------------------
SELECTION = {
    "barrel": [
        ("MS1Vtx_barrel_hits_nRPC", ">", 800),
        ("nMSeg_BO", ">", 15),
        ("MS1Vtx_mindR_jetcut", ">", 0.8),
        ("MS1Vtx_sumTrackPt0p2Cone", "<", 5),
        ("pass_muonRoItrigger", "==", 1),
        ("pass_trigger_match", "==", 1),
    ],
    "endcap": [
        ("MS1Vtx_endcap_hits_nTGC", ">", 900),
        ("nMSeg_EO", ">", 15),   # <-- Schott Table 8.2 uses 30 (nEOL); verify
        ("MS1Vtx_mindR_jetcut", ">", 0.8),
        ("MS1Vtx_sumTrackPt0p2Cone", "<", 5),
        ("pass_muonRoItrigger", "==", 1),
        ("pass_trigger_match", "==", 1),
    ],
}
HTMISS_SPLIT = {"column": "HTmiss", "background_max": 40, "signal_min": 40}


# ----------------------------------------------------------------------
# Entry helpers
# ----------------------------------------------------------------------
def _variants(entry):
    """Normalize an entry to a tuple of known names (canonical first)."""
    return (entry,) if isinstance(entry, str) else tuple(entry)


def _canonical(entry):
    """Canonical name of an entry (str itself, or first list element)."""
    return entry if isinstance(entry, str) else entry[0]


# ----------------------------------------------------------------------
# Accessors (mk1 API preserved -- all return CANONICAL names)
# ----------------------------------------------------------------------
def features(region, nn, include_candidates=False):
    """Canonical input-feature list for ('barrel'|'endcap', 'NN1'|'NN2')."""
    entries = list(NN_FEATURES[region][nn])
    if include_candidates:
        entries += NN_CANDIDATES.get(region, {}).get(nn, [])
    return [_canonical(e) for e in entries]


def candidates(region, nn):
    """Sheet-listed but undecided features (canonical names)."""
    return [_canonical(e) for e in NN_CANDIDATES.get(region, {}).get(nn, [])]


def proposed(region, nn):
    """KJ conceptual proposals -- NOT physical columns yet."""
    return list(NN_PROPOSED.get(region, {}).get(nn, []))


def provenance(nn):
    """Feature-family provenance dict for 'NN1' or 'NN2'."""
    return dict(NN_PROVENANCE[nn])


def all_features(region):
    """Canonical NN1 + NN2 features for a region (order preserved)."""
    return features(region, "NN1") + features(region, "NN2")


def feature_entries(region):
    """Raw NN1 + NN2 entries (str or list) for a region, order preserved."""
    return list(NN_FEATURES[region]["NN1"]) + list(NN_FEATURES[region]["NN2"])


def required_columns(region):
    """Everything a training file must contain: features + target + selection."""
    cols = all_features(region) + [TARGET, HTMISS_SPLIT["column"]]
    cols += [c for (c, _op, _v) in SELECTION[region]]
    seen, out = set(), []
    for c in cols:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


# ----------------------------------------------------------------------
# Vintage resolution (new in mk2)
# ----------------------------------------------------------------------
def resolve_columns(columns, region, strict=True):
    """
    Map a real CSV header onto canonical names using ONLY the known variants.

    Returns {physical_name -> canonical_name}; identity entries omitted, so
    it feeds df.rename(columns=...) directly.

    strict=True (default):
      KeyError   -- some feature matches NOTHING in the header
      ValueError -- two known variants of the same feature coexist in the
                    header (e.g. calibrated AND raw): adjudicate, don't guess.
    strict=False: unresolved features are skipped silently.
    """
    have = set(columns)
    rename, missing = {}, []
    for entry in feature_entries(region):
        names = _variants(entry)
        hits = [n for n in names if n in have]
        if not hits:
            missing.append(_canonical(entry))
            continue
        if len(hits) > 1 and strict:
            raise ValueError(
                f"[nn_features] '{_canonical(entry)}' is ambiguous: header "
                f"contains {hits}. Adjudicate before loading.")
        if hits[0] != _canonical(entry):
            rename[hits[0]] = _canonical(entry)
    if missing and strict:
        raise KeyError(
            f"[nn_features] {len(missing)} feature(s) unresolved for region "
            f"'{region}': {missing}. Add a verified variant to NN_FEATURES "
            f"or fix the input file.")
    return rename


def canonicalize(df, region, strict=True):
    """Return df with feature columns renamed to canonical names."""
    return df.rename(columns=resolve_columns(df.columns, region, strict=strict))


# ----------------------------------------------------------------------
# Feature-list CSVs (new in mk3_v3)
#   python nn_features_mk3_v3.py   ->   kj_nn/kj_Jul_26_NN1.csv
#                                       kj_nn/kj_Jul_26_NN2.csv
# Canonical names only, columns 'barrel' / 'endcap'. Confirmed
# NN_FEATURES only -- NN_CANDIDATES / NN_PROPOSED are excluded.
# Provenance lives in this .py, not in the CSVs.
# ----------------------------------------------------------------------
CSV_OUTDIR = "kj_nn"
CSV_BASENAMES = {"NN1": "kj_Jul_26_NN1.csv", "NN2": "kj_Jul_26_NN2.csv"}


def write_reference_csvs(outdir=CSV_OUTDIR):
    """Write one CSV per net (see CSV_BASENAMES): two columns, barrel and
    endcap canonical feature names, positionally paired; a region with
    fewer rows is padded with blanks (endcap NN1 has 16 vs barrel's 20 --
    KJ's July additions are barrel-only). Creates outdir if missing.
    Returns {nn: path_written}."""
    import csv
    import os
    os.makedirs(outdir, exist_ok=True)
    written = {}
    for nn, base in CSV_BASENAMES.items():
        bar = features("barrel", nn)
        end = features("endcap", nn)
        n = max(len(bar), len(end))
        bar += [""] * (n - len(bar))
        end += [""] * (n - len(end))
        path = os.path.join(outdir, base)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["barrel", "endcap"])
            w.writerows(zip(bar, end))
        written[nn] = path
        print(f"[nn_features mk3] wrote {path}  ({n} rows)")
    return written


if __name__ == "__main__":
    for nn in ("NN1", "NN2"):
        p = provenance(nn)
        print(f"{nn}: {p['family']}  ({p['ref']})")
    print()
    for reg in ("barrel", "endcap"):
        multi = sum(1 for e in feature_entries(reg) if not isinstance(e, str))
        print(f"[{reg}]  NN1={len(features(reg,'NN1'))}  "
              f"NN2={len(features(reg,'NN2'))}  "
              f"required={len(required_columns(reg))}  "
              f"multi-name={multi}")
    print()
    write_reference_csvs()
