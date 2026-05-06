"""
Report 2 — Figure 21: Extended Correlation Heatmap
Includes SDY, per-video speeds, and additional psychological measures.
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

# Compute average SDY
sdy_cols = [f'sd_rot_y_{v}' for v in VIDEOS]
df['avg_sdy'] = df[sdy_cols].mean(axis=1)

# FIGURE 21: Extended Correlation Heatmap
corr_vars = ['score_phq', 'score_gad', 'score_stai_t',
             'positive_affect_start', 'negative_affect_start',
             'avg_speed', 'avg_speed_y', 'avg_sdy', 'score_vrise']
corr_labels = ['PHQ-9', 'GAD-7', 'STAI-T',
               'Positive\nAffect', 'Negative\nAffect',
               'Scan Speed\n(Total)', 'Scan Speed\n(Yaw)', 'SDY\n(Yaw)', 'VRISE']

corr_df = df[corr_vars].copy()
corr_df.columns = corr_labels

# Compute correlation matrix with p-values
n_vars = len(corr_labels)
r_mat = np.zeros((n_vars, n_vars))
p_mat = np.zeros((n_vars, n_vars))
for i in range(n_vars):
    for j in range(n_vars):
        tmp = corr_df[[corr_labels[i], corr_labels[j]]].dropna()
        if len(tmp) > 2:
            r, p = stats.pearsonr(tmp.iloc[:, 0], tmp.iloc[:, 1])
            r_mat[i, j] = r
            p_mat[i, j] = p

# Annotation with significance stars
annot = np.empty((n_vars, n_vars), dtype=object)
for i in range(n_vars):
    for j in range(n_vars):
        stars = ''
        if p_mat[i, j] < 0.001: stars = '***'
        elif p_mat[i, j] < 0.01: stars = '**'
        elif p_mat[i, j] < 0.05: stars = '*'
        annot[i, j] = f'{r_mat[i, j]:.2f}{stars}'

r_df = pd.DataFrame(r_mat, index=corr_labels, columns=corr_labels)

fig, ax = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(r_df, dtype=bool), k=1)
sns.heatmap(r_df, mask=mask, annot=annot, fmt='s', cmap='RdBu_r',
            center=0, vmin=-1, vmax=1, ax=ax, linewidths=0.5, square=True,
            annot_kws={'fontsize': 9})
ax.set_title('Figure 21: Extended Correlation Matrix — Psychological Scores, Speed & SDY\n'
             '(* p<.05, ** p<.01, *** p<.001)',
             fontweight='bold', fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUT}/fig21_extended_correlation.png', dpi=150, bbox_inches='tight')
plt.close()


# Non-parametric correlations (Spearman) for comparison
key_pairs = [
    ('score_phq', 'avg_speed', 'PHQ-9 vs Total Speed'),
    ('score_phq', 'avg_speed_y', 'PHQ-9 vs Yaw Speed'),
    ('score_phq', 'avg_sdy', 'PHQ-9 vs SDY'),
    ('score_gad', 'avg_speed', 'GAD-7 vs Total Speed'),
    ('score_gad', 'avg_sdy', 'GAD-7 vs SDY'),
]
for col1, col2, label in key_pairs:
    tmp = df[[col1, col2]].dropna()
    r_s, p_s = stats.spearmanr(tmp[col1], tmp[col2])
