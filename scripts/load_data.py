"""
Shared data loading, preprocessing, and clinical grouping.
All other scripts import from this module.
Run this first, or import it.
"""

import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ── Style ────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({'figure.dpi': 150, 'savefig.bbox': 'tight', 'font.family': 'sans-serif'})

# ── Paths ────────────────────────────────────────────────────────────────
# scripts/ is inside report1_output/, project root is two levels up
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPTS_DIR))  # project root
DATA_FILE = os.path.join(BASE_DIR, 'data', 'data.xlsx')
HT_DIR = os.path.join(BASE_DIR, 'data', 'headtracking-data')
OUT = os.path.join(SCRIPTS_DIR, '..', 'plots')
os.makedirs(OUT, exist_ok=True)

# ── Constants ────────────────────────────────────────────────────────────
VIDEOS = ['v1', 'v2', 'v3', 'v4', 'v5']
VIDEO_NAMES = {
    'v1': 'Abandoned\nBuildings',
    'v2': 'Evening\nBeach',
    'v3': 'Campus',
    'v4': 'The Nun\nHorror',
    'v5': 'Tahiti\nSurf',
}
VIDEO_SHORT = {'v1': 'Abandoned', 'v2': 'Beach', 'v3': 'Campus', 'v4': 'Horror', 'v5': 'Surf'}
PHQ_ORDER = ['Minimal (0-4)', 'Mild (5-9)', 'Moderate-Severe (≥10)']
COLORS_3 = ['#59a14f', '#edc948', '#e15759']


# ── Clinical grouping functions ──────────────────────────────────────────
def phq_group(x):
    if x <= 4: return 'Minimal (0-4)'
    elif x <= 9: return 'Mild (5-9)'
    else: return 'Moderate-Severe (≥10)'

def gad_group(x):
    if x <= 4: return 'Minimal (0-4)'
    elif x <= 9: return 'Mild (5-9)'
    else: return 'Moderate-Severe (≥10)'

def distress_group(row):
    p, g = row['score_phq'], row['score_gad']
    if p >= 10 and g >= 10: return 'Both Distress (BD)'
    elif 5 <= p <= 9 and 5 <= g <= 9: return 'Both Mild (BMD)'
    elif p >= 5 and g < 5: return 'Either Distress\n(Dep only)'
    elif g >= 5 and p < 5: return 'Either Distress\n(Anx only)'
    else: return 'None'


# ── Load & preprocess ────────────────────────────────────────────────────
def load_data():
    """Load survey + headtracking data, merge, apply groupings. Returns the merged DataFrame."""
    df = pd.read_excel(DATA_FILE)

    # Load headtracking
    ht_rows = []
    for _, row in df.iterrows():
        pid = row['participant']
        for v in VIDEOS:
            fname = row[v]
            if pd.isna(fname): continue
            fpath = os.path.join(HT_DIR, v, str(fname))
            if not os.path.exists(fpath): continue
            try:
                ht = pd.read_csv(fpath, on_bad_lines='skip')
                if 'RotationSpeedTotal' not in ht.columns: continue
                ht_rows.append({
                    'participant': pid, 'video': v,
                    'speed_total': ht['RotationSpeedTotal'].mean(),
                    'speed_x': ht['RotationSpeedX'].mean(),
                    'speed_y': ht['RotationSpeedY'].mean(),
                    'speed_z': ht['RotationSpeedZ'].mean(),
                    'sd_rot_x': ht['RotationChangeX'].std(),
                    'sd_rot_y': ht['RotationChangeY'].std(),
                    'sd_rot_z': ht['RotationChangeZ'].std(),
                })
            except Exception:
                pass

    df_ht = pd.DataFrame(ht_rows)

    # Pivot and merge
    pivot = df_ht.pivot(index='participant', columns='video',
                        values=['speed_total', 'speed_y', 'speed_x', 'speed_z',
                                'sd_rot_x', 'sd_rot_y', 'sd_rot_z'])
    pivot.columns = [f"{m}_{v}" for m, v in pivot.columns]
    pivot.reset_index(inplace=True)
    df = df.merge(pivot, on='participant', how='left')

    # Apply groupings
    df['phq_group'] = df['score_phq'].apply(phq_group)
    df['gad_group'] = df['score_gad'].apply(gad_group)
    df['distress'] = df.apply(distress_group, axis=1)
    df['avg_speed'] = df[[f'speed_total_{v}' for v in VIDEOS]].mean(axis=1)
    df['avg_speed_y'] = df[[f'speed_y_{v}' for v in VIDEOS]].mean(axis=1)

    return df


if __name__ == '__main__':
    df = load_data()
    df.to_csv(os.path.join(BASE_DIR, 'data', 'processed_data.csv'), index=False)

