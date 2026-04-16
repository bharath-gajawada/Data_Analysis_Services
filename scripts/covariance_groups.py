"""Figures 3 & 4: PHQ × GAD Covariance Scatter + Group Distribution Bars."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from stats_helpers import adaptive_correlation

# ── Figure 3: Covariance scatter ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 6))
scatter = ax.scatter(df['score_phq'], df['score_gad'], c=df['score_stai_t'],
                     cmap='RdYlGn_r', s=80, edgecolors='black', linewidth=0.5, alpha=0.8)
plt.colorbar(scatter, ax=ax, label='STAI-T (Trait Anxiety)')
m, b = np.polyfit(df['score_phq'], df['score_gad'], 1)
x_line = np.linspace(0, 20, 50)
ax.plot(x_line, m*x_line + b, 'r--', lw=2)
result = adaptive_correlation(df['score_phq'], df['score_gad'])
ci_text = ''
if np.all(np.isfinite(result['ci'])):
    ci_text = f', 95% CI [{result["ci"][0]:.3f}, {result["ci"][1]:.3f}]'
metric_label = 'r' if result['test'] == 'pearson' else 'rho'
ax.set_title(
    f'Figure 3: Depression × Anxiety Covariance\n'
    f'{result["test"]} {metric_label} = {result["stat"]:.3f}, p = {result["p"]:.4f}{ci_text}',
    fontweight='bold'
)
ax.set_xlabel('PHQ-9 (Depression)'); ax.set_ylabel('GAD-7 (Anxiety)')
ax.axvline(4.5, color='gray', ls=':', alpha=0.5); ax.axhline(4.5, color='gray', ls=':', alpha=0.5)
ax.axvline(9.5, color='gray', ls=':', alpha=0.5); ax.axhline(9.5, color='gray', ls=':', alpha=0.5)
plt.tight_layout(); plt.savefig(f'{OUT}/fig3_phq_gad_covariance.png'); plt.close()

# ── Figure 4: Group distributions ────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
colors3 = ['#59a14f', '#edc948', '#e15759']

phq_counts = df['phq_group'].value_counts().reindex(['Minimal (0-4)', 'Mild (5-9)', 'Moderate-Severe (≥10)'])
axes[0].bar(range(3), phq_counts.values, color=colors3)
axes[0].set_xticks(range(3)); axes[0].set_xticklabels(phq_counts.index, fontsize=9)
for i, v in enumerate(phq_counts.values): axes[0].text(i, v+0.3, str(v), ha='center', fontweight='bold')
axes[0].set_title('PHQ-9 Groups'); axes[0].set_ylabel('Count')

gad_counts = df['gad_group'].value_counts().reindex(['Minimal (0-4)', 'Mild (5-9)', 'Moderate-Severe (≥10)'])
axes[1].bar(range(3), gad_counts.values, color=colors3)
axes[1].set_xticks(range(3)); axes[1].set_xticklabels(gad_counts.index, fontsize=9)
for i, v in enumerate(gad_counts.values): axes[1].text(i, v+0.3, str(v), ha='center', fontweight='bold')
axes[1].set_title('GAD-7 Groups'); axes[1].set_ylabel('Count')

dist_counts = df['distress'].value_counts()
axes[2].barh(range(len(dist_counts)), dist_counts.values, color=sns.color_palette('Set2', len(dist_counts)))
axes[2].set_yticks(range(len(dist_counts)))
axes[2].set_yticklabels(dist_counts.index, fontsize=8)
for i, v in enumerate(dist_counts.values): axes[2].text(v+0.2, i, str(v), va='center', fontweight='bold')
axes[2].set_title('Distress Groups (PHQ × GAD)'); axes[2].set_xlabel('Count')

fig.suptitle('Figure 4: Participant Grouping Based on Clinical Cutoffs & Co-occurring Distress',
             fontweight='bold', y=1.03)
plt.tight_layout(); plt.savefig(f'{OUT}/fig4_group_distributions.png'); plt.close()
