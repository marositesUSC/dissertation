# Source Code Directory

This directory contains reusable project code.

## `config.py`

The `config.py` module provides helper functions for loading YAML configuration files from the project-level `config/` directory.

This project template assumes the following structure:

```text
project-root/
├── config/
│   ├── paths.yml
│   ├── study_area.yml
│   └── variables.yml
├── scripts/
├── notebooks/
└── src/
    └── config.py
```

### Importing config.py
Because this template keeps config.py directly inside src/, scripts and notebooks may need to add the src/ directory to the Python path before importing.

### From a script in scripts/
```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from config import load_config
```

### From a notebook in the project
```python
import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parent / "src"))

from config import load_config
```

### Load a Config File
Then use `load_config()` to load files from the `config/` directory.
```python
paths = load_config("paths.yml")
study_area = load_config("study_area.yml")
variables = load_config("variables.yml")
```

### Example
```python
from config import load_config

study_area = load_config("study_area.yml")

start_date = study_area["temporal"]["start_date"]
end_date = study_area["temporal"]["end_date"]
crs = study_area["spatial"]["crs"]

print(start_date, end_date, crs)```