---
name: optimal-transport-cross-sectional-factor
description: "Build auditable cross-sectional factors with one-dimensional optimal transport from point-in-time market panels. Use when an agent needs to compare weighted feature distributions across dates, compute Wasserstein displacement and transport-pressure features, construct global or industry-neutral panels, or prepare a deterministic handoff to factor evaluation. Do not use this skill to train black-box models, search arbitrary formulas, replace data APIs, backtest portfolios, or issue investment advice."
quantSkills:
  organization: https://github.com/quantskills
  repository: quantskills/skill-optimal-transport-cross-sectional-factor
  repository_url: https://github.com/quantskills/skill-optimal-transport-cross-sectional-factor
  project_type: skill
  collection: factor-research-methods
  license: GPL-3.0
  category: factor
  tags: [optimal-transport, wasserstein, cross-sectional-factor, point-in-time, industry-neutral]
  platforms: [claude-code, codex, openclaw, cursor, hermes]
  language: zh-en
  status: draft
  validation_level: listed
  maintainer_type: community
  requires: []
  summary_zh: 用点时截面分布的单调最优传输构造可审计因子
  summary_en: Build auditable factors from point-in-time cross-sectional transport
---

```json qsh-form
{
  "version": 1,
  "task": {"placeholder": "构造最优传输截面因子", "required": true},
  "fields": [
    {"key": "input_panel", "type": "text", "label": "输入面板"},
    {"key": "feature", "type": "text", "label": "特征列"},
    {"key": "reference_window", "type": "number", "label": "参考窗口"},
    {"key": "neutralization", "type": "select", "label": "截面视角", "options": [
      {"value": "industry_neutral", "label": "行业中性"},
      {"value": "global_cross_section", "label": "全市场"}
    ]},
    {"key": "run_primary_test", "type": "select", "label": "执行主检验", "options": [
      {"value": "false", "label": "仅生成因子"},
      {"value": "true", "label": "确认后执行"}
    ]}
  ],
  "prompt_template": "{{task}}；面板：{{input_panel}}；特征：{{feature}}；窗口：{{reference_window}}；截面：{{neutralization}}；执行主检验：{{run_primary_test}}；附件：{{#attachments}}"
}
```

# Optimal Transport Cross-Sectional Factor

## Scope

This skill turns a declared `date × symbol` market panel into a deterministic research factor. Each day's weighted feature observations are treated as an empirical distribution. A strictly earlier rolling window supplies the reference distribution, and exact one-dimensional monotone transport produces distribution distance, per-symbol displacement, and a fixed transport-pressure factor.

## Use When

Use this skill when the user asks to:

- compare weighted cross-sectional feature distributions across dates;
- compute one-dimensional Wasserstein distance or monotone transport displacement;
- build global or predeclared industry-neutral transport factors;
- produce a point-in-time factor panel and auditable diagnostics for an existing evaluation workflow.

## Do Not Use When

Do not use this skill to:

- discover arbitrary formulas, dynamically select features, or tune against the test set;
- train GNN, TCN, Transformer, Autoencoder, or other black-box models;
- replace `panda_data` API documentation or a factor evaluation/backtest skill;
- use same-day or future observations in the reference distribution;
- issue buy, sell, sizing, or guaranteed-return instructions.

## Data and Point-in-Time Boundary

The input is normalized `date × symbol` data. Every feature must be finite and available by the signal close. Financial or event observations require an explicit point-in-time availability date; fields without that contract are exploratory only. The default reference window is the prior 252 trading dates with at least 80 valid dates. Signal date T is computed after the close and becomes effective on T+1.

PandaData is an optional direct data source contract, not an endorsement or a runtime hard dependency. The repository does not install packages, log in, handle credentials, call MCP, or store tokens.

## Core Contract

For each configured feature, the implementation computes:

- weighted empirical CDFs for the current cross-section and strictly earlier pooled history;
- exact one-dimensional Wasserstein-1 distance using CDF interval overlap;
- the monotone transport target at each current observation's mass midpoint;
- `transport_displacement = transport_target - current_value`;
- a fixed-weight `transport_pressure` combination, with no dynamic reweighting when a feature is missing.

The primary view is `industry_neutral`: run the same procedure within versioned industry groups, then center group results. `global_cross_section` is a separate diagnostic and is never silently substituted for the primary view.

## Output and Validation

Outputs include `date`, `symbol`, feature/value provenance, current/reference quantiles, transport target, displacement, `w1_distance`, `transport_pressure`, reference-window boundaries, coverage, algorithm version, and a fail-closed status. Synthetic fixtures are labeled synthetic and do not validate live PandaData coverage.

The default primary handoff uses a declared five-session open-to-open label. Rank IC is primary, Pearson IC secondary, HAC lag 4, and five equal-weight groups. Costs, coverage, monotonicity, and concentration are acceptance gates. This is a falsifiable research method, not investment advice.

## Local Commands

```bash
python scripts/check_runtime.py
python scripts/normalize_panel.py tests/fixtures/minimal_panel/panel.json --feature feature_a --out /tmp/normalized.json
python scripts/compute_1d_ot.py tests/fixtures/minimal_panel/panel.json --feature feature_a --out /tmp/factor.json
python -m unittest discover -s tests -v
node scripts/validate-qsh-form.mjs SKILL.md
```
