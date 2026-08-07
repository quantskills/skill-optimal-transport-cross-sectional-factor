# One-Dimensional Optimal Transport

For weighted empirical distributions P and Q, the exact one-dimensional Wasserstein-1 distance is

`W1(P,Q) = integral |F_P(x) - F_Q(x)| dx`.

The implementation integrates CDF differences over the merged support, including duplicate values and normalized positive weights. For an observation x, its mass-midpoint quantile is mapped through the reference quantile function to produce `transport_target`; displacement is `transport_target - x`.

This is a deterministic monotone transport calculation. It is not a learned embedding, neural network, arbitrary optimizer, or guarantee that displacement predicts reversal.
