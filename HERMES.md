# Hermes Loader

This repository-local file is a compatibility entry point, not an organization-wide Hermes schema.

Load the root `SKILL.md` as the authoritative contract. Read the necessary references and schemas, then use the deterministic scripts under `scripts/` for normalization, point-in-time reference construction, one-dimensional transport, fingerprinting, and freeze validation.

Use only strictly earlier dates for reference distributions. Require authorization before direct `panda_data` access, external evaluation, or writes. Do not dynamically change feature weights, train black-box models, handle credentials, use private data, or provide investment advice.
