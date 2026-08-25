from pathlib import Path
import hashlib
import platform
import shutil
import subprocess
import sys

ROOT = Path("/home/leone/GEO-MCMC")
PUB = ROOT / "publication"

ENV = PUB / "environment"
CHECKPOINTS = PUB / "checkpoints"
MANIFESTS = PUB / "manifests"
CHECKSUMS = PUB / "checksums"

for p in [ENV, CHECKPOINTS, MANIFESTS, CHECKSUMS]:
    p.mkdir(parents=True, exist_ok=True)


# ============================================================
# FILES TO FREEZE
# ============================================================

files_to_copy = [
    ROOT / "results/lcdm/07_planck_npipe_mcmc_final_mpicd.progress",
    ROOT / "results/lcdm/07_planck_npipe_mcmc_final_mpicd.covmat",

    ROOT / "results/geo/28A_lcdm_planck_plus_localH0_final.checkpoint",
    ROOT / "results/geo/28A_lcdm_planck_plus_localH0_final.progress",
    ROOT / "results/geo/28A_lcdm_planck_plus_localH0_final.covmat",

    ROOT / "results/geo/28B_geo_planck_plus_localH0_final.checkpoint",
    ROOT / "results/geo/28B_geo_planck_plus_localH0_final.progress",
    ROOT / "results/geo/28B_geo_planck_plus_localH0_final.covmat",

    ROOT / "results/geo/29_geo_planck_plus_localH0_converge.checkpoint",
    ROOT / "results/geo/29_geo_planck_plus_localH0_converge.progress",
    ROOT / "results/geo/29_geo_planck_plus_localH0_converge.covmat",
]

copied = []

for src in files_to_copy:
    if src.exists():
        dst = CHECKPOINTS / src.name
        shutil.copy2(src, dst)
        copied.append(dst)


# ============================================================
# ENVIRONMENT
# ============================================================

def run(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True,
            stderr=subprocess.STDOUT
        ).strip()
    except Exception as e:
        return f"ERROR: {e}"


environment = []

environment.append(f"Python: {sys.version}")
environment.append(f"Platform: {platform.platform()}")

environment.append("")
environment.append("Cobaya:")
environment.append(run("python -m pip show cobaya"))

environment.append("")
environment.append("NumPy:")
environment.append(run("python -m pip show numpy"))

environment.append("")
environment.append("Pandas:")
environment.append(run("python -m pip show pandas"))

environment.append("")
environment.append("SciPy:")
environment.append(run("python -m pip show scipy"))

environment.append("")
environment.append("Matplotlib:")
environment.append(run("python -m pip show matplotlib"))

environment.append("")
environment.append("MPI:")
environment.append(run("mpirun --version | head -5"))

environment.append("")
environment.append("CLASS baseline git:")
environment.append(
    run("git -C /home/leone/GEO-MCMC/theory/class rev-parse HEAD 2>/dev/null || true")
)

environment.append("")
environment.append("CLASS GEO/MCMC git:")
environment.append(
    run("git -C /home/leone/GEO-MCMC/theory/class_geo_mcmc rev-parse HEAD 2>/dev/null || true")
)

(ENV / "environment.txt").write_text(
    "\n".join(environment) + "\n"
)


# ============================================================
# PACKAGE SNAPSHOT
# ============================================================

requirements = run("python -m pip freeze")

(ENV / "requirements_freeze.txt").write_text(
    requirements + "\n"
)


# ============================================================
# SOURCE HASHES
# ============================================================

source_files = [
    ROOT / "theory/class/source/input.c",
    ROOT / "theory/class/source/perturbations.c",
    ROOT / "theory/class/source/background.c",
    ROOT / "theory/class/include/perturbations.h",

    ROOT / "theory/class_geo_mcmc/source/input.c",
    ROOT / "theory/class_geo_mcmc/source/perturbations.c",
    ROOT / "theory/class_geo_mcmc/include/perturbations.h",
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


source_lines = []

for p in source_files:
    if p.exists():
        source_lines.append(
            f"{sha256(p)}  {p}"
        )

(CHECKSUMS / "source_sha256.txt").write_text(
    "\n".join(source_lines) + "\n"
)


# ============================================================
# PUBLICATION TREE HASHES
# ============================================================

publication_files = sorted([
    p for p in PUB.rglob("*")
    if p.is_file()
    and "publication_sha256.txt" not in str(p)
])

hash_lines = []

for p in publication_files:
    rel = p.relative_to(PUB)

    hash_lines.append(
        f"{sha256(p)}  {rel}"
    )

(CHECKSUMS / "publication_sha256.txt").write_text(
    "\n".join(hash_lines) + "\n"
)


# ============================================================
# CHAIN MANIFEST
# ============================================================

chain_prefixes = [
    ROOT / "results/lcdm/07_planck_npipe_mcmc_final_mpicd",
    ROOT / "results/geo/28A_lcdm_planck_plus_localH0_final",
    ROOT / "results/geo/28B_geo_planck_plus_localH0_final",
    ROOT / "results/geo/29_geo_planck_plus_localH0_converge",
]

chain_lines = []

for prefix in chain_prefixes:

    chain_lines.append("=" * 80)
    chain_lines.append(str(prefix))
    chain_lines.append("=" * 80)

    for i in range(1, 5):

        f = Path(str(prefix) + f".{i}.txt")

        if not f.exists():
            continue

        size = f.stat().st_size
        digest = sha256(f)

        with open(f) as fh:
            nlines = sum(1 for _ in fh)

        chain_lines.append(
            f"chain {i}: "
            f"bytes={size} "
            f"rows={nlines-1} "
            f"sha256={digest}"
        )

    chain_lines.append("")


(MANIFESTS / "chains_manifest.txt").write_text(
    "\n".join(chain_lines) + "\n"
)


# ============================================================
# REPRODUCIBILITY NOTE
# ============================================================

note = """
GEO COSMOLOGY MCMC — REPRODUCIBILITY FREEZE
===========================================

This directory contains publication-level summaries,
tables, figures, configuration files, diagnostics,
software versions and SHA256 checksums.

Raw MCMC chains are intentionally not duplicated inside
the publication directory.

Their filenames, row counts, byte sizes and SHA256 hashes
are recorded in:

    manifests/chains_manifest.txt

The complete raw chains should be archived in the DOI
repository associated with the publication.

Important convergence statement
--------------------------------
GEO-29 used four MPI chains and reached a final recorded

    R-1 ~= 0.01731

The pre-specified strict target was

    R-1 < 0.01

Therefore the run must not be described as formally
converged under the strict stopping criterion.

It may be described as a long-chain stable or
near-converged numerical result, with the exact
diagnostic reported.

Canonical GEO quantities used in the Hubble test
------------------------------------------------
eta   = 3/5
mu_H  = eta
R     = mu_H^(1/3)

The old documentation identity R = eta^(1/3) is not
used as a general GEO radial law.
"""

(PUB / "REPRODUCIBILITY_FREEZE.txt").write_text(
    note.strip() + "\n"
)


print("=" * 80)
print("GEO-32 REPRODUCIBILITY FREEZE COMPLETE")
print("=" * 80)

print()
print("Copied diagnostics:", len(copied))

print()
print("Created:")
print(ENV / "environment.txt")
print(ENV / "requirements_freeze.txt")
print(CHECKSUMS / "source_sha256.txt")
print(CHECKSUMS / "publication_sha256.txt")
print(MANIFESTS / "chains_manifest.txt")
print(PUB / "REPRODUCIBILITY_FREEZE.txt")
