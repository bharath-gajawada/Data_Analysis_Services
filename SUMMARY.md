# Analysis Cleanup Summary

## What was kept
- A sequential notebook entry point at [analysis_workflow.ipynb](analysis_workflow.ipynb) for the full analysis flow.
- Python modules for reusable preprocessing, plots, and statistics in [scripts/](scripts).
- Assumption-aware statistical helpers in [scripts/stats_helpers.py](scripts/stats_helpers.py).

## What was cleaned up
- Removed temporary reference artifacts and working noise files.
- Replaced broken `01_load_data.py` imports with direct imports from [scripts/load_data.py](scripts/load_data.py).
- Reduced hard-coded significance text in plots and added computed p-values and confidence intervals.
- Added normality checks, adaptive test selection, and FDR correction for repeated tests.

## Next steps
- Run the notebook top-to-bottom once the `data/` folder is available in the workspace.
- Validate whether the footer-stat optimization in [scripts/load_data.py](scripts/load_data.py) matches the exact raw file layout.
- If needed, extend the same assumption-aware pattern to any remaining inferential comparisons not yet covered.
