# Panel and Label Boundary

The output grain is `date × symbol`. T-day values are generated after the close and become effective on T+1. The default handoff label is five-session open-to-open, using an externally declared label builder; this Skill does not run a backtest engine.

Evaluation belongs to existing factor-evaluation/backtest Skills. The primary hypothesis, label, costs, sample split, and acceptance gates must be frozen before execution.
