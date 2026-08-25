import glob
import math
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ============================================================
# GEO COSMOLOGY MCMC — PUBLICATION ASSET BUILDER
# ============================================================

ROOT = Path("/home/leone/GEO-MCMC")
OUT = ROOT / "publication"

TABLES = OUT / "tables"
FIGURES = OUT / "figures"
SUMMARIES = OUT / "summaries"

for p in [TABLES, FIGURES, SUMMARIES]:
    p.mkdir(parents=True, exist_ok=True)


# ============================================================
# FROZEN GEO CONSTANTS
# ============================================================

ETA_GEO = 3.0 / 5.0
MU_H = ETA_GEO

PHI = 1.88961381521168

R_GEO = MU_H ** (1.0 / 3.0)

ALPHA_GEO = (
    PHI
    * (1.0 - ETA_GEO)
    / math.sqrt(2.0)
)

P_GEO = (
    1.0
    + ALPHA_GEO
    * (1.0 - R_GEO)
)

H0_LOCAL_REF = 73.04
H0_LOCAL_SIGMA = 1.04


# ============================================================
# RUNS
# ============================================================

RUNS = {
    "LCDM_control": (
        ROOT
        / "results/geo/"
        "28A_lcdm_planck_plus_localH0_final"
    ),

    "GEO_28B": (
        ROOT
        / "results/geo/"
        "28B_geo_planck_plus_localH0_final"
    ),

    "GEO_29": (
        ROOT
        / "results/geo/"
        "29_geo_planck_plus_localH0_converge"
    ),
}


# ============================================================
# UTILITIES
# ============================================================

def load_chains(prefix):

    files = sorted(
        glob.glob(
            str(prefix) + ".[1-4].txt"
        )
    )

    if len(files) != 4:
        raise RuntimeError(
            f"{prefix}: expected 4 chains, "
            f"found {len(files)}"
        )

    dfs = []

    for chain_id, filename in enumerate(files, 1):

        with open(filename) as fh:
            columns = (
                fh.readline()
                .lstrip("#")
                .split()
            )

        d = pd.read_csv(
            filename,
            sep=r"\s+",
            comment="#",
            names=columns,
            engine="python"
        )

        d["chain"] = chain_id

        dfs.append(d)

    return pd.concat(
        dfs,
        ignore_index=True
    )


def weighted_quantile(
    values,
    quantiles,
    weights
):

    values = np.asarray(
        values,
        dtype=float
    )

    weights = np.asarray(
        weights,
        dtype=float
    )

    idx = np.argsort(values)

    x = values[idx]
    w = weights[idx]

    cdf = np.cumsum(w)
    cdf /= cdf[-1]

    return np.interp(
        quantiles,
        cdf,
        x
    )


def stats(
    d,
    parameter
):

    x = d[parameter].to_numpy(float)
    w = d["weight"].to_numpy(float)

    mean = np.average(
        x,
        weights=w
    )

    std = np.sqrt(
        np.average(
            (x - mean) ** 2,
            weights=w
        )
    )

    q025, q16, q50, q84, q975 = (
        weighted_quantile(
            x,
            [
                0.025,
                0.16,
                0.50,
                0.84,
                0.975,
            ],
            w
        )
    )

    return {
        "mean": mean,
        "std": std,
        "median": q50,
        "p2.5": q025,
        "p16": q16,
        "p84": q84,
        "p97.5": q975,
    }


def best_point(d):

    return d.loc[
        d["minuslogpost"].idxmin()
    ]


def read_checkpoint(prefix):

    filename = Path(
        str(prefix) + ".checkpoint"
    )

    text = filename.read_text()

    converged = (
        "converged: true"
        in text.lower()
    )

    rminus1 = np.nan

    for line in text.splitlines():

        if "Rminus1_last:" in line:

            value = (
                line.split(
                    "Rminus1_last:",
                    1
                )[1]
                .strip()
            )

            if value != ".inf":
                rminus1 = float(value)

    return converged, rminus1


# ============================================================
# LOAD
# ============================================================

data = {}

for name, prefix in RUNS.items():

    print(
        "Loading",
        name
    )

    d = load_chains(prefix)

    if name.startswith("GEO"):

        d["H0_GEO"] = (
            d["H0"]
            * P_GEO
        )

    data[name] = d


