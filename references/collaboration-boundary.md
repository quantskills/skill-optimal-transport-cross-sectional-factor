# Collaboration Boundary

`skill-pandadata-api` supplies direct SDK documentation and query conventions. `skill-factor-evaluate`, `skill-ic-analysis`, and backtest tools may consume this Skill's panel, but none is a hard runtime dependency. This Skill computes the declared OT representation and records diagnostics; collaborators evaluate it.

Missing collaborators produce `not_checked` or a scoped blocked state. Synthetic collaborator output is never reported as live execution.
