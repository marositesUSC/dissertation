"""
files.py

File discovery and selection utilities for lidar data processing.

This module contains functions for finding raw lidar files, parsing timestamps
from lidar file names, and selecting files within a requested time range.

Author: Benjamin Marosites
Created: June 2026
Project: Dissertation research — spatial-temporal lidar alignment
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re

import pandas as pd


def list_lidar_files(
    root_dir: str | Path,
    pattern: str = "*",
    recursive: bool = True,
) -> list[Path]:
    """
    List lidar files in a directory.

    Parameters
    ----------
    root_dir : str or pathlib.Path
        Directory containing lidar files.
    pattern : str
        File search pattern. Examples include '*', 'R*', 'S*', '*.txt'.
    recursive : bool
        If True, search through subdirectories.

    Returns
    -------
    list[pathlib.Path]
        Sorted list of matching file paths.
    """
    root_dir = Path(root_dir)

    if not root_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {root_dir}")

    if recursive:
        files = list(root_dir.rglob(pattern))
    else:
        files = list(root_dir.glob(pattern))

    files = [file for file in files if file.is_file()]

    return sorted(files)


def parse_raymetrics_filename_time(
    file_path: str | Path,
    prefix: str,
) -> datetime:
    """
    Parse datetime from a Raymetrics-style lidar file name.

    Expected examples
    -----------------
    R1892323.091335
    S1892323.091335
    R18A1523.091335
    S18B0223.091335
    R1892323.091335.TXT

    Pattern
    -------
    <prefix>YYMDDHH.MMSSss

    Interpretation
    --------------
    prefix : Instrument/file source prefix, such as R or S
    YY     : two-digit year, e.g. 18 = 2018
    M      : month, where 9 = September, A = October, B = November
    DD     : day of month
    HH     : hour
    MM     : minute
    SSss   : seconds with hundredths, e.g. 1335 = 13.35 seconds

    Parameters
    ----------
    file_path : str or pathlib.Path
        Lidar file path or file name.
    prefix : str
        Expected first character of the file name. UIUC uses 'R';
        USC uses 'S'.

    Returns
    -------
    datetime.datetime
        Parsed file timestamp.
    """
    name = Path(file_path).name.strip().upper()
    prefix = prefix.strip().upper()

    if len(prefix) != 1:
        raise ValueError(f"Expected a single-character prefix, got: {prefix!r}")

    pattern = (
        rf"^{re.escape(prefix)}"
        r"(?P<year>\d{2})"
        r"(?P<month>[0-9AB])"
        r"(?P<day>\d{2})"
        r"(?P<hour>\d{2})"
        r"\."
        r"(?P<minute>\d{2})"
        r"(?P<sec_hundredths>\d{4})"
        r"(?P<file_type>\.[A-Z0-9]+)?"
        r"$"
    )

    match = re.match(pattern, name)

    if match is None:
        raise ValueError(
            f"Could not parse Raymetrics filename timestamp with prefix "
            f"{prefix!r}: {name}"
        )

    year = 2000 + int(match.group("year"))

    month_token = match.group("month")
    if month_token == "A":
        month = 10
    elif month_token == "B":
        month = 11
    else:
        month = int(month_token)

    day = int(match.group("day"))
    hour = int(match.group("hour"))
    minute = int(match.group("minute"))

    sec_hundredths = int(match.group("sec_hundredths"))
    second = sec_hundredths // 100
    microsecond = (sec_hundredths % 100) * 10_000

    return datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
    )


def parse_uiuc_filename_time(file_path: str | Path) -> datetime:
    """
    Parse datetime from a UIUC lidar file name.

    UIUC files use the Raymetrics-style prefix 'R'.

    Parameters
    ----------
    file_path : str or pathlib.Path
        UIUC lidar file path or file name.

    Returns
    -------
    datetime.datetime
        Parsed file timestamp.
    """
    return parse_raymetrics_filename_time(file_path, prefix="R")


def parse_usc_filename_time(file_path: str | Path) -> datetime:
    """
    Parse datetime from a USC lidar file name.

    USC files use the Raymetrics-style prefix 'S'.

    Parameters
    ----------
    file_path : str or pathlib.Path
        USC lidar file path or file name.

    Returns
    -------
    datetime.datetime
        Parsed file timestamp.
    """
    return parse_raymetrics_filename_time(file_path, prefix="S")


def parse_lidar_filename_time(
    file_path: str | Path,
    source: str,
) -> datetime:
    """
    Parse datetime from a lidar file name using source-specific logic.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Lidar file path or file name.
    source : str
        Lidar source. Expected values are 'UIUC' or 'USC'.

    Returns
    -------
    datetime.datetime
        Parsed file timestamp.
    """
    source = source.strip().upper()

    if source == "UIUC":
        return parse_uiuc_filename_time(file_path)

    if source == "USC":
        return parse_usc_filename_time(file_path)

    raise ValueError(f"Unsupported lidar source: {source}")


def select_files_by_time(
    file_paths: list[str | Path],
    source: str,
    start_time: str | datetime | pd.Timestamp,
    end_time: str | datetime | pd.Timestamp,
    include_start: bool = True,
    include_end: bool = True,
) -> pd.DataFrame:
    """
    Select lidar files whose filename timestamps fall within a time range.

    Parameters
    ----------
    file_paths : list of str or pathlib.Path
        Candidate lidar files.
    source : str
        Lidar source. Expected values are 'UIUC' or 'USC'.
    start_time : str, datetime, or pandas.Timestamp
        Start of requested time range.
    end_time : str, datetime, or pandas.Timestamp
        End of requested time range.
    include_start : bool
        If True, include files exactly at start_time.
    include_end : bool
        If True, include files exactly at end_time.

    Returns
    -------
    pandas.DataFrame
        Table with candidate files, parsed times, parse errors, and
        a Boolean selection flag.

        Columns:
        - file_path
        - file_name
        - file_time
        - parse_error
        - selected
    """
    start_time = pd.Timestamp(start_time)
    end_time = pd.Timestamp(end_time)

    if end_time < start_time:
        raise ValueError("end_time must be greater than or equal to start_time.")

    records = []

    for file_path in file_paths:
        file_path = Path(file_path)

        try:
            file_time = parse_lidar_filename_time(file_path, source)
        except Exception as exc:
            records.append(
                {
                    "file_path": file_path,
                    "file_name": file_path.name,
                    "file_time": pd.NaT,
                    "parse_error": str(exc),
                    "selected": False,
                }
            )
            continue

        file_time = pd.Timestamp(file_time)

        after_start = file_time >= start_time if include_start else file_time > start_time
        before_end = file_time <= end_time if include_end else file_time < end_time
        selected = bool(after_start and before_end)

        records.append(
            {
                "file_path": file_path,
                "file_name": file_path.name,
                "file_time": file_time,
                "parse_error": None,
                "selected": selected,
            }
        )

    df = pd.DataFrame.from_records(records)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "file_path",
                "file_name",
                "file_time",
                "parse_error",
                "selected",
            ]
        )

    return df.sort_values("file_time", na_position="last").reset_index(drop=True)


def find_files_by_time(
    root_dir: str | Path,
    source: str,
    start_time: str | datetime | pd.Timestamp,
    end_time: str | datetime | pd.Timestamp,
    pattern: str | None = None,
    recursive: bool = True,
) -> pd.DataFrame:
    """
    Find lidar files in a directory whose filename timestamps fall within a time range.

    Parameters
    ----------
    root_dir : str or pathlib.Path
        Directory to search.
    source : str
        Lidar source. Expected values are 'UIUC' or 'USC'.
    start_time : str, datetime, or pandas.Timestamp
        Start of requested time range.
    end_time : str, datetime, or pandas.Timestamp
        End of requested time range.
    pattern : str or None
        File search pattern. If None, a source-specific default is used:
        'R*' for UIUC and 'S*' for USC.
    recursive : bool
        If True, search through subdirectories.

    Returns
    -------
    pandas.DataFrame
        Table with candidate files, parsed times, parse errors, and selection flag.
    """
    source_clean = source.strip().upper()

    if pattern is None:
        if source_clean == "UIUC":
            pattern = "R*"
        elif source_clean == "USC":
            pattern = "S*"
        else:
            raise ValueError(f"Unsupported lidar source: {source}")

    file_paths = list_lidar_files(
        root_dir=root_dir,
        pattern=pattern,
        recursive=recursive,
    )

    return select_files_by_time(
        file_paths=file_paths,
        source=source_clean,
        start_time=start_time,
        end_time=end_time,
    )


def get_selected_file_paths(files_table: pd.DataFrame) -> list[Path]:
    """
    Extract selected file paths from a file-selection table.

    Parameters
    ----------
    files_table : pandas.DataFrame
        Output from select_files_by_time() or find_files_by_time().

    Returns
    -------
    list[pathlib.Path]
        File paths where selected is True.
    """
    required_columns = {"file_path", "selected"}

    missing_columns = required_columns.difference(files_table.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    selected = files_table.loc[files_table["selected"], "file_path"]

    return [Path(path) for path in selected]