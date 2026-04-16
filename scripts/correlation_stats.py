"""Figure 10: Correlation Heatmap + All Statistical Tests."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from load_data import VIDEOS, VIDEO_SHORT, PHQ_ORDER
from stats_helpers import (
    adaptive_correlation,
    adaptive_paired_test,
    adaptive_two_group_test,
    benjamini_hochberg,
    shapiro_safe,
)

# ── Figure 10: Correlation Heatmap ───────────────────────────────────────
corr_vars = ['score_phq', 'score_gad', 'score_stai_t', 'avg_speed', 'avg_speed_y']
corr_labels = ['PHQ-9', 'GAD-7', 'STAI-T', 'Scan Speed\n(Total)', 'Scan Speed\n(Yaw)']
corr_df = df[corr_vars].copy()
corr_df.columns = corr_labels
corr_mat = corr_df.corr()

fig, ax = plt.subplots(figsize=(8, 6.5))
mask = np.triu(np.ones_like(corr_mat, dtype=bool), k=1)
sns.heatmap(corr_mat, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, vmin=-1, vmax=1, ax=ax, linewidths=0.5, square=True)
ax.set_title('Figure 10: Correlation — Psychological Scores vs. Headtracking\n'
             '(Replicating Srivastava & Lahane, 2025, Fig 2)', fontweight='bold')
plt.tight_layout(); plt.savefig(f'{OUT}/fig10_correlation.png'); plt.close()

# Statistical Tests


# Descriptive statistics
print("\n--- Descriptive Statistics ---")
desc = df[['age', 'score_phq', 'score_gad', 'score_stai_t', 'score_vrise',
           'positive_affect_start', 'negative_affect_start',
           'positive_affect_end', 'negative_affect_end', 'avg_speed', 'avg_speed_y']].describe().round(2)
print(desc.to_string())

# Correlations with normality checks
print("\n--- Correlations with normality checks ---")
pairs = [('score_phq', 'score_gad'), ('score_phq', 'score_stai_t'),
         ('score_phq', 'avg_speed'), ('score_phq', 'avg_speed_y'),
         ('score_gad', 'avg_speed'), ('score_gad', 'avg_speed_y'),
         ('score_stai_t', 'avg_speed'), ('score_stai_t', 'avg_speed_y')]
corr_results = []
for a, b in pairs:
    tmp = df[[a, b]].dropna()
    result = adaptive_correlation(tmp[a], tmp[b])
    corr_results.append((a, b, result))

raw_corr_p = [result['p'] for _, _, result in corr_results]
corr_q = benjamini_hochberg(raw_corr_p)
for (a, b, result), q in zip(corr_results, corr_q):
    stat_name = 'r' if result['test'] == 'pearson' else 'rho'
    ci_text = ''
    if np.all(np.isfinite(result['ci'])):
        ci_text = f", 95% CI [{result['ci'][0]:.3f}, {result['ci'][1]:.3f}]"
    print(
        f"  {a} vs {b}: {result['test']} {stat_name}={result['stat']:.3f}, "
        f"p={result['p']:.4f}, q={q:.4f}{ci_text}, "
        f"Shapiro p=({result['normal'][0]:.3f}, {result['normal'][1]:.3f})"
    )

# Two-group comparisons with assumption checks
print("\n--- Two-group comparisons with assumption checks ---")
df_min = df[df['phq_group'] == 'Minimal (0-4)']
df_mod = df[df['phq_group'] == 'Moderate-Severe (≥10)']
speed_tests = []
for v in VIDEOS:
    col = f'speed_total_{v}'
    a = df_mod[col].dropna(); b = df_min[col].dropna()
    if len(a) < 2 or len(b) < 2:
        print(f"  {VIDEO_SHORT[v]}: insufficient data"); continue
    result = adaptive_two_group_test(a, b)
    speed_tests.append((v, 'total', result))
    ci_text = ''
    if np.all(np.isfinite(result['ci'])):
        ci_text = f", 95% CI [{result['ci'][0]:.3f}, {result['ci'][1]:.3f}]"
    print(
        f"  {VIDEO_SHORT[v]}: {result['test']} stat={result['stat']:.2f}, p={result['p']:.4f}{ci_text}, "
        f"normality p=({result['normal'][0]:.3f}, {result['normal'][1]:.3f})"
    )

# Yaw speed t-tests
print("\n--- Yaw speed comparisons with assumption checks ---")
yaw_tests = []
for v in VIDEOS:
    col = f'speed_y_{v}'
    a = df_mod[col].dropna(); b = df_min[col].dropna()
    if len(a) < 2 or len(b) < 2:
        print(f"  {VIDEO_SHORT[v]}: insufficient data"); continue
    result = adaptive_two_group_test(a, b)
    yaw_tests.append((v, 'yaw', result))
    ci_text = ''
    if np.all(np.isfinite(result['ci'])):
        ci_text = f", 95% CI [{result['ci'][0]:.3f}, {result['ci'][1]:.3f}]"
    print(
        f"  {VIDEO_SHORT[v]}: {result['test']} stat={result['stat']:.2f}, p={result['p']:.4f}{ci_text}, "
        f"normality p=({result['normal'][0]:.3f}, {result['normal'][1]:.3f})"
    )

speed_q = benjamini_hochberg([result['p'] for _, _, result in speed_tests])
yaw_q = benjamini_hochberg([result['p'] for _, _, result in yaw_tests])
if len(speed_tests) > 0:
    print("\n  FDR-adjusted q-values for total speed:")
    for (v, _, result), q in zip(speed_tests, speed_q):
        print(f"    {VIDEO_SHORT[v]}: p={result['p']:.4f}, q={q:.4f}")
if len(yaw_tests) > 0:
    print("\n  FDR-adjusted q-values for yaw speed:")
    for (v, _, result), q in zip(yaw_tests, yaw_q):
        print(f"    {VIDEO_SHORT[v]}: p={result['p']:.4f}, q={q:.4f}")

# Three-group comparisons with assumption checks
print("\n--- Three-group comparisons with assumption checks ---")
groups_data = [df[df['phq_group']==g]['avg_speed'].dropna() for g in PHQ_ORDER]
groups_data = [g for g in groups_data if len(g) > 0]
if len(groups_data) >= 2:
    normal_p = [shapiro_safe(g) for g in groups_data]
    levene_p = stats.levene(*groups_data, center='median').pvalue if len(groups_data) >= 2 else np.nan
    if all(np.isfinite(p) and p >= 0.05 for p in normal_p) and (not np.isfinite(levene_p) or levene_p >= 0.05):
        f_stat, p = stats.f_oneway(*groups_data)
        print(f"  Total Speed: one-way ANOVA F={f_stat:.2f}, p={p:.4f}, Levene p={levene_p:.4f}, Shapiro p={normal_p}")
    else:
        h, p = stats.kruskal(*groups_data)
        print(f"  Total Speed: Kruskal-Wallis H={h:.2f}, p={p:.4f}, Levene p={levene_p:.4f}, Shapiro p={normal_p}")
groups_y = [df[df['phq_group']==g]['avg_speed_y'].dropna() for g in PHQ_ORDER]
groups_y = [g for g in groups_y if len(g) > 0]
if len(groups_y) >= 2:
    normal_p = [shapiro_safe(g) for g in groups_y]
    levene_p = stats.levene(*groups_y, center='median').pvalue if len(groups_y) >= 2 else np.nan
    if all(np.isfinite(p) and p >= 0.05 for p in normal_p) and (not np.isfinite(levene_p) or levene_p >= 0.05):
        f_stat, p = stats.f_oneway(*groups_y)
        print(f"  Yaw Speed: one-way ANOVA F={f_stat:.2f}, p={p:.4f}, Levene p={levene_p:.4f}, Shapiro p={normal_p}")
    else:
        h, p = stats.kruskal(*groups_y)
        print(f"  Yaw Speed: Kruskal-Wallis H={h:.2f}, p={p:.4f}, Levene p={levene_p:.4f}, Shapiro p={normal_p}")

# Outlier check
print("\n--- Outlier Check (|z| > 3) ---")
for name, col in [('PHQ-9', 'score_phq'), ('GAD-7', 'score_gad'), ('STAI-T', 'score_stai_t')]:
    z = np.abs(stats.zscore(df[col]))
    print(f"  {name}: {(z>3).sum()} outlier(s)")

# PANAS
print("\n--- PANAS paired comparisons with assumption checks ---")
pa_result = adaptive_paired_test(df['positive_affect_start'], df['positive_affect_end'])
na_result = adaptive_paired_test(df['negative_affect_start'], df['negative_affect_end'])
for label, result in [('Positive Affect', pa_result), ('Negative Affect', na_result)]:
    ci_text = ''
    if np.all(np.isfinite(result['ci'])):
        ci_text = f", 95% CI [{result['ci'][0]:.3f}, {result['ci'][1]:.3f}]"
    print(f"  {label}: {result['test']} stat={result['stat']:.2f}, p={result['p']:.4f}{ci_text}, normality p={result['normal']:.3f}")

# Sample size
print(f"\n--- Sample Size ---")
print(f"  Total N = {len(df)}")
for g in PHQ_ORDER:
    print(f"  {g}: n={len(df[df['phq_group']==g])}")
print(f"  NOTE: Small sample (N=40) limits power. Reference paper had N=50.")
