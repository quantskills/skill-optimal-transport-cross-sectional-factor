# Optimal Transport Cross-Sectional Factor

> One-line positioning: Build auditable equity factors by transporting weighted point-in-time cross-sectional distributions with exact one-dimensional monotone optimal transport.

## What this is

This Skill does not train black-box models or search arbitrary formulas. It compares each `date × symbol` feature cross-section with a strictly lagged pooled historical reference distribution and emits Wasserstein-1 distance, per-symbol transport displacement, distribution pressure, and quality states. The primary view is predeclared within-industry transport with group centering; global transport remains a separate diagnostic.

Project-configured PandaData-compatible sources may produce the normalized input. This describes a data contract and is not an official endorsement of any provider. MCP is not a runtime dependency; this repository does not install packages, log in, handle credentials, or store tokens.

## Quick start

```bash
python scripts/check_runtime.py
python scripts/normalize_panel.py tests/fixtures/minimal_panel/panel.json --feature feature_a --out /tmp/normalized.json
python scripts/compute_1d_ot.py tests/fixtures/minimal_panel/panel.json --feature feature_a --group-key industry --out /tmp/factor.json
python -m unittest discover -s tests -v
node scripts/validate-qsh-form.mjs SKILL.md
```

## Mathematical contract

For each date and predeclared group:

- build weighted current and historical pooled empirical CDFs;
- use only trading dates `< T`, default window 252 and minimum 80 valid dates;
- compute exact `W1(P,Q) = integral |F_P - F_Q| dx`;
- map each current observation's mass-midpoint quantile into the reference distribution;
- combine declared features with fixed weights into `transport_pressure` without dynamic substitution.

Transport displacement is a falsifiable research variable. It does not imply reversal or a trading direction.

## Boundary

This Skill does not replace `skill-pandadata-api`, `skill-factor-evaluate`, IC/backtest, portfolio optimization, risk models, or data-quality auditors. It does not train GNN, TCN, Transformer, or Autoencoder models, search arbitrary formulas, use future data, or provide investment advice.

## Status

`draft`, registry `validation_level: listed`. Synthetic fixtures validate mechanics only and are not real PandaData validation. Formal runs must verify returned schemas, disclosure availability dates, sample splits, labels, and costs.

## License

GPL-3.0. See [LICENSE](LICENSE).
