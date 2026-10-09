# -*- coding: utf-8 -*-
"""
nn_features.py  (mk2_v3)
========================

Single source of truth for the MSVtx ABCD neural-network INPUT columns
(NN1 / NN2, barrel / endcap), plus the per-region preselection and the target.

WHAT CHANGED FROM mk2_v2  (mk2_v3, 2026-07-10)
----------------------------------------------
write_reference_csvs() added at the bottom -- running this file now also
writes legacy_nn/legacy_NN1.csv and legacy_nn/legacy_NN2.csv: canonical
feature names only, two columns ('barrel', 'endcap'). All provenance
(variants, comments, refs) stays HERE in the .py. Nothing else changed.

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
            ["MS1Vtx_sumTrackPt0p2Cone", "MS1Vtx_sumTrackPt0p2Cone_raw"],  # low-pT track isolation (dR<0.2)
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
# NN PROVENANCE  (Schott Sec. 8.3.2 -- unchanged from mk1)
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
def features(region, nn):
    """Canonical input-feature list for ('barrel'|'endcap', 'NN1'|'NN2')."""
    return [_canonical(e) for e in NN_FEATURES[region][nn]]


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
# Feature-list CSVs (new in mk2_v3)
#   python nn_features_mk2_v3.py   ->   legacy_nn/legacy_NN1.csv
#                                       legacy_nn/legacy_NN2.csv
# Canonical names only, columns 'barrel' / 'endcap'. Provenance lives
# in this .py, not in the CSVs.
# ----------------------------------------------------------------------
CSV_OUTDIR = "legacy_nn"
CSV_BASENAMES = {"NN1": "legacy_NN1.csv", "NN2": "legacy_NN2.csv"}


def write_reference_csvs(outdir=CSV_OUTDIR):
    """Write one CSV per net (see CSV_BASENAMES): two columns, barrel and
    endcap canonical feature names, positionally paired; a region with
    fewer rows is padded with blanks. Creates outdir if missing.
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
        print(f"[nn_features mk2] wrote {path}  ({n} rows)")
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
