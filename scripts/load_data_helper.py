"""Helper to load data for all plot scripts."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

def load_and_setup():
    """Import 01_load_data, load data, return (df, OUT)."""
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader('load_data', os.path.join(os.path.dirname(__file__), '01_load_data.py'))
    mod = loader.load_module()
    df = mod.load_data()
    return df, mod.OUT
