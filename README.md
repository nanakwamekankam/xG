# xG Model Project

## Setup

Create the conda environment:

```bashgit add README.md
conda env create -f environment.yml
```

Activate it:
``` bash
conda activate xg_env
```

To use tabpfn:

1. Open https://ux.priorlabs.ai in a browser and log in (or register)
2. Accept the license on the Licenses tab
3. Copy your API Key from https://ux.priorlabs.ai/account
4. Set the environment variable: export TABPFN_TOKEN="<your-api-key>"
 or in Python (before calling .fit()): import os; os.environ["TABPFN_TOKEN"] = "<your-api-key>"
