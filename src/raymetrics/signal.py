"""
signal.py

Signal-processing utilities for lidar analog and photon-counting data.

This module contains functions for background correction, range correction,
smoothing, and relative-backscatter preparation.

Author: Benjamin Marosites
Created: June 2026
Project: Dissertation research — spatial-temporal lidar alignment
"""

from __future__ import annotations

import numpy as np
import pandas as pd

def estimate_background(
    signal: np.ndarray,
    range_m: np.ndarray,
    background_min_m: float,
    background_max_m: float,
    method: str = "median",
) -> float:
    """
    Estimate background signal from a far-range interval.

    Parameters
    ----------
    signal : np.ndarray
        Raw lidar signal.
    range_m : np.ndarray
        Range from lidar, in meters.
    background_min_m : float
        Lower bound of background range interval.
    background_max_m : float
        Upper bound of background range interval.
    method : str
        Background estimator. Options: 'median' or 'mean'.

    Returns
    -------
    float
        Estimated background signal.
    """
    mask = (range_m >= background_min_m) & (range_m <= background_max_m)

    if not np.any(mask):
        raise ValueError("No range bins found in background interval.")

    if method == "median":
        return float(np.nanmedian(signal[mask]))

    if method == "mean":
        return float(np.nanmean(signal[mask]))

    raise ValueError(f"Unsupported background method: {method}")

def range_correct_signal(
    signal: np.ndarray,
    range_m: np.ndarray,
    background: float | None = None,
) -> np.ndarray:
    """
    Apply background subtraction and range-squared correction.

    Parameters
    ----------
    signal : np.ndarray
        Raw lidar signal.
    range_m : np.ndarray
        Range from lidar, in meters.
    background : float or None
        Background value to subtract before range correction.

    Returns
    -------
    np.ndarray
        Range-corrected signal.
    """
    corrected = signal.astype(float).copy()

    if background is not None:
        corrected = corrected - background

    return corrected * range_m**2

def smooth_signal(
    signal: np.ndarray,
    window_bins: int = 5,
    method: str = "rolling_median",
) -> np.ndarray:
    """
    Smooth a one-dimensional lidar signal.

    Parameters
    ----------
    signal : np.ndarray
        Input signal.
    window_bins : int
        Rolling window size in range bins.
    method : str
        Smoothing method. Options: 'rolling_median' or 'rolling_mean'.

    Returns
    -------
    np.ndarray
        Smoothed signal.
    """
    series = pd.Series(signal)

    if method == "rolling_median":
        return series.rolling(
            window=window_bins,
            center=True,
            min_periods=1,
        ).median().to_numpy()

    if method == "rolling_mean":
        return series.rolling(
            window=window_bins,
            center=True,
            min_periods=1,
        ).mean().to_numpy()

    raise ValueError(f"Unsupported smoothing method: {method}")

def build_quality_mask(
    range_m: np.ndarray,
    signal: np.ndarray,
    valid_min_range_m: float,
    valid_max_range_m: float,
) -> np.ndarray:
    """
    Build a basic quality mask for lidar range-gate data.

    Returns True for valid data and False for invalid data.
    """
    return (
        np.isfinite(signal)
        & np.isfinite(range_m)
        & (range_m >= valid_min_range_m)
        & (range_m <= valid_max_range_m)
    )

def process_backscatter_profile(
    df: pd.DataFrame,
    signal_col: str,
    range_col: str = "range_m",
    background_min_m: float = 9000,
    background_max_m: float = 12000,
    valid_min_range_m: float = 30,
    valid_max_range_m: float = 6000,
    smoothing_window_bins: int = 5,
) -> pd.DataFrame:
    """
    Process one lidar backscatter profile.

    Adds background-corrected, range-corrected, smoothed, and QC columns.
    """
    out = df.copy()

    signal = out[signal_col].to_numpy(dtype=float)
    range_m = out[range_col].to_numpy(dtype=float)

    background = estimate_background(
        signal=signal,
        range_m=range_m,
        background_min_m=background_min_m,
        background_max_m=background_max_m,
    )

    out[f"{signal_col}_background"] = background
    out[f"{signal_col}_background_corrected"] = signal - background

    out[f"{signal_col}_range_corrected"] = range_correct_signal(
        signal=signal,
        range_m=range_m,
        background=background,
    )

    out[f"{signal_col}_range_corrected_smoothed"] = smooth_signal(
        out[f"{signal_col}_range_corrected"].to_numpy(),
        window_bins=smoothing_window_bins,
        method="rolling_median",
    )

    out["valid_signal"] = build_quality_mask(
        range_m=range_m,
        signal=out[f"{signal_col}_range_corrected_smoothed"].to_numpy(),
        valid_min_range_m=valid_min_range_m,
        valid_max_range_m=valid_max_range_m,
    )

    return out