# ============================================================
# TABLE 0 — GEO CONSTANTS
# ============================================================

constants = pd.DataFrame([
    ["eta", ETA_GEO, "Canonical GEO efficiency"],
    ["mu_H", MU_H, "Hubble-channel realization"],
    ["Phi", PHI, "GEO operator"],
    ["R", R_GEO, "mu_H^(1/3)"],
    ["alpha", ALPHA_GEO, "Phi*(1-eta)/sqrt(2)"],
    ["P_GEO", P_GEO, "1 + alpha*(1-R)"],
    ["H0_local_reference", H0_LOCAL_REF, "External comparison"],
    ["H0_local_sigma", H0_LOCAL_SIGMA, "External likelihood sigma"],
])

constants.columns = [
    "quantity",
    "value",
    "definition",
]

constants.to_csv(
    TABLES / "table_00_geo_constants.csv",
    index=False
)


# ============================================================
# TABLE 1 — POSTERIOR SUMMARY
# ============================================================

parameters = [
    "H0",
    "Omega_m",
    "sigma8",
    "omega_b",
    "omega_cdm",
    "logA",
    "n_s",
    "tau_reio",
]

rows = []

for run_name, d in data.items():

    for parameter in parameters:

        s = stats(
            d,
            parameter
        )

        rows.append({
            "run": run_name,
            "parameter": parameter,
            **s
        })

    if run_name.startswith("GEO"):

        s = stats(
            d,
            "H0_GEO"
        )

        rows.append({
            "run": run_name,
            "parameter": "H0_GEO",
            **s
        })


posterior = pd.DataFrame(
    rows
)

posterior.to_csv(
    TABLES / "table_01_posterior_summary.csv",
    index=False
)


# ============================================================
# TABLE 2 — BEST FIT
# ============================================================

best_rows = []

for run_name, d in data.items():

    b = best_point(d)

    cmb = float(
        b["chi2__CMB"]
    )

    if run_name == "LCDM_control":

        local = float(
            b["chi2__local_H0_control"]
        )

        h0_obs = float(
            b["H0"]
        )

    else:

        local = float(
            b["chi2__local_H0_GEO"]
        )

        h0_obs = float(
            b["H0"]
            * P_GEO
        )

    best_rows.append({
        "run":
            run_name,

        "H0_primitive":
            float(b["H0"]),

        "H0_local_prediction":
            h0_obs,

        "Omega_m":
            float(b["Omega_m"]),

        "sigma8":
            float(b["sigma8"]),

        "chi2_CMB":
            cmb,

        "chi2_local_H0":
            local,

        "chi2_joint":
            cmb + local,

        "minuslogpost":
            float(b["minuslogpost"]),
    })


best_table = pd.DataFrame(
    best_rows
)

best_table.to_csv(
    TABLES / "table_02_bestfit_comparison.csv",
    index=False
)


# ============================================================
# TABLE 3 — DIAGNOSTICS
# ============================================================

diag_rows = []

for run_name, prefix in RUNS.items():

    converged, rminus1 = (
        read_checkpoint(prefix)
    )

    d = data[run_name]

    diag_rows.append({
        "run":
            run_name,

        "rows":
            len(d),

        "total_weight":
            d["weight"].sum(),

        "chains":
            4,

        "Rminus1_last":
            rminus1,

        "strict_converged":
            converged,
    })


diagnostics = pd.DataFrame(
    diag_rows
)

diagnostics.to_csv(
    TABLES / "table_03_chain_diagnostics.csv",
    index=False
)


# ============================================================
# TABLE 4 — HEAD TO HEAD
# ============================================================

lcdm_best = (
    best_table[
        best_table["run"]
        == "LCDM_control"
    ]
    .iloc[0]
)

geo_best = (
    best_table[
        best_table["run"]
        == "GEO_29"
    ]
    .iloc[0]
)


