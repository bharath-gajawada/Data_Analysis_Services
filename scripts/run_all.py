"""
Master runner — Execute all Report 2 analysis scripts in order.
"""
import subprocess
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
scripts = [
    '01_normality_checks.py',
    '02_ancova.py',
    '03_regression.py',
    '04_mixed_anova.py',
    '05_sdy_analysis.py',
    '06_power_analysis.py',
    '07_extended_correlation.py',
]

failed = []
for s in scripts:
    path = os.path.join(SCRIPTS_DIR, s)
    print(f"\n{'='*70}")
    print(f"Running {s}...")
    print('='*70)
    result = subprocess.run([sys.executable, path], capture_output=False,
                            cwd=os.path.dirname(SCRIPTS_DIR))
    if result.returncode != 0:
        failed.append(s)
        print(f"  FAILED: {s} (return code {result.returncode})")
    else:
        print(f"  OK: {s}")

print(f"\n{'='*70}")
if failed:
    print(f"COMPLETED with {len(failed)} failures: {', '.join(failed)}")
else:
    print(f"ALL {len(scripts)} SCRIPTS COMPLETED SUCCESSFULLY")
    print(f"Plots saved to: {os.path.join(os.path.dirname(SCRIPTS_DIR), 'plots')}")
print('='*70)
