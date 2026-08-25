from pathlib import Path
import math

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# GEO-31 — eta = 3/5 VALIDATION ASSETS
# ============================================================

ROOT = Path("/home/leone/GEO-MCMC")

PUB = ROOT / "publication"
FIGURES = PUB / "figures"
TABLES = PUB / "tables"

VAL_PROFILE = PUB / "validation" / "eta_profile"
VAL_CROSS = PUB / "validation" / "cross_configuration"

for p in [
    FIGURES,
    TABLES,
    VAL_PROFILE,
    VAL_CROSS,
]:
    p.mkdir(parents=True, exist_ok=True)


# ============================================================
# INPUTS
# ============================================================

PROFILE_FILE = (
    ROOT
    / "results/geo/18_fc_profile_wide/"
      "geo18b_fc_profile_coarse.csv"
)

CROSS_FILE = (
    ROOT
    / "results/geo/20_eta_cross_configuration/"
      "20_eta_stability_summary.csv"
)

ALL_CROSS_FILE = (
    ROOT
    / "results/geo/20_eta_cross_configuration/"
      "20_all_profiles.csv"
)


# ============================================================
# GEO CANONICAL NODE
# ============================================================

ETA_GEO = 3.0 / 5.0

FC_GEO = math.sqrt(
    ETA_GEO
)


# ============================================================
# LOAD PROFILE
# ============================================================

profile = pd.read_csv(
    PROFILE_FILE
)

# Normalize column names defensively
profile.columns = [
    c.strip()
    for c in profile.columns
]

if "delta_chi2" not in profile.columns:

    if "Dchi2" in profile.columns:
        profile["delta_chi2"] = profile["Dchi2"]

    elif "chi_total" in profile.columns:
        profile["delta_chi2"] = (
            profile["chi_total"]
            - profile["chi_total"].min()
        )

    elif "chi2" in profile.columns:
        profile["delta_chi2"] = (
            profile["chi2"]
            - profile["chi2"].min()
        )

    else:
        raise RuntimeError(
            "Could not infer delta chi2 column "
            f"from {profile.columns.tolist()}"
        )


# infer fc
if "fc" not in profile.columns:
    raise RuntimeError(
        "Expected fc column in GEO-18 profile"
    )

profile["eta"] = (
    profile["fc"] ** 2
)


# ============================================================
# FIND BEST AND CANONICAL NODE
# ============================================================

ibest = profile[
    "delta_chi2"
].idxmin()

best = profile.loc[
    ibest
]

inode = np.argmin(
    np.abs(
        profile["fc"].to_numpy()
        - FC_GEO
    )
)

node = profile.iloc[
    inode
]


# ============================================================
# PUBLICATION TABLE 05
# ============================================================

table05_cols = []

preferred = [
    "fc",
    "eta",
    "chi_total",
    "chi2",
    "delta_chi2",
    "H0",
    "Omega_m",
    "logA",
    "sigma8",
    "S8",
]

for c in preferred:
    if c in profile.columns:
        table05_cols.append(c)

table05 = profile[
    table05_cols
].copy()

table05.to_csv(
    TABLES / "table_05_eta_profile.csv",
    index=False
)

table05.to_csv(
    VAL_PROFILE / "geo18_eta_profile_source.csv",
    index=False
)


# ============================================================
# FIGURE 04 — PROFILE LIKELIHOOD
# ============================================================

fig, ax = plt.subplots(
    figsize=(8, 5)
)

ax.plot(
    profile["fc"],
    profile["delta_chi2"],
    marker="o",
    markersize=4,
    linewidth=1.5,
    label=r"Profile $\Delta\chi^2(f_c)$"
)

ax.axvline(
    FC_GEO,
    linestyle="--",
    linewidth=1.8,
    label=(
        r"GEO node "
        r"$f_c=\sqrt{3/5}$"
    )
)

ax.axhline(
    1.0,
    linestyle=":",
    linewidth=1.2,
    label=r"$\Delta\chi^2=1$"
)

ax.axhline(
    3.84,
    linestyle=":",
    linewidth=1.2,
    label=r"$\Delta\chi^2=3.84$"
)

ax.scatter(
    [best["fc"]],
    [best["delta_chi2"]],
    s=50,
    label="Profile minimum"
)

ax.scatter(
    [node["fc"]],
    [node["delta_chi2"]],
    s=50,
    label="Canonical GEO node"
)

ax.set_xlabel(
    r"$f_c$"
)

ax.set_ylabel(
    r"$\Delta\chi^2$"
)

ax.set_title(
    r"GEO efficiency profile: "
    r"$f_c$ and canonical $\eta=3/5$ node"
)

ax.legend()

fig.tight_layout()

fig.savefig(
    FIGURES / "figure_04_eta_profile.png",
    dpi=300
)

fig.savefig(
    FIGURES / "figure_04_eta_profile.pdf"
)

plt.close(fig)


# ============================================================
# LOAD CROSS-CONFIGURATION SUMMARY
# ============================================================

cross = pd.read_csv(
    CROSS_FILE
)

cross.columns = [
    c.strip()
    for c in cross.columns
]

required = [
    "test",
    "fc_best",
    "eta_best",
    "delta_chi2_GEO",
]

for c in required:
    if c not in cross.columns:
        raise RuntimeError(
            f"Missing expected column {c}"
        )


# ============================================================
# PUBLICATION TABLE 06
# ============================================================

table06_cols = [
    c
    for c in [
        "test",
        "fc_best",
        "eta_best",
        "delta_chi2_GEO",
        "fc68_low",
        "fc68_high",
        "fc95_low",
        "fc95_high",
        "H0_best",
        "S8_best",
    ]
    if c in cross.columns
]

