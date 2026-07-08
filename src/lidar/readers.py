"""
readers.py

File-reading utilities for USC and UIUC lidar data.

This module contains instrument-specific readers that parse raw lidar files
and return standardized metadata dictionaries and profile dataframes.

Author: Benjamin Marosites
Created: June 2026
Project: Dissertation research — spatial-temporal lidar alignment
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_uiuc_file(file_path: str | Path) -> tuple[dict, pd.DataFrame]:
    """
    Read one UIUC aerosol lidar file.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to one UIUC raw lidar file.

    Returns
    -------
    metadata : dict
        Standardized scan-level metadata.
    profile : pandas.DataFrame
        Range-gate-level lidar signal data.
    """
    raise NotImplementedError("UIUC reader is not implemented yet.")


def read_usc_file(file_path: str | Path) -> tuple[dict, pd.DataFrame]:
    """
    Read one USC aerosol lidar file.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to one USC raw lidar file.

    Returns
    -------
    metadata : dict
        Standardized scan-level metadata.
    profile : pandas.DataFrame
        Range-gate-level lidar signal data.
    """
    raise NotImplementedError("USC reader is not implemented yet.")


def read_lidar_file(
    file_path: str | Path,
    source: str,
) -> tuple[dict, pd.DataFrame]:
    """
    Read one lidar file using the appropriate source-specific reader.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to one raw lidar file.
    source : str
        Lidar source. Expected values are 'UIUC' or 'USC'.

    Returns
    -------
    metadata : dict
        Standardized scan-level metadata.
    profile : pandas.DataFrame
        Range-gate-level lidar signal data.
    """
    source = source.upper()

    if source == "UIUC":
        return read_uiuc_file(file_path)

    if source == "USC":
        return read_usc_file(file_path)

    raise ValueError(f"Unsupported lidar source: {source}")