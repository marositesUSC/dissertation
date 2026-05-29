# Copy this as a template
For new projects go to 
```text
GitHub -> https://github.com/marositesUSC/research-project-template -> Use this template -> Create a new repository
```

Then clone the new repo to the right local folder on your machine. 

```powershell
cd C:\Users\ben\Projects\research ### your directory
git clone https://github.com/YOUR-USERNAME/new-project-name.git ### your .git dir
```
*delete text above this from your clone.*

---- 
# Project Title

Briefly describe the purpose of this project. Include the research question, class assignment, analysis goal, or decision this project supports.

## Project Overview

This repository contains code, documentation, data organization, GIS materials, and outputs for a reproducible research or analysis project.

**Project:** [Project name]  
**Author(s):** [Your name(s)]  
**Affiliation / Course / Organization:** [Affiliation, course, lab, or organization]  
**Start date:** [YYYY-MM-DD]  
**Status:** [Active / In progress / Complete / Archived]

## Objectives

The main objectives of this project are:

1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

## Repository Structure

```text
.
├── README.md
├── PROJECT_LOG.md
├── environment.yml
├── config/
├── data/
├── docs/
├── gis/
├── notebooks/
├── outputs/
├── scripts/
├── src/
└── tests/
```

## Directory Guide

| Directory / File | Purpose |
|---|---|
| [`README.md`](README.md) | Project overview, setup instructions, and repository guide. |
| [`PROJECT_LOG.md`](PROJECT_LOG.md) | Human-readable project log for major decisions, progress, outputs, and notes. |
| [`environment.yml`](environment.yml) | Conda/Mamba environment definition. |
| [`config/`](config/README.md) | Project configuration files such as paths, study area settings, plotting settings, and variable metadata. |
| [`data/`](data/README.md) | Project data organized by processing stage. Large data files are usually not tracked by Git. |
| [`docs/`](docs/README.md) | Project documentation, methods notes, references, and supporting written materials. |
| [`gis/`](gis/README.md) | GIS project files, geodatabases, layer files, and map-related materials. |
| [`notebooks/`](notebooks/) | Jupyter notebooks for exploration, analysis, visualization, and workflow documentation. |
| [`outputs/`](outputs/) | Generated figures, maps, tables, animations, reports, and other products. |
| [`scripts/`](scripts/) | Standalone scripts for processing, analysis, modeling, and output generation. |
| [`src/`](src/README.md) | Reusable project code and helper functions. |
| [`tests/`](tests/) | Tests for reusable code in `src/`. |

## Data Organization

Data are organized by processing stage:

```text
data/
├── README.md
├── datasets.md
├── 00_raw/
├── 01_interim/
├── 02_processed/
├── 03_model_inputs/
├── 04_models/
├── 09_final/
└── 99_external/
```

| Folder | Purpose |
|---|---|
| [`data/00_raw/`](data/00_raw/) | Original downloaded, collected, or received data. Raw data should not be manually edited. |
| [`data/01_interim/`](data/01_interim/) | Intermediate data created during cleaning, quality control, reprojection, filtering, or formatting. |
| [`data/02_processed/`](data/02_processed/) | Analysis-ready datasets. |
| [`data/03_model_inputs/`](data/03_model_inputs/) | Final datasets formatted specifically for modeling, simulation, or statistical analysis. |
| [`data/04_models/`](data/04_models/) | Model artifacts, trained models, model outputs, or configuration files. |
| [`data/09_final/`](data/09_final/) | Final curated datasets used for publication, reporting, delivery, or archiving. |
| [`data/99_external/`](data/99_external/) | External reference datasets such as boundaries, land cover, elevation, station metadata, or other supporting sources. |

Dataset sources, access dates, processing notes, coordinate reference systems, units, and responsible scripts should be documented in [data/datasets.md](data/datasets.md) and any additional data can be stored in that specific directory. 

## Environment Setup

This project uses Conda/Mamba for environment management.

Create the environment:

```bash
mamba env create -f environment.yml
```

Activate the environment:

```bash
conda activate project-env
```

Update the environment after changes to `environment.yml`:

```bash
mamba env update -f environment.yml --prune
```

Register the environment as a Jupyter kernel:

```bash
python -m ipykernel install --user --name project-env --display-name "Python (project-env)"
```

> Replace `project-env` with the actual environment name used for this project.

## Configuration Files

Project settings are stored in [`config/`](config/) so that important choices are not hardcoded across scripts and notebooks. You can hardcode into note books and scripts, but to make it easier try to use the configuration controls here.

Common configuration files include:

| File | Purpose |
|---|---|
| [`config/paths.yml`](config/paths.yml) | Common project directories and reusable paths. |
| [`config/study_area.yml`](config/study_area.yml) | Spatial extent, temporal coverage, CRS, and study-area metadata. |
| [`config/variables.yml`](config/variables.yml) | Standard variable names, raw/source variable mappings, units, labels, and notes. |
| [`config/plotting.yml`](config/plotting.yml) | Figure sizes, map settings, output formats, labels, and visualization defaults. |

