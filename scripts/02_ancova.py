"""
Report 2 — Figure 14: ANCOVA — Depression effect on scanning speed, controlling for anxiety.
Replicates the reference paper's primary analysis (Srivastava & Lahane, 2025).
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

# ANCOVA: Scanning Speed ~ PHQ Group + GAD-7 (covariate)

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("WARNING: statsmodels not installed. Install with: pip install statsmodels")

if HAS_STATSMODELS:
    ancova_df = df[['avg_speed', 'avg_speed_y', 'phq_group', 'score_gad', 'score_stai_t']].dropna()
    ancova_df['phq_group'] = pd.Categorical(ancova_df['phq_group'], categories=PHQ_ORDER, ordered=True)

    # ANCOVA 1: Total Speed ~ PHQ Group + GAD-7
    model1 = ols('avg_speed ~ C(phq_group, Treatment) + score_gad', data=ancova_df).fit()
    anova1 = anova_lm(model1, typ=2)
    ss_phq = anova1.loc['C(phq_group, Treatment)', 'sum_sq']
    ss_resid = anova1.loc['Residual', 'sum_sq']
    eta_sq_phq = ss_phq / (ss_phq + ss_resid)

    # ANCOVA 2: Yaw Speed ~ PHQ Group + GAD-7
    model2 = ols('avg_speed_y ~ C(phq_group, Treatment) + score_gad', data=ancova_df).fit()
    anova2 = anova_lm(model2, typ=2)
    ss_phq2 = anova2.loc['C(phq_group, Treatment)', 'sum_sq']
    ss_resid2 = anova2.loc['Residual', 'sum_sq']
    eta_sq_phq2 = ss_phq2 / (ss_phq2 + ss_resid2)

    # ANCOVA 3: Total Speed ~ PHQ Group + GAD-7 + STAI-T
    model3 = ols('avg_speed ~ C(phq_group, Treatment) + score_gad + score_stai_t', data=ancova_df).fit()
    anova3 = anova_lm(model3, typ=2)

    # Assumption Check: Homogeneity of regression slopes
    model_interact = ols('avg_speed ~ C(phq_group, Treatment) * score_gad', data=ancova_df).fit()
    anova_interact = anova_lm(model_interact, typ=2)
    interact_p = anova_interact.loc['C(phq_group, Treatment):score_gad', 'PR(>F)']

    # FIGURE 14: ANCOVA-adjusted Group Means
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors3 = ['#59a14f', '#edc948', '#e15759']

    # Panel A: Total Speed
    group_means = ancova_df.groupby('phq_group')['avg_speed'].agg(['mean', 'std', 'count'])
    group_means = group_means.reindex(PHQ_ORDER)
    se = group_means['std'] / np.sqrt(group_means['count'])
    axes[0].bar(range(3), group_means['mean'], yerr=1.96*se, capsize=6,
                color=colors3, edgecolor='black', linewidth=0.5, alpha=0.85)
    axes[0].set_xticks(range(3))
    axes[0].set_xticklabels(PHQ_ORDER, fontsize=9)
    axes[0].set_ylabel('Mean Total Scan Speed (°/s)')
    f_val = anova1.loc['C(phq_group, Treatment)', 'F']
    p_val = anova1.loc['C(phq_group, Treatment)', 'PR(>F)']
    axes[0].set_title(f'Total Speed\nANCOVA: F={f_val:.2f}, p={p_val:.3f}, η²={eta_sq_phq:.3f}',
                      fontweight='bold')
    # Add n labels
    for i, (_, row) in enumerate(group_means.iterrows()):
        axes[0].text(i, row['mean'] - 2, f'n={int(row["count"])}\nM={row["mean"]:.1f}',
                     ha='center', fontsize=9, fontweight='bold')

    # Panel B: Yaw Speed
    group_means_y = ancova_df.groupby('phq_group')['avg_speed_y'].agg(['mean', 'std', 'count'])
    group_means_y = group_means_y.reindex(PHQ_ORDER)
    se_y = group_means_y['std'] / np.sqrt(group_means_y['count'])
    axes[1].bar(range(3), group_means_y['mean'], yerr=1.96*se_y, capsize=6,
                color=colors3, edgecolor='black', linewidth=0.5, alpha=0.85)
    axes[1].set_xticks(range(3))
    axes[1].set_xticklabels(PHQ_ORDER, fontsize=9)
    axes[1].set_ylabel('Mean Yaw Speed (°/s)')
    f_val2 = anova2.loc['C(phq_group, Treatment)', 'F']
    p_val2 = anova2.loc['C(phq_group, Treatment)', 'PR(>F)']
    axes[1].set_title(f'Yaw Speed\nANCOVA: F={f_val2:.2f}, p={p_val2:.3f}, η²={eta_sq_phq2:.3f}',
                      fontweight='bold')
    for i, (_, row) in enumerate(group_means_y.iterrows()):
        axes[1].text(i, row['mean'] - 1, f'n={int(row["count"])}\nM={row["mean"]:.1f}',
                     ha='center', fontsize=9, fontweight='bold')

    fig.suptitle('Figure 14: ANCOVA — Scanning Speed by PHQ-9 Group, Controlling for GAD-7\n'
                 '(Error bars = 95% CI; replicating Srivastava & Lahane, 2025)',
                 fontweight='bold', fontsize=12, y=1.04)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig14_ancova_results.png', dpi=150, bbox_inches='tight')
    plt.close()


    # Levene's test for homogeneity of variances
    groups = [ancova_df[ancova_df['phq_group'] == g]['avg_speed'].values for g in PHQ_ORDER]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) >= 2:
        lev_stat, lev_p = stats.levene(*groups)

    groups_y = [ancova_df[ancova_df['phq_group'] == g]['avg_speed_y'].values for g in PHQ_ORDER]
    groups_y = [g for g in groups_y if len(g) > 0]
    if len(groups_y) >= 2:
        lev_stat_y, lev_p_y = stats.levene(*groups_y)

else:
    print("Skipping ANCOVA — statsmodels not available.")
