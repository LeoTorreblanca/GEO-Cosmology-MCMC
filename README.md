# GEO Cosmology MCMC Validation

## Reproducible cosmological tests of the GEO framework

This directory contains the publication-oriented numerical validation
package for the GEO (Hidden Geometry) framework.

The objective of this analysis is to test whether the canonical GEO
geometric node can be propagated through cosmological observables and
compared against a matched ΛCDM control using Planck/NPIPE likelihoods
and a local-H0 likelihood.


## Main numerical result

![Hubble posterior comparison](figures/figure_01_h0_posteriors.png)

The extended GEO calculation yields approximately

$$
H_{0,\rm primitive}=67.72\pm0.49
$$

and

$$
H_{0,\rm GEO}=73.39\pm0.53
\;{\rm km\,s^{-1}\,Mpc^{-1}}.
$$

The matched best-point comparison gives

$$
\Delta\chi^2_{\rm joint}\simeq-19.94,
$$

for GEO minus the ΛCDM + local-H0 control in the exact likelihood
configuration documented here.


---

# 1. Canonical GEO node

The canonical efficiency is

$$
\eta = \frac{3}{5} = 0.6
$$

with

$$
f_c = \sqrt{\eta}
     = 0.774596669241483.
$$

For the Hubble-channel realization used in this analysis,

$$
\mu_H = \eta.
$$

The GEO radial law is

$$
R = \mu_H^{1/3},
$$

giving

$$
R = 0.843432665301749.
$$

The GEO operator values used here are

$$
\Phi = 1.88961381521168
$$

and

$$
\alpha =
\frac{\Phi(1-\eta)}{\sqrt{2}}
=0.534463497023985.
$$

The resulting projection factor is

$$
P_{\rm GEO}
=
1+\alpha(1-R)
=
1.083679525222552.
$$

Thus the local GEO realization is

$$
H_{0,\rm GEO}
=
P_{\rm GEO} H_{0,\rm primitive}.
$$

The radial relation must be interpreted as

$$
R=\mu^{1/3}.
$$

The historical notation \(R=\eta^{1/3}\) is not used as a general
operator identity.

---

# 2. Cosmological data and likelihoods

The principal MCMC analysis uses:

- Planck 2018 low-ℓ TT
- Planck 2018 low-ℓ EE
- Planck NPIPE CamSpec TTTEEE
- a local-H0 likelihood for the joint comparison

The analysis is performed with Cobaya and CLASS.

A matched ΛCDM control is retained for direct comparison.

---

# 3. Independent eta validation

Before the final Hubble MCMC comparison, the canonical GEO node was
tested with profile likelihoods in which \(f_c\) was allowed to vary.

The wide profile gives

$$
f_{c,\rm best}=0.774088414673177
$$

and therefore

$$
\eta_{\rm best}=0.599212873731233.
$$

The canonical prediction is

$$
f_{c,\rm GEO}=0.774596669241483,
\qquad
\eta_{\rm GEO}=0.600000000000000.
$$

At the canonical node,

$$
\Delta\chi^2_{\rm GEO}
=
0.001005928553.
$$

Therefore the canonical GEO node lies essentially at the minimum of
this profile likelihood.

Cross-configuration tests also show that the median preferred value is

$$
\eta=0.6.
$$

These configurations are not all statistically independent.
Consequently, these tests establish compatibility and numerical
stability of the canonical node, not an independent measurement of a
new universal constant.

See:

- `figures/figure_04_eta_profile.pdf`
- `figures/figure_05_eta_cross_configuration.pdf`
- `figures/figure_06_eta_node_penalty.pdf`
- `tables/table_05_eta_profile.csv`
- `tables/table_06_eta_cross_configuration.csv`

---

# 4. ΛCDM versus GEO joint test

The final comparison propagates the same cosmological likelihood
structure through a ΛCDM control and through the canonical GEO Hubble
mapping.

For GEO-29 the posterior primitive Hubble parameter is approximately

$$
H_{0,\rm primitive}
=
67.7213 \pm 0.4884
\ {\rm km\,s^{-1}\,Mpc^{-1}}.
$$

After the canonical GEO projection,

$$
H_{0,\rm GEO}
=
73.3882 \pm 0.5292
\ {\rm km\,s^{-1}\,Mpc^{-1}}.
$$

The best sampled GEO-29 point gives

$$
H_{0,\rm GEO}
=
73.5099
\ {\rm km\,s^{-1}\,Mpc^{-1}}.
$$

The best-point comparison gives

$$
\Delta\chi^2_{\rm CMB}
=
-3.242,
$$

$$
\Delta\chi^2_{\rm local\,H0}
=
-16.697,
$$

and

$$
\Delta\chi^2_{\rm joint}
=
-19.939,
$$

where negative values indicate a lower chi-square for the GEO
configuration relative to the matched ΛCDM+H0 control in this test.

This comparison should be interpreted within the exact likelihood,
parameter and model configuration documented in this repository.

---

# 5. Long-chain stability

The principal extended GEO run uses four MPI chains with 30,000 stored
rows per chain.

Total:

$$
4\times30,000=120,000
$$

stored chain rows.

The final recorded convergence diagnostic is

$$
R-1 \simeq 0.01731.
$$

The pre-specified strict target was

$$
R-1<0.01.
$$

The strict stopping criterion was therefore not formally reached.

The run is consequently reported as a long-chain, numerically stable
result rather than as a formally converged \(R-1<0.01\) chain.

Importantly, the shorter GEO-28B and extended GEO-29 calculations give
closely consistent posterior results:

$$
H_{0,\rm GEO}^{28B}
=
73.3998 \pm 0.4998,
$$

$$
H_{0,\rm GEO}^{29}
=
73.3882 \pm 0.5292.
$$

---

# 6. Figures

The publication package contains:

1. `figure_01_h0_posteriors`
   - comparison of H0 posterior distributions.

2. `figure_02_convergence`
   - MCMC convergence history.

3. `figure_03_H0_Omega_m`
   - joint H0–Omega_m posterior structure.

4. `figure_04_eta_profile`
   - profile likelihood of the GEO efficiency node.

5. `figure_05_eta_cross_configuration`
   - cross-configuration comparison of preferred eta.

6. `figure_06_eta_node_penalty`
   - chi-square penalty of the canonical eta=3/5 node.

Both PDF and PNG versions are supplied.

---

# 7. Tables

Machine-readable CSV tables contain:

- canonical GEO quantities;
- posterior summaries;
- best-fit comparisons;
- chain diagnostics;
- ΛCDM/GEO head-to-head statistics;
- eta profile likelihood;
- cross-configuration eta stability.

See the `tables/` directory.

---

# 8. Reproducibility

The numerical environment has been frozen.

Included are:

- Python version;
- Cobaya version;
- NumPy/Pandas/SciPy versions;
- MPI information;
- package freeze;
- CLASS source hashes;
- GEO-modified CLASS source hashes;
- YAML configurations;
- MCMC checkpoints;
- covariance matrices;
- progress diagnostics;
- SHA256 hashes of the raw chains.

Raw chains are identified in

`manifests/chains_manifest.txt`.

The complete chains should accompany the archival DOI release.

See:

`REPRODUCIBILITY_FREEZE.txt`

for the reproducibility statement.

---

# 9. Directory structure

```text
publication/
├── configs/
├── figures/
├── tables/
├── validation/
├── checkpoints/
├── environment/
├── manifests/
├── checksums/
├── scripts/
├── summaries/
├── logs/
├── README.md
└── REPRODUCIBILITY_FREEZE.txt
