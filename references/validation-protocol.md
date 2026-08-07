# Validation Protocol

Validate in layers:

1. synthetic exact-W1 and transport-direction tests;
2. point-in-time exclusion and insufficient-history tests;
3. duplicate, zero-weight, missing, and constant-reference tests;
4. schema, fingerprint, and freeze checks;
5. small authorized PandaData smoke query with returned-schema evidence;
6. separate frozen primary evaluation.

Suggested development/validation/freeze periods are complete natural-year segments near 60/20/20. No segment is accepted without declared coverage and sample thresholds. Exploratory variants are grouped before BH-FDR correction; the primary test is not selected after observing results.
