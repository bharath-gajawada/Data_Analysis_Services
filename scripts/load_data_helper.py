"""Helper to load data for all Report 2 plot scripts."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

def load_and_setup():
    """Import 01_load_data from report1, load data, return (df, OUT) with report2 output path."""
    from importlib.machinery import SourceFileLoader
    # Reuse report1's data loader
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    report2_dir = os.path.dirname(scripts_dir)
    project_root = os.path.dirname(report2_dir)
    report1_loader = os.path.join(project_root, 'report1_output', 'scripts', '01_load_data.py')
    mod = SourceFileLoader('load_data', report1_loader).load_module()
    df = mod.load_data()
    OUT = os.path.join(report2_dir, 'plots')
    os.makedirs(OUT, exist_ok=True)
    return df, OUT, mod