Reusable helpers for reading configuration files live in: [`src/config.py`](src/config.py)

See [`src/README.md`](src/README.md) for import examples and usage notes.

## Reproducibility Workflow

The intended workflow is:

1. Place original source data in [`data/00_raw/`](data/00_raw/) or [`data/99_external/`](data/99_external/).
2. Document each dataset in [data/datasets.md](data/datasets.md).
3. Use scripts or notebooks to clean and transform data.
4. Save intermediate products to [`data/01_interim/`](data/01_interim/).
5. Save analysis-ready products to [`data/02_processed/`](data/02_processed/).
6. Save model-ready inputs to [`data/03_model_inputs/`](data/03_model_inputs/).
7. Save model artifacts or model outputs to [`data/04_models/`](data/04_models/).
8. Save final curated products to [`data/09_final/`](data/09_final/).
9. Save generated figures, maps, tables, animations, and reports to [`outputs/`](outputs/).
10. Record major project decisions, milestones, and important outputs in [`PROJECT_LOG.md`](PROJECT_LOG.md).

Whenever possible, processed and final outputs should be reproducible from the raw/external data and the code in this repository.

## Git and Version Control

This repository is intended to track:

- Code
- Documentation
- Configuration files
- Lightweight project files
- Small examples or placeholder files

This repository generally should not track:

- Large raw datasets
- Large processed datasets
- File geodatabases
- NetCDF, GRIB, HDF, GeoTIFF, LAS/LAZ, or other large scientific/geospatial files
- Temporary files
- Local environment folders
- Python cache files
- Jupyter checkpoint files
- ArcGIS lock files

See [`.gitignore`](.gitignore) for project-specific rules.

## Working with Notebooks

Jupyter notebooks should be stored in [`notebooks/`](notebooks/).

Use notebooks for:

- Exploratory analysis
- Draft workflows
- Visualization experiments
- Narrative analysis notes
- Prototyping code before moving reusable functions into [`src/`](src/)

Reusable code should eventually be moved from notebooks into [`src/`](src/) or [`scripts/`](scripts/) when it becomes stable.

## Working with Scripts and Source Code

Use [`scripts/`](scripts/) for runnable project steps, such as:

- Downloading data
- Cleaning data
- Processing GIS layers
- Running models
- Generating figures or tables

Use [`src/`](src/) for reusable code, such as:

- Helper functions
- Configuration loaders
- Data-processing utilities
- Plotting functions
- GIS utilities
- Model functions

Tests for reusable code should live in[ `tests/`](tests/).

Run tests from the project root with:

```bash
pytest
```

## GIS Notes

GIS-related files should be stored in [`gis/`](/gis/).

Use this folder for:

- ArcGIS Pro projects
- Geodatabases
- Layer files
- Symbology
- Map exports
- Study-area boundaries
- GIS processing support files

Avoid working with active ArcGIS projects inside cloud-synced folders when possible, especially when using file geodatabases or `.aprx` files.

## Outputs

Generated outputs should be stored in [`outputs/`](outputs/).

```text
outputs/
├── animations/
├── figures/
├── maps/
├── reports/
└── tables/
```

Outputs are often ignored by Git unless they are final, lightweight, and intentionally included.

## Project Log

Use [`PROJECT_LOG.md`](PROJECT_LOG.md) to record major project activity, decisions, issues, and outputs.

Examples of useful log entries include:

- Dataset added or updated
- Processing method changed
- Model configuration changed
- Important figure or table created
- Analysis decision made
- Problem discovered and resolved
- Meeting or advisor feedback incorporated

Routine code changes should still be tracked with Git commits. The project log is for human-readable context.

## Documentation

Use [`docs/`](docs/) for supporting project materials:

```text
docs/
├── methods/
├── notes/
└── references/
```

This folder can include methods notes, literature notes, meeting notes, reference material, diagrams, and other supporting documentation.

## License

No license has been selected for this project yet.

Before making this repository public, sharing it with collaborators, or publishing outputs from it, choose an appropriate license for the code, documentation, and data.

To create a license, open repo on GitHub:
1) Open the repository on GitHub.
2) Click Add file.
3) Click Create new file.
4) Name the file: `LICENSE`
5) GitHub should show a button or prompt to Choose a license template.
6) Pick a license, such as MIT License.
7) Review it.
8) Commit the file.

GitHub will automatically fill in the license text for common licenses.
Common options include:

- MIT License for reusable open-source code
- Apache License 2.0 for open-source code with explicit patent language
- CC BY 4.0 for documentation, educational materials, figures, or datasets that others may reuse with attribution
- Private/internal use only for work that should not be reused without permission

## Citation

If this project produces a report, paper, dataset, or software product, add citation information here.

```text
[Author]. ([Year]). [Project or dataset title]. [Repository or archive]. [DOI or URL if available].
```