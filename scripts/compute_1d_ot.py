#!/usr/bin/env python3
"""Compute exact one-dimensional weighted empirical transport features."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ALGORITHM_VERSION = "ot1d-weighted-empirical-v1"


def _clean_pairs(rows, value_key, weight_key="weight"):
    pairs = []
    for row in rows:
        value = row.get(value_key)
        weight = row.get(weight_key, 1.0)
        if value is None or weight is None:
            continue
        value = float(value)
        weight = float(weight)
        if math.isfinite(value) and math.isfinite(weight) and weight > 0:
            pairs.append((value, weight))
    return sorted(pairs)


def _normalize(pairs):
    total = sum(weight for _, weight in pairs)
    if total <= 0:
        return []
    return [(value, weight / total) for value, weight in pairs]


def weighted_quantile(pairs, q):
    """Return the left-continuous weighted empirical quantile."""
    normalized = _normalize(pairs)
    if not normalized:
        return None
    q = min(max(float(q), 0.0), 1.0)
    cumulative = 0.0
    for value, mass in normalized:
        cumulative += mass
        if q <= cumulative or math.isclose(q, cumulative):
            return value
    return normalized[-1][0]


def weighted_midpoint_quantile(pairs, value):
    normalized = _normalize(pairs)
    if not normalized:
        return None
    before = sum(mass for item, mass in normalized if item < value)
    at = sum(mass for item, mass in normalized if item == value)
    return before + at / 2.0


def wasserstein_1(left, right):
    """Integrate the absolute CDF difference over the merged support."""
    a = _normalize(left)
    b = _normalize(right)
    if not a or not b:
        return None
    masses_a = defaultdict(float)
    masses_b = defaultdict(float)
    for value, mass in a:
        masses_a[value] += mass
    for value, mass in b:
        masses_b[value] += mass
    support = sorted(set(masses_a) | set(masses_b))
    cdf_a = cdf_b = distance = 0.0
    for index, value in enumerate(support[:-1]):
        cdf_a += masses_a[value]
        cdf_b += masses_b[value]
        distance += abs(cdf_a - cdf_b) * (support[index + 1] - value)
    return distance


def _robust_scale(pairs):
    values = [value for value, _ in pairs]
    if not values:
        return None
    median = weighted_quantile(pairs, 0.5)
    deviations = sorted((abs(value - median), weight) for value, weight in pairs)
    mad = weighted_quantile(deviations, 0.5)
    if mad is None or mad <= 1e-12:
        spread = max(values) - min(values)
        return spread if spread > 1e-12 else None
    return 1.4826 * mad


def _reference_rows(history, date, window):
    dates = sorted({row["date"] for row in history if row["date"] < date})
    selected = set(dates[-window:])
    return [row for row in history if row["date"] in selected]


def compute(rows, features, reference_window=252, min_reference_dates=80,
            min_cross_section=2, weight_key="weight", group_key=None,
            view="industry_neutral", feature_weights=None):
    """Build row-level transport outputs and date/group diagnostics."""
    feature_weights = feature_weights or {feature: 1.0 for feature in features}
    current_by_date = defaultdict(list)
    for row in rows:
        current_by_date[row["date"]].append(row)
    output = []
    diagnostics = []
    for date in sorted(current_by_date):
        current_rows = current_by_date[date]
        groups = defaultdict(list)
        for row in current_rows:
            group = row.get(group_key) if view == "industry_neutral" and group_key else "__global__"
            groups[group].append(row)
        for group, group_rows in sorted(groups.items(), key=lambda item: str(item[0])):
            history = _reference_rows(rows, date, reference_window)
            if view == "industry_neutral" and group_key:
                history = [row for row in history if row.get(group_key) == group]
            valid_dates = {row["date"] for row in history}
            base_diag = {"date": date, "view": view, "group": group,
                         "current_count": len(group_rows),
                         "reference_observation_count": len(history),
                         "reference_start": min(valid_dates) if valid_dates else None,
                         "reference_end": max(valid_dates) if valid_dates else None,
                         "factor_status": "available"}
            if len(valid_dates) < min_reference_dates:
                base_diag["factor_status"] = "insufficient_history"
            elif len(group_rows) < min_cross_section:
                base_diag["factor_status"] = "insufficient_cross_section"
            feature_state = {}
            for feature in features:
                current = _clean_pairs(group_rows, feature, weight_key)
                reference = _clean_pairs(history, feature, weight_key)
                feature_state[feature] = (current, reference, wasserstein_1(current, reference), _robust_scale(reference))
            if base_diag["factor_status"] == "available":
                base_diag["w1_distance"] = sum(feature_weights[f] * state[2] for f, state in feature_state.items() if state[2] is not None) / sum(feature_weights.values())
            else:
                base_diag["w1_distance"] = None
            diagnostics.append(base_diag)
            for row in group_rows:
                record = {"date": date, "symbol": row["symbol"], "group": group,
                          "factor_status": base_diag["factor_status"],
                          "algorithm_version": ALGORITHM_VERSION,
                          "reference_start": base_diag["reference_start"],
                          "reference_end": base_diag["reference_end"],
                          "w1_distance": base_diag["w1_distance"]}
                pressures = []
                for feature in features:
                    current, reference, distance, scale = feature_state[feature]
                    value = row.get(feature)
                    if value is None or not reference or distance is None or scale is None:
                        record[f"{feature}_displacement"] = None
                        continue
                    q = weighted_midpoint_quantile(current, float(value))
                    target = weighted_quantile(reference, q)
                    displacement = target - float(value) if target is not None else None
                    record[f"{feature}_current_quantile"] = q
                    record[f"{feature}_transport_target"] = target
                    record[f"{feature}_transport_displacement"] = displacement
                    if displacement is not None:
                        pressures.append((feature_weights[feature], displacement / scale))
                if base_diag["factor_status"] == "available" and len(pressures) == len(features):
                    record["transport_pressure"] = sum(weight * value for weight, value in pressures) / sum(feature_weights.values())
                else:
                    record["transport_pressure"] = None
                output.append(record)
    return output, diagnostics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--feature", action="append", required=True)
    parser.add_argument("--group-key", default=None)
    parser.add_argument("--view", choices=["industry_neutral", "global_cross_section"], default="industry_neutral")
    parser.add_argument("--reference-window", type=int, default=252)
    parser.add_argument("--min-reference-dates", type=int, default=80)
    parser.add_argument("--min-cross-section", type=int, default=2)
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    output, diagnostics = compute(rows, args.feature, args.reference_window, args.min_reference_dates, args.min_cross_section, group_key=args.group_key, view=args.view)
    args.out.write_text(json.dumps({"factor_values": output, "diagnostics": diagnostics}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
