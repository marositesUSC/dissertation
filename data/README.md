# Data Directory

This directory contains project data organized by processing stage.

## Structure

- `00_raw/`: Original downloaded, collected, or received data. These files should not be manually edited.
- `01_interim/`: Intermediate data created during cleaning, quality control, reprojection, filtering, or formatting.
- `02_processed/`: Analysis-ready datasets produced from raw or interim data.
- `03_model_inputs/`: Final datasets formatted specifically for model training, simulation, or statistical analysis.
- `04_models/`: Model artifacts, trained models, configuration files, or model outputs.
- `09_final/`: Final curated datasets used for publication, reporting, or delivery.
- `99_external/`: External reference datasets used by the project, such as boundaries, land cover, elevation, or station metadata.

## Version Control

Large data files are generally not tracked by Git. This repository may include small sample data or placeholder files only.

## Reproducibility

Processed and final datasets should be reproducible from scripts in `scripts/` or code in `src/`. When adding a dataset, document in the [datasets document](datasets.md) and for bigger datasets, add a README or any other documentation in that dataset's folder. Include the following when you can:

- Source
- Download/access date
- Processing steps
- Responsible script or notebook
- Coordinate reference system, if applicable
- Units and key variables


