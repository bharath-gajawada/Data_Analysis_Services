"""
Report 2 — Figure 18: Standard Deviation of Yaw (SDY) Analysis
SDY captures exploration range, complementing the speed measures.
Used in Srivastava & Lahane (2025) as an additional headtracking metric.
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

# Compute average SDY across videos
sdy_cols = [f'sd_rot_y_{v}' for v in VIDEOS]
df['avg_sdy'] = df[sdy_cols].mean(axis=1)

# Kruskal-Wallis for SDY across PHQ groups
sdy_groups = [df[df['phq_group'] == g]['avg_sdy'].dropna().values for g in PHQ_ORDER]
sdy_groups = [g for g in sdy_groups if len(g) > 0]
if len(sdy_groups) >= 2:
    h, p = stats.kruskal(*sdy_groups)

# Correlations: PHQ-9 vs SDY
sdy_clean = df[['score_phq', 'avg_sdy']].dropna()
r_p, p_p = stats.pearsonr(sdy_clean['score_phq'], sdy_clean['avg_sdy'])
r_s, p_s = stats.spearmanr(sdy_clean['score_phq'], sdy_clean['avg_sdy'])

# Mann-Whitney U: Minimal vs Moderate-Severe
sdy_min = df[df['phq_group'] == 'Minimal (0-4)']['avg_sdy'].dropna()
sdy_mod = df[df['phq_group'] == 'Moderate-Severe (≥10)']['avg_sdy'].dropna()
if len(sdy_min) > 0 and len(sdy_mod) > 0:
    u, p_u = stats.mannwhitneyu(sdy_min, sdy_mod, alternative='two-sided')
    r_rb = 1 - (2*u)/(len(sdy_min)*len(sdy_mod))

# Per-video SDY analysis
for v in VIDEOS:
    col = f'sd_rot_y_{v}'
    a = df[df['phq_group'] == 'Minimal (0-4)'][col].dropna()
    b = df[df['phq_group'] == 'Moderate-Severe (≥10)'][col].dropna()
    if len(a) >= 2 and len(b) >= 2:
        t, p = stats.ttest_ind(a, b, equal_var=False)
        d = (b.mean()-a.mean()) / np.sqrt((a.std()**2+b.std()**2)/2) if (a.std()+b.std()) > 0 else 0

# FIGURE 18: SDY by Depression Group
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Overall SDY by group
ax = axes[0]
plot_data = df[['phq_group', 'avg_sdy']].dropna()
plot_data['phq_group'] = pd.Categorical(plot_data['phq_group'], categories=PHQ_ORDER, ordered=True)
sns.boxplot(data=plot_data, x='phq_group', y='avg_sdy', order=PHQ_ORDER,
            palette=COLORS_3, ax=ax, width=0.5)
sns.stripplot(data=plot_data, x='phq_group', y='avg_sdy', order=PHQ_ORDER,
              color='black', alpha=0.4, size=5, ax=ax, jitter=True)
ax.set_xlabel('PHQ-9 Group')
ax.set_ylabel('Avg SDY (°)')
ax.set_title(f'Avg SDY by Depression Group\nKruskal-Wallis H={h:.2f}, p={p:.3f}', fontweight='bold')

# Panel B: Per-video SDY
sdy_long_cols = {f'sd_rot_y_{v}': VIDEO_SHORT[v] for v in VIDEOS}
sdy_long = []
for _, row in df.iterrows():
    for col, vname in sdy_long_cols.items():
        if pd.notna(row.get(col)):
            sdy_long.append({'phq_group': row['phq_group'], 'video': vname, 'sdy': row[col]})
df_sdy_long = pd.DataFrame(sdy_long)
df_sdy_long['phq_group'] = pd.Categorical(df_sdy_long['phq_group'], categories=PHQ_ORDER, ordered=True)

ax = axes[1]
video_order = ['Abandoned', 'Beach', 'Campus', 'Horror', 'Surf']
sns.boxplot(data=df_sdy_long, x='video', y='sdy', hue='phq_group',
            hue_order=PHQ_ORDER, palette=COLORS_3, order=video_order, ax=ax)
ax.set_xlabel('Video')
ax.set_ylabel('SDY (°)')
ax.set_title('SDY by Video × Depression Group', fontweight='bold')
ax.legend(title='PHQ-9 Group', fontsize=8)

fig.suptitle('Figure 18: Standard Deviation of Yaw (SDY) — Exploration Range\n'
             '(SDY captures variability of horizontal scanning; lower = less exploration)',
             fontweight='bold', fontsize=12, y=1.04)
plt.tight_layout()
plt.savefig(f'{OUT}/fig18_sdy_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# FIGURE 19: SDY vs PHQ-9 Scatter
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(df['score_phq'], df['avg_sdy'], c=df['score_gad'], cmap='RdYlGn_r',
           s=70, edgecolors='black', linewidth=0.5, alpha=0.8)
plt.colorbar(ax.collections[0], ax=ax, label='GAD-7 Score')
# Regression line
m, b = np.polyfit(df['score_phq'].dropna(), df['avg_sdy'].dropna(), 1)
x_line = np.linspace(0, df['score_phq'].max() + 1, 50)
ax.plot(x_line, m*x_line + b, 'r--', lw=2)
ax.set_xlabel('PHQ-9 Score')
ax.set_ylabel('Average SDY (°)')
ax.set_title(f'Figure 19: PHQ-9 vs SDY Correlation\n'
             f'Pearson r={r_p:.3f}, p={p_p:.3f} | Spearman ρ={r_s:.3f}, p={p_s:.3f}',
             fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUT}/fig19_sdy_correlation.png', dpi=150, bbox_inches='tight')
plt.close()
