"""Helper to load data for all plot scripts."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

def load_and_setup():
    """Import load_data, load data, return (df, OUT)."""
    import load_data as mod
    df = mod.load_data()
    return df, mod.OUT
