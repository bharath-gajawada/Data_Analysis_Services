"""
Report 2 — Figure 17: Two-Way Mixed ANOVA
Between-subjects: PHQ-9 group (3 levels)
Within-subjects: Video type (5 levels)
DV: Scanning speed
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT, mod = load_and_setup()

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd

VIDEOS = mod.VIDEOS
VIDEO_SHORT = mod.VIDEO_SHORT
VIDEO_NAMES = mod.VIDEO_NAMES
PHQ_ORDER = mod.PHQ_ORDER
COLORS_3 = mod.COLORS_3

# Prepare long-format data for mixed ANOVA
speed_cols = {f'speed_total_{v}': VIDEO_SHORT[v] for v in VIDEOS}
long_data = []
for _, row in df.iterrows():
    pid = row['participant']
    grp = row['phq_group']
    for col, vname in speed_cols.items():
        if pd.notna(row.get(col)):
            long_data.append({'participant': pid, 'phq_group': grp,
                              'video': vname, 'speed': row[col]})

df_long = pd.DataFrame(long_data)
df_long['phq_group'] = pd.Categorical(df_long['phq_group'], categories=PHQ_ORDER, ordered=True)

# Filter to participants with complete data across all 5 videos
complete_pids = df_long.groupby('participant')['video'].nunique()
complete_pids = complete_pids[complete_pids == 5].index
df_balanced = df_long[df_long['participant'].isin(complete_pids)].copy()

try:
    import pingouin as pg
    HAS_PINGOUIN = True
except ImportError:
    HAS_PINGOUIN = False
    print("WARNING: pingouin not installed. Install with: pip install pingouin")
    print("Falling back to manual computation...")

aov = None  # initialize for use in plotting

if HAS_PINGOUIN:
    aov = pg.mixed_anova(data=df_balanced, dv='speed', within='video',
                         between='phq_group', subject='participant')

    # Mauchly's sphericity test
    spher = pg.sphericity(data=df_balanced, dv='speed', within='video', subject='participant')

    # Post-hoc: Pairwise between-group comparisons per video
    for v in ['Abandoned', 'Beach', 'Campus', 'Horror', 'Surf']:
        v_data = df_long[df_long['video'] == v]
        g_min = v_data[v_data['phq_group'] == 'Minimal (0-4)']['speed'].dropna()
        g_mod = v_data[v_data['phq_group'] == 'Moderate-Severe (≥10)']['speed'].dropna()
        if len(g_min) > 0 and len(g_mod) > 0:
            u_stat, u_p = stats.mannwhitneyu(g_min, g_mod, alternative='two-sided')
            r_effect = 1 - (2*u_stat)/(len(g_min)*len(g_mod))

if not HAS_PINGOUIN:
    # Fallback: Separate Kruskal-Wallis per Video
    for v in ['Abandoned', 'Beach', 'Campus', 'Horror', 'Surf']:
        v_data = df_long[df_long['video'] == v]
        groups = [v_data[v_data['phq_group'] == g]['speed'].dropna().values for g in PHQ_ORDER]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) >= 2:
            h, p = stats.kruskal(*groups)

    # Friedman Test: Within-subjects effect of video
    if len(complete_pids) > 0:
        pivot_friedman = df_balanced.pivot(index='participant', columns='video', values='speed')
        chi2, p = stats.friedmanchisquare(*[pivot_friedman[c].values for c in pivot_friedman.columns])

# FIGURE 17: Interaction Plot
fig, ax = plt.subplots(figsize=(12, 7))

video_order = ['Abandoned', 'Beach', 'Campus', 'Horror', 'Surf']
for i, grp in enumerate(PHQ_ORDER):
    grp_data = df_long[df_long['phq_group'] == grp]
    means = grp_data.groupby('video')['speed'].mean().reindex(video_order)
    sems = grp_data.groupby('video')['speed'].sem().reindex(video_order)
    x_pos = np.arange(len(video_order)) + (i - 1) * 0.15  # slight offset
    ax.errorbar(x_pos, means.values, yerr=1.96*sems.values,
                fmt='o-', capsize=5, capthick=2, linewidth=2, markersize=8,
                color=COLORS_3[i], label=grp)

ax.set_xticks(range(len(video_order)))
ax.set_xticklabels(video_order, fontsize=11)
ax.set_xlabel('Video Type', fontsize=12)
ax.set_ylabel('Mean Scanning Speed (°/s)', fontsize=12)
ax.legend(title='PHQ-9 Group', fontsize=10)
ax.grid(True, alpha=0.3)

title_str = 'Figure 17: Interaction Plot — Video Type × Depression Group\n'
if HAS_PINGOUIN and aov is not None:
    # Get p-values from the ANOVA table (pingouin uses 'p_unc' column)
    p_between = aov[aov['Source'] == 'phq_group']['p_unc'].values[0]
    p_within = aov[aov['Source'] == 'video']['p_unc'].values[0]
    p_interact = aov[aov['Source'] == 'Interaction']['p_unc'].values[0]
    title_str += (f'Between (PHQ): p={p_between:.3f} | '
                  f'Within (Video): p={p_within:.3f} | '
                  f'Interaction: p={p_interact:.3f}')
else:
    title_str += '(Mixed ANOVA — pingouin not installed for full results)'

ax.set_title(title_str, fontweight='bold', fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUT}/fig17_interaction_plot.png', dpi=150, bbox_inches='tight')
plt.close()
