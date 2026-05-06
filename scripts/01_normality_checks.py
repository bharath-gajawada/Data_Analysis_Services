"""
Report 2 — Figure 11 & 12: Normality Checks
Shapiro-Wilk tests + Q-Q plots for all key variables.
Determines whether parametric or non-parametric tests are appropriate.
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
PHQ_ORDER = mod.PHQ_ORDER

# Collect all variables to test for normality
normality_results = []

# --- Overall variables ---
overall_vars = {
    'PHQ-9': df['score_phq'],
    'GAD-7': df['score_gad'],
    'STAI-T': df['score_stai_t'],
    'Positive Affect (Pre)': df['positive_affect_start'],
    'Negative Affect (Pre)': df['negative_affect_start'],
    'Positive Affect (Post)': df['positive_affect_end'],
    'Negative Affect (Post)': df['negative_affect_end'],
    'Avg Scan Speed (Total)': df['avg_speed'],
    'Avg Scan Speed (Yaw)': df['avg_speed_y'],
}

# Add per-video speed variables
for v in VIDEOS:
    overall_vars[f'Speed Total ({VIDEO_SHORT[v]})'] = df[f'speed_total_{v}']
    overall_vars[f'Speed Yaw ({VIDEO_SHORT[v]})'] = df[f'speed_y_{v}']
    overall_vars[f'SDY ({VIDEO_SHORT[v]})'] = df[f'sd_rot_y_{v}']

for name, series in overall_vars.items():
    data = series.dropna()
    if len(data) < 3:
        continue
    w_stat, p_val = stats.shapiro(data)
    normality_results.append({
        'Variable': name,
        'Group': 'Overall',
        'N': len(data),
        'W': round(w_stat, 4),
        'p-value': round(p_val, 4),
        'Normal (a=.05)': 'Yes' if p_val > 0.05 else 'No',
        'Skewness': round(stats.skew(data), 3),
        'Kurtosis': round(stats.kurtosis(data), 3),
    })

# --- Within-group normality (for group comparison variables) ---
key_speed_vars = ['avg_speed', 'avg_speed_y']
for grp_name in PHQ_ORDER:
    grp_df = df[df['phq_group'] == grp_name]
    for var_name, col_name in [('Avg Speed (Total)', 'avg_speed'), ('Avg Speed (Yaw)', 'avg_speed_y')]:
        data = grp_df[col_name].dropna()
        if len(data) < 3:
            continue
        w_stat, p_val = stats.shapiro(data)
        normality_results.append({
            'Variable': var_name,
            'Group': grp_name,
            'N': len(data),
            'W': round(w_stat, 4),
            'p-value': round(p_val, 4),
            'Normal (a=.05)': 'Yes' if p_val > 0.05 else 'No',
            'Skewness': round(stats.skew(data), 3),
            'Kurtosis': round(stats.kurtosis(data), 3),
        })

norm_df = pd.DataFrame(normality_results)

# FIGURE 11: Q-Q Plots for Key Variables
qq_vars = [
    ('PHQ-9', df['score_phq']),
    ('GAD-7', df['score_gad']),
    ('STAI-T', df['score_stai_t']),
    ('Avg Scan Speed\n(Total)', df['avg_speed']),
    ('Avg Scan Speed\n(Yaw)', df['avg_speed_y']),
    ('Positive Affect\n(Pre-VR)', df['positive_affect_start']),
    ('Negative Affect\n(Pre-VR)', df['negative_affect_start']),
    ('VRISE Score', df['score_vrise']),
]

fig, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()

for i, (name, data) in enumerate(qq_vars):
    data_clean = data.dropna()
    ax = axes[i]
    res = stats.probplot(data_clean, dist="norm", plot=ax)
    w, p = stats.shapiro(data_clean)
    ax.set_title(f'{name}\nW={w:.3f}, p={p:.3f}', fontsize=10,
                 fontweight='bold' if p < 0.05 else 'normal',
                 color='red' if p < 0.05 else 'black')
    ax.get_lines()[0].set_markerfacecolor('#4e79a7')
    ax.get_lines()[0].set_markersize(5)
    ax.get_lines()[1].set_color('#e15759')
    ax.get_lines()[1].set_linewidth(2)

fig.suptitle('Figure 11: Q-Q Plots — Normality Assessment of Key Variables\n'
             '(Red title = normality rejected at α = .05)',
             fontweight='bold', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUT}/fig11_qq_plots.png', dpi=150, bbox_inches='tight')
plt.close()


# FIGURE 12: Q-Q Plots for Scanning Speed within each PHQ-9 Group
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
colors_grp = {'Minimal (0-4)': '#59a14f', 'Mild (5-9)': '#edc948', 'Moderate-Severe (≥10)': '#e15759'}

for col_idx, (speed_name, speed_col) in enumerate([('Total Speed', 'avg_speed'), ('Yaw Speed', 'avg_speed_y')]):
    for grp_idx, grp in enumerate(PHQ_ORDER):
        ax = axes[col_idx, grp_idx]
        grp_data = df[df['phq_group'] == grp][speed_col].dropna()
        if len(grp_data) < 3:
            ax.set_title(f'{speed_name}\n{grp} (n={len(grp_data)})\nInsufficient data')
            continue
        res = stats.probplot(grp_data, dist="norm", plot=ax)
        w, p = stats.shapiro(grp_data)
        ax.set_title(f'{speed_name}\n{grp} (n={len(grp_data)})\nW={w:.3f}, p={p:.3f}',
                     fontsize=9, color='red' if p < 0.05 else 'black')
        ax.get_lines()[0].set_markerfacecolor(colors_grp[grp])
        ax.get_lines()[0].set_markersize(5)

fig.suptitle('Figure 12: Within-Group Normality — Scanning Speed by PHQ-9 Group\n'
             '(Checking ANOVA/t-test assumption: residuals should be normally distributed)',
             fontweight='bold', fontsize=12, y=1.03)
plt.tight_layout()
plt.savefig(f'{OUT}/fig12_qq_within_groups.png', dpi=150, bbox_inches='tight')
plt.close()


# FIGURE 13: Histograms with Normal Overlay
hist_vars = [
    ('PHQ-9', df['score_phq'], '#4e79a7'),
    ('GAD-7', df['score_gad'], '#e15759'),
    ('Avg Scan Speed (Total)', df['avg_speed'], '#59a14f'),
    ('Avg Scan Speed (Yaw)', df['avg_speed_y'], '#edc948'),
]

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes = axes.flatten()

for i, (name, data, color) in enumerate(hist_vars):
    ax = axes[i]
    data_clean = data.dropna()
    ax.hist(data_clean, bins=15, density=True, alpha=0.7, color=color, edgecolor='black', linewidth=0.5)
    # Normal overlay
    mu, sigma = data_clean.mean(), data_clean.std()
    x = np.linspace(data_clean.min() - sigma, data_clean.max() + sigma, 100)
    ax.plot(x, stats.norm.pdf(x, mu, sigma), 'k--', lw=2, label=f'Normal(μ={mu:.1f}, σ={sigma:.1f})')
    w, p = stats.shapiro(data_clean)
    ax.set_title(f'{name}\nShapiro-Wilk: W={w:.3f}, p={p:.3f}', fontweight='bold',
                 color='red' if p < 0.05 else 'black')
    ax.set_ylabel('Density')
    ax.legend(fontsize=8)

fig.suptitle('Figure 13: Distribution of Key Variables with Normal Overlay\n'
             '(Red title = normality rejected at α = .05)',
             fontweight='bold', fontsize=13, y=1.03)
plt.tight_layout()
plt.savefig(f'{OUT}/fig13_hist_normal_overlay.png', dpi=150, bbox_inches='tight')
plt.close()


# Save results to CSV
norm_df.to_csv(f'{OUT}/normality_results.csv', index=False)
