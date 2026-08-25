# Methods

## Numerical framework

The cosmological inference was performed with:

- Cobaya 3.6.2
- CLASS
- Planck 2018 low-ell TT
- Planck 2018 low-ell EE
- Planck NPIPE CamSpec TTTEEE
- MPI parallel MCMC sampling

Exact software versions are recorded in:

`environment/environment.txt`

and

`environment/requirements_freeze.txt`

## Baseline model

A standard LCDM Planck/NPIPE posterior was first obtained and retained
as the primitive cosmological baseline.

The matched local-H0 control evaluates the local likelihood directly
on the sampled primitive H0.

## GEO realization

The canonical GEO node is fixed to

eta = 3/5.

The Hubble-channel realization uses

mu_H = eta

and the radial law

R = mu_H^(1/3).

The historical expression R = eta^(1/3) is not treated as a general
GEO operator identity.

The fixed GEO projection is

H0_GEO = P_GEO * H0_primitive,

with

P_GEO = 1.083679525222552.

No additional sampled GEO parameter is introduced in the final
GEO-vs-LCDM Hubble comparison.

## Likelihood comparison

The LCDM control evaluates the local-H0 likelihood using H0 directly.

The GEO configuration evaluates the same local likelihood using
H0_GEO while Planck/NPIPE continues to constrain the primitive H0.

This preserves the distinction between the CMB primitive scale and
the projected GEO local realization.

## MCMC

The principal extended GEO calculation uses four MPI chains with
30,000 stored rows per chain.

The final recorded convergence diagnostic was

R-1 = 0.01731.

The pre-specified strict target R-1 < 0.01 was not formally reached.

The result is therefore described as long-chain stable /
near-converged rather than strictly converged according to that
criterion.

## Reproducibility

Configuration files, numerical summaries, diagnostic files,
covariance matrices, software versions and cryptographic hashes are
included in this repository.

Raw-chain SHA256 hashes are recorded in:

`manifests/chains_manifest.txt`

The raw chains are intended to accompany the archival DOI release.