table06 = cross[
    table06_cols
].copy()

table06.to_csv(
    TABLES / "table_06_eta_cross_configuration.csv",
    index=False
)

table06.to_csv(
    VAL_CROSS / "geo20_eta_cross_configuration_source.csv",
    index=False
)


# Copy full profile source too
all_cross = pd.read_csv(
    ALL_CROSS_FILE
)

all_cross.to_csv(
    VAL_CROSS / "geo20_all_profiles_source.csv",
    index=False
)


# ============================================================
# FIGURE 05 — CROSS-CONFIGURATION eta
# ============================================================

fig, ax = plt.subplots(
    figsize=(9, 5.5)
)

x = np.arange(
    len(cross)
)

eta_best = cross[
    "eta_best"
].to_numpy(float)

ax.scatter(
    x,
    eta_best,
    s=65,
    label=r"Best-fit $\eta=f_c^2$"
)

ax.axhline(
    ETA_GEO,
    linestyle="--",
    linewidth=1.8,
    label=r"Canonical $\eta=3/5$"
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    cross["test"],
    rotation=25,
    ha="right"
)

ax.set_ylabel(
    r"$\eta_{\rm best}$"
)

ax.set_title(
    r"Cross-configuration stability of "
    r"$\eta=f_c^2$"
)

ax.legend()

fig.tight_layout()

fig.savefig(
    FIGURES / "figure_05_eta_cross_configuration.png",
    dpi=300
)

fig.savefig(
    FIGURES / "figure_05_eta_cross_configuration.pdf"
)

plt.close(fig)


# ============================================================
# FIGURE 06 — PENALTY OF CANONICAL NODE
# ============================================================

fig, ax = plt.subplots(
    figsize=(9, 5.5)
)

ax.bar(
    x,
    cross["delta_chi2_GEO"]
)

ax.axhline(
    1.0,
    linestyle="--",
    linewidth=1.2,
    label=r"$\Delta\chi^2=1$"
)

ax.set_xticks(
    x
)

ax.set_xticklabels(
    cross["test"],
    rotation=25,
    ha="right"
)

ax.set_ylabel(
    r"$\Delta\chi^2(\eta=3/5)$"
)

ax.set_title(
    "Likelihood penalty of the canonical GEO node"
)

ax.legend()

fig.tight_layout()

fig.savefig(
    FIGURES / "figure_06_eta_node_penalty.png",
    dpi=300
)

fig.savefig(
    FIGURES / "figure_06_eta_node_penalty.pdf"
)

plt.close(fig)


# ============================================================
# TEXT SUMMARY
# ============================================================

summary = f"""
GEO-31 — eta VALIDATION SUMMARY
================================

Canonical GEO node
------------------
eta_GEO = {ETA_GEO:.15f}
fc_GEO  = {FC_GEO:.15f}

GEO-18 wide profile
-------------------
fc_best       = {best['fc']:.15f}
eta_best      = {best['eta']:.15f}
Delta chi2 min= {best['delta_chi2']:.15f}

Canonical node in profile
-------------------------
fc_node       = {node['fc']:.15f}
eta_node      = {node['eta']:.15f}
Delta chi2 GEO= {node['delta_chi2']:.15f}

Difference
----------
fc_GEO - fc_best =
{FC_GEO - best['fc']:.15e}

eta_GEO - eta_best =
{ETA_GEO - best['eta']:.15e}

Cross-configuration results
---------------------------
Median fc_best =
{cross['fc_best'].median():.15f}

Median eta_best =
{cross['eta_best'].median():.15f}

Mean Delta chi2 GEO =
{cross['delta_chi2_GEO'].mean():.15f}

Max Delta chi2 GEO =
{cross['delta_chi2_GEO'].max():.15f}

Interpretation
--------------
The canonical eta=3/5 node is compared against
profile-likelihood fits in which fc is allowed to vary.

The cross-configuration cases are not all statistically
independent. In particular, the weak-lensing-like cases
reuse common BAO/SN/fs8/CMB information and differ mainly
through their S8 prior.

Therefore this section establishes compatibility and
cross-configuration stability, not a measurement of a
new universal constant.

Correct radial law used elsewhere in GEO:
R = mu^(1/3)
"""

summary_path = (
    PUB
    / "summaries"
    / "GEO_ETA_VALIDATION_SUMMARY.txt"
)

summary_path.write_text(
    summary.strip()
    + "\n"
)


# ============================================================
# FINAL PRINT
# ============================================================

print("=" * 80)
print("GEO-31 VALIDATION ASSETS COMPLETE")
print("=" * 80)

print()
print("GEO-18:")
print(
    f"fc_best  = {best['fc']:.12f}"
)
print(
    f"eta_best = {best['eta']:.12f}"
)
print(
    f"fc_GEO   = {FC_GEO:.12f}"
)
print(
    f"eta_GEO  = {ETA_GEO:.12f}"
)
print(
    f"Dchi2 GEO= {node['delta_chi2']:.12f}"
)

print()
print("GEO-20:")
print(
    cross[
        [
            "test",
            "fc_best",
            "eta_best",
            "delta_chi2_GEO",
        ]
    ].to_string(
        index=False
    )
)

print()
print("Saved:")
print(TABLES / "table_05_eta_profile.csv")
print(TABLES / "table_06_eta_cross_configuration.csv")
print(FIGURES / "figure_04_eta_profile.png")
print(FIGURES / "figure_05_eta_cross_configuration.png")
print(FIGURES / "figure_06_eta_node_penalty.png")
print(summary_path)
