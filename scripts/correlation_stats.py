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

# Pearson correlations
print("\n--- Pearson Correlations ---")
pairs = [('score_phq', 'score_gad'), ('score_phq', 'score_stai_t'),
         ('score_phq', 'avg_speed'), ('score_phq', 'avg_speed_y'),
         ('score_gad', 'avg_speed'), ('score_gad', 'avg_speed_y'),
         ('score_stai_t', 'avg_speed'), ('score_stai_t', 'avg_speed_y')]
for a, b in pairs:
    tmp = df[[a, b]].dropna()
    r, p = stats.pearsonr(tmp[a], tmp[b])
    print(f"  {a} vs {b}: r={r:.3f}, p={p:.4f}")

# T-tests: Minimal vs Moderate-Severe
print("\n--- T-tests: Minimal vs Moderate-Severe Depression (Total Speed) ---")
df_min = df[df['phq_group'] == 'Minimal (0-4)']
df_mod = df[df['phq_group'] == 'Moderate-Severe (≥10)']
for v in VIDEOS:
    col = f'speed_total_{v}'
    a = df_mod[col].dropna(); b = df_min[col].dropna()
    if len(a) < 2 or len(b) < 2:
        print(f"  {VIDEO_SHORT[v]}: insufficient data"); continue
    t, p = stats.ttest_ind(a, b, equal_var=False)
    d = (a.mean()-b.mean()) / np.sqrt((a.std()**2+b.std()**2)/2) if (a.std()+b.std()) > 0 else 0
    print(f"  {VIDEO_SHORT[v]}: Mod M={a.mean():.2f} SD={a.std():.2f}, "
          f"Min M={b.mean():.2f} SD={b.std():.2f}, t={t:.2f}, p={p:.4f}, d={d:.3f}")

# Yaw speed t-tests
print("\n--- T-tests: Yaw Speed Minimal vs Moderate-Severe ---")
for v in VIDEOS:
    col = f'speed_y_{v}'
    a = df_mod[col].dropna(); b = df_min[col].dropna()
    if len(a) < 2 or len(b) < 2:
        print(f"  {VIDEO_SHORT[v]}: insufficient data"); continue
    t, p = stats.ttest_ind(a, b, equal_var=False)
    d = (a.mean()-b.mean()) / np.sqrt((a.std()**2+b.std()**2)/2) if (a.std()+b.std()) > 0 else 0
    print(f"  {VIDEO_SHORT[v]}: Mod M={a.mean():.2f}, Min M={b.mean():.2f}, t={t:.2f}, p={p:.4f}, d={d:.3f}")

# Kruskal-Wallis
print("\n--- Kruskal-Wallis: Speed across 3 PHQ groups ---")
groups_data = [df[df['phq_group']==g]['avg_speed'].dropna() for g in PHQ_ORDER]
groups_data = [g for g in groups_data if len(g) > 0]
if len(groups_data) >= 2:
    h, p = stats.kruskal(*groups_data)
    print(f"  Total Speed: H={h:.2f}, p={p:.4f}")
groups_y = [df[df['phq_group']==g]['avg_speed_y'].dropna() for g in PHQ_ORDER]
groups_y = [g for g in groups_y if len(g) > 0]
if len(groups_y) >= 2:
    h, p = stats.kruskal(*groups_y)
    print(f"  Yaw Speed: H={h:.2f}, p={p:.4f}")

# Outlier check
print("\n--- Outlier Check (|z| > 3) ---")
for name, col in [('PHQ-9', 'score_phq'), ('GAD-7', 'score_gad'), ('STAI-T', 'score_stai_t')]:
    z = np.abs(stats.zscore(df[col]))
    print(f"  {name}: {(z>3).sum()} outlier(s)")

# PANAS
print("\n--- PANAS Paired t-tests ---")
t1, p1 = stats.ttest_rel(df['positive_affect_start'], df['positive_affect_end'])
t2, p2 = stats.ttest_rel(df['negative_affect_start'], df['negative_affect_end'])
print(f"  Positive Affect: t={t1:.2f}, p={p1:.4f}")
print(f"  Negative Affect: t={t2:.2f}, p={p2:.4f}")

# Sample size
print(f"\n--- Sample Size ---")
print(f"  Total N = {len(df)}")
for g in PHQ_ORDER:
    print(f"  {g}: n={len(df[df['phq_group']==g])}")
print(f"  NOTE: Small sample (N=40) limits power. Reference paper had N=50.")
