"""
geometry.py

Coordinate transformation utilities for spatial-temporal alignment of
independent lidar scans.

This module contains functions for converting lidar range-gate observations
from instrument-relative coordinates into a shared Cartesian coordinate system.

Author: Benjamin Marosites
Created: June 2026
Project: Dissertation research — spatial-temporal lidar alignment
"""

from __future__ import annotations

import numpy as np
import pandas as pd

def lidar_to_xyz(
    range_m: np.ndarray,
    azimuth_deg: np.ndarray,
    elevation_deg: np.ndarray,
    origin_x: float,
    origin_y: float,
    origin_z: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert lidar range, azimuth, and elevation angle to Cartesian coordinates.

    Parameters
    ----------
    range_m : array-like
        Distance from the lidar to each range gate, in meters.
    azimuth_deg : array-like
        Azimuth angle in degrees. Assumed clockwise from north.
    elevation_deg : array-like
        Elevation angle in degrees above horizontal.
    origin_x : float
        Lidar x-coordinate in the shared coordinate system.
    origin_y : float
        Lidar y-coordinate in the shared coordinate system.
    origin_z : float
        Lidar z-coordinate in the shared coordinate system.

    Returns
    -------
    x, y, z : tuple of array-like
        Cartesian coordinates for each lidar range gate.
    """
    azimuth_rad = np.deg2rad(azimuth_deg)
    elevation_rad = np.deg2rad(elevation_deg)

    horizontal_range_m = range_m * np.cos(elevation_rad)

    x = origin_x + horizontal_range_m * np.sin(azimuth_rad)
    y = origin_y + horizontal_range_m * np.cos(azimuth_rad)
    z = origin_z + range_m * np.sin(elevation_rad)

    return x, y, z