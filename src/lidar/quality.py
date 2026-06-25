"""
quality.py

Quality-control utilities for near-surface lidar signal processing.

This module contains functions for identifying range gates and profiles that
may be affected by near-field contamination, saturation, hard targets, ground
intersections, low signal-to-noise ratio, or beam blockage.

The goal is not to delete questionable data, but to create explicit quality
flags that can be carried through signal processing and spatial-temporal
alignment.

Author: Benjamin Marosites
Created: June 2026
Project: Dissertation research — spatial-temporal lidar alignment
"""

from __future__ import annotations

import numpy as np
import pandas as pd

def flag_near_field(
    range_m: np.ndarray,
    min_valid_range_m: float,
) -> np.ndarray:
    """
    Flag range gates within the near-field exclusion distance.

    Parameters
    ----------
    range_m : np.ndarray
        Range from the lidar, in meters.
    min_valid_range_m : float
        Minimum range considered valid for atmospheric interpretation.

    Returns
    -------
    np.ndarray
        Boolean array where True indicates a near-field range gate.
    """
    range_m = np.asarray(range_m, dtype=float)

    return range_m < min_valid_range_m

def flag_saturation(
    signal: np.ndarray,
    saturation_threshold: float,
) -> np.ndarray:
    """
    Flag range gates where the signal exceeds a saturation threshold.

    Parameters
    ----------
    signal : np.ndarray
        Raw or corrected lidar signal.
    saturation_threshold : float
        Signal value above which the detector or recorded signal is considered
        saturated or physically unreliable.

    Returns
    -------
    np.ndarray
        Boolean array where True indicates possible saturation.
    """
    signal = np.asarray(signal, dtype=float)

    return signal >= saturation_threshold

def flag_hard_targets(
    signal: np.ndarray,
    window_bins: int = 7,
    threshold_multiplier: float = 8.0,
) -> np.ndarray:
    """
    Flag sharp, localized signal spikes that may indicate hard targets.

    This function compares each signal value to a rolling median background.
    Large positive departures from the local median are flagged.

    Parameters
    ----------
    signal : np.ndarray
        Raw or background-corrected lidar signal.
    window_bins : int
        Rolling window size in bins used to estimate the local median.
    threshold_multiplier : float
        Multiplier applied to the local median absolute deviation.

    Returns
    -------
    np.ndarray
        Boolean array where True indicates a possible hard-target return.
    """
    signal = np.asarray(signal, dtype=float)
    series = pd.Series(signal)

    local_median = series.rolling(
        window=window_bins,
        center=True,
        min_periods=1,
    ).median()

    local_anomaly = series - local_median

    local_mad = local_anomaly.abs().rolling(
        window=window_bins,
        center=True,
        min_periods=1,
    ).median()

    # Avoid division by zero or unrealistically tiny thresholds.
    local_mad = local_mad.replace(0, np.nan)

    flag = local_anomaly > threshold_multiplier * local_mad

    return flag.fillna(False).to_numpy()

def flag_blocked_after_target(
    hard_target_flag: np.ndarray,
    range_m: np.ndarray | None = None,
    buffer_bins: int = 1,
) -> np.ndarray:
    """
    Flag range gates after the first detected hard target.

    This is a conservative screening step for beams that may be blocked by
    ground, vegetation, buildings, or other non-atmospheric targets.

    Parameters
    ----------
    hard_target_flag : np.ndarray
        Boolean array where True indicates a possible hard-target return.
    range_m : np.ndarray or None
        Range from lidar, in meters. Included for future expansion and
        readability; not required by the current implementation.
    buffer_bins : int
        Number of bins after the first hard target to allow before flagging
        the beam as blocked.

    Returns
    -------
    np.ndarray
        Boolean array where True indicates the beam may be blocked beyond a
        hard target.
    """
    hard_target_flag = np.asarray(hard_target_flag, dtype=bool)

    blocked = np.zeros_like(hard_target_flag, dtype=bool)

    hard_target_indices = np.where(hard_target_flag)[0]

    if len(hard_target_indices) == 0:
        return blocked

    first_target_idx = hard_target_indices[0]
    start_block_idx = first_target_idx + buffer_bins + 1

    if start_block_idx < len(blocked):
        blocked[start_block_idx:] = True

    return blocked

