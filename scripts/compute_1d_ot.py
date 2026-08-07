#!/usr/bin/env python3
"""Compute exact one-dimensional weighted empirical transport features."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

ALGORITHM_VERSION = "ot1d-weighted-empirical-v2"


def _clean_pairs(rows, value_key, weight_key="weight"):
    pairs = []
    for row in rows:
        value = row.get(value_key)
        weight = row.get(weight_key, 1.0)
        if value is None or weight is None:
            continue
        try:
            value, weight = float(value), float(weight)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and math.isfinite(weight) and weight > 0:
            pairs.append((value, weight))
    return sorted(pairs)


def _row_weight_status(row, weight_key):
    value = row.get(weight_key, 1.0)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "invalid_weight"
    return "invalid_weight" if not math.isfinite(value) or value <= 0 else "available"


def _normalize(pairs):
    total = sum(weight for _, weight in pairs)
    return [(value, weight / total) for value, weight in pairs] if total > 0 else []


def weighted_quantile(pairs, q):
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
    a, b = _normalize(left), _normalize(right)
    if not a or not b:
        return None
    left_mass, right_mass = defaultdict(float), defaultdict(float)
    for value, mass in a:
        left_mass[value] += mass
    for value, mass in b:
        right_mass[value] += mass
    support = sorted(set(left_mass) | set(right_mass))
    cdf_left = cdf_right = distance = 0.0
    for index, value in enumerate(support[:-1]):
        cdf_left += left_mass[value]
        cdf_right += right_mass[value]
        distance += abs(cdf_left - cdf_right) * (support[index + 1] - value)
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


def _reference_rows(rows, date, window):
    dates = sorted({row["date"] for row in rows if row["date"] < date})
    selected = set(dates[-window:])
    return [row for row in rows if row["date"] in selected]


def _median(values):
    values = sorted(values)
    if not values:
        return None
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2.0


def compute(rows, features, reference_window=252, min_reference_dates=80,
            min_cross_section=2, weight_key="weight", group_key=None,
            view="industry_neutral", feature_weights=None):
    feature_weights = feature_weights or {feature: 1.0 for feature in features}
    if set(feature_weights) != set(features) or any(float(feature_weights[f]) <= 0 for f in features):
        raise ValueError("feature_weights must contain exactly positive weights for every feature")
    current_by_date = defaultdict(list)
    for row in rows:
        current_by_date[row["date"]].append(row)
    output, diagnostics = [], []
    for date in sorted(current_by_date):
        groups = defaultdict(list)
        for row in current_by_date[date]:
            group = row.get(group_key) if view == "industry_neutral" and group_key else "__global__"
            groups[group].append(row)
        for group, group_rows in sorted(groups.items(), key=lambda item: str(item[0])):
            history = _reference_rows(rows, date, reference_window)
            if view == "industry_neutral" and group_key:
                history = [row for row in history if row.get(group_key) == group]
            valid_dates = {row["date"] for row in history}
            feature_state = {}
            for feature in features:
                current = _clean_pairs(group_rows, feature, weight_key)
                reference = _clean_pairs(history, feature, weight_key)
                feature_state[feature] = (current, reference, wasserstein_1(current, reference), _robust_scale(reference))
            group_status = "available"
            if len(valid_dates) < min_reference_dates:
                group_status = "insufficient_history"
            elif len(group_rows) < min_cross_section:
                group_status = "insufficient_cross_section"
            elif any(state[2] is None for state in feature_state.values()):
                group_status = "missing_feature"
            elif any(state[3] is None for state in feature_state.values()):
                group_status = "constant_reference"
            base_diag = {"date": date, "view": view, "group": group, "current_count": len(group_rows),
                         "reference_observation_count": len(history), "reference_start": min(valid_dates) if valid_dates else None,
                         "reference_end": max(valid_dates) if valid_dates else None, "factor_status": group_status,
                         "w1_distance": sum(feature_weights[f] * feature_state[f][2] for f in features) / sum(feature_weights.values()) if group_status == "available" else None}
            diagnostics.append(base_diag)
            group_records = []
            for row in group_rows:
                row_status = _row_weight_status(row, weight_key)
                if row_status == "available" and group_status != "available":
                    row_status = group_status
                if row_status == "available" and any(row.get(feature) is None for feature in features):
                    row_status = "missing_feature"
                record = {"date": date, "symbol": row["symbol"], "group": group, "factor_status": row_status,
                          "algorithm_version": ALGORITHM_VERSION, "reference_start": base_diag["reference_start"],
                          "reference_end": base_diag["reference_end"], "w1_distance": base_diag["w1_distance"], "transport_pressure_raw": None}
                pressures = []
                for feature in features:
                    current, reference, distance, scale = feature_state[feature]
                    value = row.get(feature)
                    if row_status != "available" or value is None or distance is None or scale is None:
                        record[f"{feature}_transport_displacement"] = None
                        continue
                    q = weighted_midpoint_quantile(current, float(value))
                    target = weighted_quantile(reference, q)
                    displacement = target - float(value) if target is not None else None
                    record[f"{feature}_current_quantile"] = q
                    record[f"{feature}_transport_target"] = target
                    record[f"{feature}_transport_displacement"] = displacement
                    if displacement is not None:
                        pressures.append(feature_weights[feature] * displacement / scale)
                if row_status == "available" and len(pressures) == len(features):
                    record["transport_pressure_raw"] = sum(pressures) / sum(feature_weights.values())
                group_records.append(record)
            center = _median([r["transport_pressure_raw"] for r in group_records if r["transport_pressure_raw"] is not None])
            for record in group_records:
                raw = record["transport_pressure_raw"]
                record["transport_pressure"] = raw - center if raw is not None and view == "industry_neutral" else raw
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
