"""
simple_parser.py

File-reading utilities for USC and UIUC lidar data.

This module reads one Raymetrics-style lidar file, separates the metadata/header
section from the profile data section, extracts standardized metadata, decodes
dataset descriptor lines, and returns a metadata dictionary and profile
dataframe.

Author: Benjamin Marosites
Created: June 2026
Project: Dissertation research — spatial-temporal lidar alignment
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

def read_lidar_file(
    file_path: str | Path,
    source: str,
    end_meta: int,
) -> tuple[dict, pd.DataFrame]:
    """
    Read one lidar file and return standardized metadata and profile data.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Path to one raw lidar file.
    source : str
        Lidar source. Expected values are 'UIUC' or 'USC'.
    end_meta : int
        Index where the metadata/header section ends and raw profile data begins.
        For example, if metadata occupies lines 0 through 6, use end_meta=7.

    Returns
    -------
    metadata : dict
        Standardized scan-level metadata.
    profile : pandas.DataFrame
        Range-gate-level profile data. This first version returns an empty
        standardized profile dataframe until raw signal decoding is added.
    """
    file_path = Path(file_path)
    source = source.strip().upper()

    with open(file_path, 'r') as file:
        content = file.readlines()
    
    header_lines = [line.strip() for line in content[:end_meta]]

    if len(header_lines) < 4:
        raise ValueError("Expected at least 4 header lines.")

    measurement_name = header_lines[0]
    header2_metadata = parse_header_line_2(header_lines[1])
    dataset_descriptors = decode_dataset_descriptors(header_lines)

    metadata = {
        "source": source,
        "file_name": file_path.name,
        "file_path": str(file_path),
        "measurement_name": measurement_name,
        "header_lines": header_lines,
        "dataset_descriptors": dataset_descriptors,
    }

    metadata.update(header2_metadata)
    if not dataset_descriptors:
        raise ValueError(f"No dataset descriptors found in file: {file_path}")

    n_bins = dataset_descriptors[0]["n_bins"]
    bin_width = dataset_descriptors[0]["bin_width_m"]

    metadata["n_bins"] = n_bins
    metadata["bin_width_m"] = bin_width


    profile_df = pd.read_csv(
        file_path,
        sep=',|\t', # sep=r",|\t|\s+",  
        skiprows=end_meta,
        engine="python",
    )
    profile_df.insert(0, 'range_bin', profile_df.index)
    profile_df.insert(1, 'range_m', bin_width/2 + profile_df["range_bin"] * bin_width)    ## Using center of the range gate:
    
    return metadata, profile_df


def parse_header_line_2(header2: str) -> dict:
    """
    Parse the second Raymetrics header line.

    Expected fields
    ---------------
    campaign start_date start_time end_date end_time height longitude latitude
    zenith azimuth ground_temperature ground_pressure

    Returns
    -------
    dict
        Parsed metadata fields.
    """
    pattern = (
        r"^(?P<campaign>\S+)\s+"
        r"(?P<start_date>\d{2}/\d{2}/\d{4})\s+"
        r"(?P<start_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<end_date>\d{2}/\d{2}/\d{4})\s+"
        r"(?P<end_time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<height_m_asl>[-+]?\d+(?:\.\d+)?)\s+"
        r"(?P<longitude_deg>[-+]?\d+(?:\.\d+)?)\s+"
        r"(?P<latitude_deg>[-+]?\d+(?:\.\d+)?)\s+"
        r"(?P<zenith_deg>[-+]?\d+(?:\.\d+)?)\s+"
        r"(?P<azimuth_deg>[-+]?\d+(?:\.\d+)?)\s+"
        r"(?P<ground_temperature_c>[-+]?\d+(?:\.\d+)?)\s+"
        r"(?P<ground_pressure_hpa>[-+]?\d+(?:\.\d+)?)"
        r"$"
    )

    match = re.match(pattern, header2.strip())

    if match is None:
        raise ValueError(f"Could not parse Raymetrics header line 2: {header2}")

    parts = match.groupdict()

    return {
        "campaign": parts["campaign"],
        "scan_start_time": f"{parts['start_date']} {parts['start_time']}",
        "scan_end_time": f"{parts['end_date']} {parts['end_time']}",
        "height_m_asl": float(parts["height_m_asl"]),
        "longitude_deg": float(parts["longitude_deg"]),
        "latitude_deg": float(parts["latitude_deg"]),
        "raw_zenith_deg": float(parts["zenith_deg"]), #* -1,    # Sign flip follows current project convention; verify against scan geometry.
        "raw_azimuth_deg": float(parts["azimuth_deg"]),
        "ground_temperature_c": float(parts["ground_temperature_c"]),
        "ground_pressure_hpa": float(parts["ground_pressure_hpa"]),
    }


def decode_dataset_descriptors(
    header_lines: list[str],
    first_descriptor_index: int = 4,
) -> list[dict]:
    """
    Decode dataset descriptor lines from the metadata/header section.

    Parameters
    ----------
    header_lines : list[str]
        Metadata/header lines.
    first_descriptor_index : int
        Index of the first dataset descriptor line. For Raymetrics files, this
        is commonly 4, after the first four header lines.

    Returns
    -------
    list[dict]
        One dictionary per dataset descriptor line.
    """
    descriptor_lines = header_lines[first_descriptor_index:]

    descriptors = []

    for dataset_index, line in enumerate(descriptor_lines):
        if not line.strip():
            continue

        parts = line.split()

        # A valid dataset descriptor should have at least enough fields to
        # include dataset presence, signal type, laser source, n_bins, and bin width.
        if len(parts) < 7:
            continue

        descriptor = {
            "dataset_index": dataset_index,
            "raw_descriptor": line,
            "dataset_present": int(parts[0]),
            "signal_mode": int(parts[1]),
            "laser_source": int(parts[2]),
            "n_bins": int(parts[3]),
            "pmt_high_voltage": float(parts[5]),
            "bin_width_m": float(parts[6]),
        }

        # These fields may be present depending on file format/version.
        if len(parts) > 7:
            descriptor["wavelength_nm"] = parts[7]

        if len(parts) > 14:
            descriptor["dataset_label"] = parts[14]

        if len(parts) > 15:
            descriptor["recorder"] = parts[15]

        descriptors.append(descriptor)

    return descriptors