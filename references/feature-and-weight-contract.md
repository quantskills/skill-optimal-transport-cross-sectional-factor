# Feature and Weight Contract

Features are declared before execution and have fixed combination weights. Missing core features do not trigger dynamic reweighting. Each row is unique on `date × symbol`; values must be finite. Weights must be finite and non-negative, with zero-weight rows excluded from distribution mass.

The default is equal weight. A user may declare free-float or tradable-market-value weight only when its point-in-time meaning and source field are documented. Industry labels must be versioned and available at T; unclassified rows are excluded from the industry-neutral primary view.