comparison = pd.DataFrame([
    [
        "H0 primitive",
        lcdm_best["H0_primitive"],
        geo_best["H0_primitive"],
        (
            geo_best["H0_primitive"]
            - lcdm_best["H0_primitive"]
        )
    ],

    [
        "H0 local prediction",
        lcdm_best["H0_local_prediction"],
        geo_best["H0_local_prediction"],
        (
            geo_best["H0_local_prediction"]
            - lcdm_best["H0_local_prediction"]
        )
    ],

    [
        "chi2 CMB",
        lcdm_best["chi2_CMB"],
        geo_best["chi2_CMB"],
        (
            geo_best["chi2_CMB"]
            - lcdm_best["chi2_CMB"]
        )
    ],

    [
        "chi2 local H0",
        lcdm_best["chi2_local_H0"],
        geo_best["chi2_local_H0"],
        (
            geo_best["chi2_local_H0"]
            - lcdm_best["chi2_local_H0"]
        )
    ],

    [
        "chi2 joint",
        lcdm_best["chi2_joint"],
        geo_best["chi2_joint"],
        (
            geo_best["chi2_joint"]
            - lcdm_best["chi2_joint"]
        )
    ],
])

comparison.columns = [
    "quantity",
    "LCDM_control",
    "GEO_29",
    "GEO_minus_LCDM",
]

comparison.to_csv(
    TABLES / "table_04_head_to_head.csv",
    index=False
)


# ============================================================
# FIGURE 1 — H0 POSTERIORS
# ============================================================

fig, ax = plt.subplots(
    figsize=(8, 5)
)

lcdm = data["LCDM_control"]
geo = data["GEO_29"]

ax.hist(
    lcdm["H0"],
    bins=80,
    weights=lcdm["weight"],
    density=True,
    histtype="step",
    linewidth=2,
    label="LCDM: H0"
)

ax.hist(
    geo["H0"],
    bins=80,
    weights=geo["weight"],
    density=True,
    histtype="step",
    linewidth=2,
    label="GEO: primitive H0"
)

ax.hist(
    geo["H0_GEO"],
    bins=80,
    weights=geo["weight"],
    density=True,
    histtype="step",
    linewidth=2,
    label="GEO: projected H0"
)

ax.axvline(
    H0_LOCAL_REF,
    linestyle="--",
    linewidth=1.5,
    label="Local reference 73.04"
)

ax.set_xlabel(
    r"$H_0$ [km s$^{-1}$ Mpc$^{-1}$]"
)

ax.set_ylabel(
    "Posterior density"
)

ax.set_title(
    "Planck/NPIPE + local-H0 comparison"
)

ax.legend()

fig.tight_layout()

fig.savefig(
    FIGURES / "figure_01_h0_posteriors.png",
    dpi=300
)

fig.savefig(
    FIGURES / "figure_01_h0_posteriors.pdf"
)

plt.close(fig)


# ============================================================
# FIGURE 2 — CONVERGENCE
# ============================================================

fig, ax = plt.subplots(
    figsize=(8, 5)
)

for run_name, prefix in [
    (
        "LCDM control (28A)",
        RUNS["LCDM_control"]
    ),

    (
        "GEO final (29)",
        RUNS["GEO_29"]
    ),
]:

    progress_file = Path(
        str(prefix) + ".progress"
    )

    if not progress_file.exists():
        continue

    p = pd.read_csv(
        progress_file,
        sep=r"\s+"
    )

    if (
        "N" not in p
        or "Rminus1" not in p
    ):
        continue

    good = (
        np.isfinite(
            p["Rminus1"]
        )
        & (p["Rminus1"] > 0)
    )

    ax.plot(
        p.loc[good, "N"],
        p.loc[good, "Rminus1"],
        label=run_name
    )


ax.axhline(
    0.01,
    linestyle="--",
    linewidth=1.5,
    label="Strict target R-1 = 0.01"
)

ax.axhline(
    0.05,
    linestyle=":",
    linewidth=1.5,
    label="R-1 = 0.05"
)

ax.set_yscale(
    "log"
)

ax.set_xlabel(
    "Accepted samples (combined)"
)

ax.set_ylabel(
    "R - 1"
)

ax.set_title(
    "MCMC convergence history"
)

ax.legend()

fig.tight_layout()

fig.savefig(
    FIGURES / "figure_02_convergence.png",
    dpi=300
)

fig.savefig(
    FIGURES / "figure_02_convergence.pdf"
)

plt.close(fig)