def flag_possible_ground_intersection(
    range_m: np.ndarray,
    elevation_deg: float,
    lidar_height_m: float,
) -> np.ndarray:
    """
    Flag range gates at or beyond the approximate ground-intersection distance.

    This assumes flat terrain and uses the elevation angle relative to
    horizontal. Negative elevation angles point downward.

    Parameters
    ----------
    range_m : np.ndarray
        Range from lidar, in meters.
    elevation_deg : float
        Beam elevation angle in degrees relative to horizontal.
        Negative values indicate downward-pointing beams.
    lidar_height_m : float
        Height of the lidar above the local ground surface, in meters.

    Returns
    -------
    np.ndarray
        Boolean array where True indicates the range gate is at or beyond the
        estimated ground-intersection distance.
    """
    range_m = np.asarray(range_m, dtype=float)

    if elevation_deg >= 0:
        return np.zeros_like(range_m, dtype=bool)

    elevation_rad = np.deg2rad(abs(elevation_deg))

    if elevation_rad == 0:
        return np.zeros_like(range_m, dtype=bool)

    ground_range_m = lidar_height_m / np.sin(elevation_rad)

    return range_m >= ground_range_m

def build_valid_precheck_mask(
    *flags: np.ndarray,
) -> np.ndarray:
    """
    Build a valid-data mask from one or more Boolean quality flags.

    Parameters
    ----------
    *flags : np.ndarray
        Boolean arrays where True indicates a quality-control problem.

    Returns
    -------
    np.ndarray
        Boolean array where True indicates the range gate passed all supplied
        quality-control checks.
    """
    if len(flags) == 0:
        raise ValueError("At least one flag array must be provided.")

    combined_bad = np.zeros_like(np.asarray(flags[0], dtype=bool))

    for flag in flags:
        combined_bad |= np.asarray(flag, dtype=bool)

    return ~combined_bad

def summarize_profile_quality(
    range_m: np.ndarray,
    signal: np.ndarray,
    valid_mask: np.ndarray,
    hard_target_flag: np.ndarray | None = None,
    saturation_flag: np.ndarray | None = None,
) -> dict:
    """
    Summarize quality-control results for one lidar profile.

    Parameters
    ----------
    range_m : np.ndarray
        Range from lidar, in meters.
    signal : np.ndarray
        Raw or processed lidar signal.
    valid_mask : np.ndarray
        Boolean array where True indicates valid range gates.
    hard_target_flag : np.ndarray or None
        Optional Boolean hard-target flag.
    saturation_flag : np.ndarray or None
        Optional Boolean saturation flag.

    Returns
    -------
    dict
        Profile-level quality summary.
    """
    range_m = np.asarray(range_m, dtype=float)
    signal = np.asarray(signal, dtype=float)
    valid_mask = np.asarray(valid_mask, dtype=bool)

    if len(range_m) == 0:
        raise ValueError("Cannot summarize an empty profile.")

    max_idx = int(np.nanargmax(signal))

    summary = {
        "n_bins": int(len(range_m)),
        "n_valid_bins": int(np.sum(valid_mask)),
        "fraction_valid": float(np.mean(valid_mask)),
        "max_signal": float(np.nanmax(signal)),
        "range_at_max_signal_m": float(range_m[max_idx]),
    }

    if hard_target_flag is not None:
        hard_target_flag = np.asarray(hard_target_flag, dtype=bool)
        summary["n_hard_target_bins"] = int(np.sum(hard_target_flag))

        if np.any(hard_target_flag):
            summary["first_hard_target_range_m"] = float(
                range_m[np.where(hard_target_flag)[0][0]]
            )
        else:
            summary["first_hard_target_range_m"] = np.nan

    if saturation_flag is not None:
        saturation_flag = np.asarray(saturation_flag, dtype=bool)
        summary["n_saturated_bins"] = int(np.sum(saturation_flag))

    return summary

