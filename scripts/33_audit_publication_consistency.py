from pathlib import Path
import math
import re
import pandas as pd

ROOT = Path.home() / "GEO-Cosmology-MCMC"

errors = []

# ------------------------------------------------------------
# Load frozen tables
# ------------------------------------------------------------

constants = pd.read_csv(ROOT / "tables/table_00_geo_constants.csv")
posterior = pd.read_csv(ROOT / "tables/table_01_posterior_summary.csv")
bestfit = pd.read_csv(ROOT / "tables/table_02_bestfit_comparison.csv")
diag = pd.read_csv(ROOT / "tables/table_03_chain_diagnostics.csv")
head = pd.read_csv(ROOT / "tables/table_04_head_to_head.csv")
eta_prof = pd.read_csv(ROOT / "tables/table_05_eta_profile.csv")
eta_cross = pd.read_csv(ROOT / "tables/table_06_eta_cross_configuration.csv")

# ------------------------------------------------------------
# Canonical constants
# ------------------------------------------------------------

def get_constant(name):
    row = constants.loc[constants["quantity"] == name]
    if row.empty:
        raise RuntimeError(f"Missing constant {name}")
    return float(row.iloc[0]["value"])

eta = get_constant("eta")
mu = get_constant("mu_H")
phi = get_constant("Phi")
R = get_constant("R")
alpha = get_constant("alpha")
P = get_constant("P_GEO")

if abs(eta - 0.6) > 1e-12:
    errors.append(f"eta mismatch: {eta}")

if abs(mu - 0.6) > 1e-12:
    errors.append(f"mu_H mismatch: {mu}")

if abs(R - mu**(1/3)) > 1e-12:
    errors.append(f"R != mu^(1/3): R={R}")

alpha_expected = phi * (1-eta) / math.sqrt(2)
if abs(alpha - alpha_expected) > 1e-12:
    errors.append(f"alpha mismatch: {alpha} vs {alpha_expected}")

P_expected = 1 + alpha*(1-R)
if abs(P - P_expected) > 1e-12:
    errors.append(f"P_GEO mismatch: {P} vs {P_expected}")

# ------------------------------------------------------------
# GEO-29 posterior
# ------------------------------------------------------------

geo_h0 = posterior[
    (posterior["run"] == "GEO_29") &
    (posterior["parameter"] == "H0")
].iloc[0]

geo_h0geo = posterior[
    (posterior["run"] == "GEO_29") &
    (posterior["parameter"] == "H0_GEO")
].iloc[0]

if abs(float(geo_h0geo["mean"]) - float(geo_h0["mean"])*P) > 1e-6:
    errors.append("H0_GEO posterior mean does not match P_GEO*H0")

# ------------------------------------------------------------
# Best-fit comparison
# ------------------------------------------------------------

lcdm = bestfit[bestfit["run"] == "LCDM_control"].iloc[0]
geo = bestfit[bestfit["run"] == "GEO_29"].iloc[0]

delta_joint = float(geo["chi2_joint"] - lcdm["chi2_joint"])

h2h = head[head["quantity"] == "chi2 joint"].iloc[0]
delta_table = float(h2h["GEO_minus_LCDM"])

if abs(delta_joint - delta_table) > 1e-6:
    errors.append(
        f"Delta chi2 mismatch: computed={delta_joint}, table={delta_table}"
    )

# ------------------------------------------------------------
# eta profile
# ------------------------------------------------------------

row_geo = eta_prof.iloc[(eta_prof["fc"] - math.sqrt(0.6)).abs().argmin()]

if abs(float(row_geo["eta"]) - 0.6) > 1e-12:
    errors.append("Canonical eta node missing from eta profile")

if abs(float(row_geo["delta_chi2"]) - 0.001005928553241) > 1e-9:
    errors.append(
        f"Unexpected canonical-node delta chi2: {row_geo['delta_chi2']}"
    )

# ------------------------------------------------------------
# Diagnostic
# ------------------------------------------------------------

geo29_diag = diag[diag["run"] == "GEO_29"].iloc[0]
rminus1 = float(geo29_diag["Rminus1_last"])

if abs(rminus1 - 0.0173097526187087) > 1e-10:
    errors.append(f"Unexpected GEO-29 R-1: {rminus1}")

# ------------------------------------------------------------
# Text consistency
# ------------------------------------------------------------

results_text = (ROOT / "RESULTS.md").read_text()

required_strings = [
    "73.388163",
    "73.509859",
    "-19.938923",
    "0.01731",
    "0.599212873731233",
    "0.001005928553",
]

for value in required_strings:
    if value not in results_text:
        errors.append(f"RESULTS.md missing expected value {value}")

# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

print("=" * 78)
print("GEO COSMOLOGY MCMC — PUBLICATION CONSISTENCY AUDIT")
print("=" * 78)

print(f"eta       = {eta:.15f}")
print(f"mu_H      = {mu:.15f}")
print(f"R         = {R:.15f}")
print(f"alpha     = {alpha:.15f}")
print(f"P_GEO     = {P:.15f}")
print()
print(f"GEO-29 H0 mean      = {float(geo_h0['mean']):.9f}")
print(f"GEO-29 H0_GEO mean  = {float(geo_h0geo['mean']):.9f}")
print(f"Delta chi2 joint     = {delta_joint:.9f}")
print(f"GEO-29 R-1           = {rminus1:.12f}")

print()

if errors:
    print("AUDIT FAILED")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("AUDIT PASSED")
print("All frozen numerical quantities are internally consistent.")