# ============================================================
# FIGURE 3 — H0 vs OMEGA_M
# ============================================================

fig, ax = plt.subplots(
    figsize=(7, 6)
)

# Deterministic thinning for visualization only
lcdm_plot = lcdm.iloc[
    ::max(1, len(lcdm)//6000)
]

geo_plot = geo.iloc[
    ::max(1, len(geo)//6000)
]

ax.scatter(
    lcdm_plot["H0"],
    lcdm_plot["Omega_m"],
    s=4,
    alpha=0.15,
    label="LCDM control"
)

ax.scatter(
    geo_plot["H0"],
    geo_plot["Omega_m"],
    s=4,
    alpha=0.15,
    label="GEO primitive"
)

ax.set_xlabel(
    r"Primitive $H_0$"
)

ax.set_ylabel(
    r"$\Omega_m$"
)

ax.set_title(
    r"$H_0$--$\Omega_m$ posterior structure"
)

ax.legend()

fig.tight_layout()

fig.savefig(
    FIGURES / "figure_03_H0_Omega_m.png",
    dpi=300
)

fig.savefig(
    FIGURES / "figure_03_H0_Omega_m.pdf"
)

plt.close(fig)


# ============================================================
# TEXT SUMMARY
# ============================================================

geo29_h0 = stats(
    geo,
    "H0"
)

geo29_h0geo = stats(
    geo,
    "H0_GEO"
)

delta_joint = (
    geo_best["chi2_joint"]
    - lcdm_best["chi2_joint"]
)


summary = f"""
GEO COSMOLOGY MCMC — PUBLICATION SUMMARY
========================================

Canonical GEO constants
-----------------------
eta       = {ETA_GEO:.15f}
mu_H      = {MU_H:.15f}
Phi       = {PHI:.15f}
R         = {R_GEO:.15f}
alpha     = {ALPHA_GEO:.15f}
P_GEO     = {P_GEO:.15f}

Correct radial law:
R = mu^(1/3)

GEO-29 posterior
----------------
H0 primitive =
{geo29_h0['mean']:.9f} +/- {geo29_h0['std']:.9f}

H0 GEO =
{geo29_h0geo['mean']:.9f} +/- {geo29_h0geo['std']:.9f}

68% H0 GEO =
[{geo29_h0geo['p16']:.9f},
 {geo29_h0geo['p84']:.9f}]

95% H0 GEO =
[{geo29_h0geo['p2.5']:.9f},
 {geo29_h0geo['p97.5']:.9f}]

Best GEO-29 point
-----------------
H0 primitive =
{geo_best['H0_primitive']:.9f}

H0 GEO =
{geo_best['H0_local_prediction']:.9f}

chi2 CMB =
{geo_best['chi2_CMB']:.6f}

chi2 local H0 =
{geo_best['chi2_local_H0']:.6f}

chi2 joint =
{geo_best['chi2_joint']:.6f}

Matched LCDM control
--------------------
chi2 joint =
{lcdm_best['chi2_joint']:.6f}

GEO - LCDM
----------
Delta chi2 joint =
{delta_joint:.6f}

Convergence
-----------
See table_03_chain_diagnostics.csv.

GEO-29 did not formally satisfy the pre-specified
R-1 < 0.01 criterion.

Its final recorded R-1 is approximately 0.0173.

Therefore the numerical result must be reported as
a long-chain stable / near-converged result, not as
strict R-1 < 0.01 convergence.

Interpretation
--------------
The fixed GEO projection preserves a primitive H0
near the Planck/NPIPE-preferred scale while producing
a projected local H0 near 73.4 km/s/Mpc.

The fixed projection does not introduce an additional
sampled cosmological parameter in this comparison.

This numerical result does not by itself establish
eta = 3/5 as a universal constant of nature.
"""

summary_file = (
    SUMMARIES
    / "GEO_MCMC_PUBLICATION_SUMMARY.txt"
)

summary_file.write_text(
    summary.strip()
    + "\n"
)


print()
print("=" * 72)
print("PUBLICATION ASSETS COMPLETE")
print("=" * 72)

print()
print(constants)
print()
print(comparison)

print()
print("Files:")
print(TABLES)
print(FIGURES)
print(summary_file)
