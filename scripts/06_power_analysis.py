"""
Report 2 — Figure 20: Power Analysis
Computes required sample size to detect the reference paper's effect sizes
and post-hoc power for our study.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT, mod = load_and_setup()

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

PHQ_ORDER = mod.PHQ_ORDER



# Manual power computation for independent samples t-test

def compute_power_ttest(d, n1, n2, alpha=0.05):
    """Compute power for two-sample t-test given effect size d, sample sizes, and alpha."""
    # Non-centrality parameter
    se = np.sqrt(1/n1 + 1/n2)
    ncp = d / se
    df = n1 + n2 - 2
    # Critical t-value
    t_crit = stats.t.ppf(1 - alpha/2, df)
    # Power = P(reject H0 | H1 is true)
    power = 1 - stats.nct.cdf(t_crit, df, ncp) + stats.nct.cdf(-t_crit, df, ncp)
    return power

def sample_size_for_power(d, target_power=0.80, alpha=0.05, ratio=1.0):
    """Find per-group n needed for target power (equal or unequal groups)."""
    for n in range(3, 500):
        n2 = max(int(n * ratio), 3)
        power = compute_power_ttest(d, n, n2, alpha)
        if power >= target_power:
            return n, n2, power
    return 500, int(500*ratio), compute_power_ttest(d, 500, int(500*ratio), alpha)

# Reference paper effect sizes
ref_effects = {
    'No Depression vs Moderate-Severe': 1.64,
    'Mild vs Moderate-Severe': 1.22,
    'No Depression vs Mild': 0.37,
}

# Required sample sizes
for name, d in ref_effects.items():
    n, _, power = sample_size_for_power(d, target_power=0.80)

# Our study's actual power
n_minimal = len(df[df['phq_group'] == 'Minimal (0-4)'])
n_moderate = len(df[df['phq_group'] == 'Moderate-Severe (≥10)'])
n_mild = len(df[df['phq_group'] == 'Mild (5-9)'])

# Our observed effect sizes
df_min = df[df['phq_group'] == 'Minimal (0-4)']['avg_speed'].dropna()
df_mod = df[df['phq_group'] == 'Moderate-Severe (≥10)']['avg_speed'].dropna()
if len(df_min) > 0 and len(df_mod) > 0:
    pooled_sd = np.sqrt((df_min.std()**2 + df_mod.std()**2) / 2)
    d_observed = (df_min.mean() - df_mod.mean()) / pooled_sd if pooled_sd > 0 else 0
    power_observed = compute_power_ttest(abs(d_observed), n_minimal, n_moderate)

# Power to detect reference effects with our sample sizes
for name, d in ref_effects.items():
    if 'Mild vs Moderate' in name:
        power = compute_power_ttest(d, n_mild, n_moderate)
    elif 'No Depression vs Moderate' in name:
        power = compute_power_ttest(d, n_minimal, n_moderate)
    else:
        power = compute_power_ttest(d, n_minimal, n_mild)

# FIGURE 20: Power Curves
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Panel A: Power as function of sample size (for different effect sizes)
ax = axes[0]
n_range = np.arange(5, 80)
colors = ['#4e79a7', '#e15759', '#59a14f', '#edc948']
effect_sizes = [0.3, 0.5, 0.8, 1.2, 1.6]
for i, d in enumerate(effect_sizes):
    powers = [compute_power_ttest(d, n, n) for n in n_range]
    color = plt.cm.viridis(i / len(effect_sizes))
    ax.plot(n_range, powers, lw=2.5, label=f'd = {d}', color=color)

ax.axhline(0.80, color='red', ls='--', lw=1.5, alpha=0.7, label='Target power = .80')
ax.axvline(n_minimal, color='gray', ls=':', lw=1.5, alpha=0.7, label=f'Our n (Minimal) = {n_minimal}')
ax.axvline(n_moderate, color='orange', ls=':', lw=1.5, alpha=0.7, label=f'Our n (Mod-Sev) = {n_moderate}')
ax.set_xlabel('Sample Size Per Group', fontsize=11)
ax.set_ylabel('Statistical Power', fontsize=11)
ax.set_title('(a) Power by Sample Size & Effect Size', fontweight='bold')
ax.legend(fontsize=8, loc='lower right')
ax.set_ylim(0, 1.05)
ax.grid(True, alpha=0.3)

# Panel B: Power for our study at different effect sizes
ax = axes[1]
d_range = np.linspace(0.1, 2.5, 100)
power_our = [compute_power_ttest(d, n_minimal, n_moderate) for d in d_range]
power_ref_n = [compute_power_ttest(d, 30, 20) for d in d_range]  # approx ref paper sizes

ax.plot(d_range, power_our, lw=2.5, color='#e15759',
        label=f'Our study (n1={n_minimal}, n2={n_moderate})')
ax.plot(d_range, power_ref_n, lw=2.5, color='#4e79a7',
        label='Reference paper (~n1=30, n2=20)')
ax.axhline(0.80, color='red', ls='--', lw=1.5, alpha=0.7, label='Target power = .80')

# Mark reference effect sizes
for name, d in ref_effects.items():
    ax.axvline(d, color='gray', ls=':', alpha=0.4)
    ax.text(d, 0.02, f'd={d}', ha='center', fontsize=8, rotation=90, color='gray')

ax.set_xlabel("Cohen's d (Effect Size)", fontsize=11)
ax.set_ylabel('Statistical Power', fontsize=11)
ax.set_title('(b) Power Comparison: Our Study vs Reference', fontweight='bold')
ax.legend(fontsize=9)
ax.set_ylim(0, 1.05)
ax.grid(True, alpha=0.3)

fig.suptitle('Figure 20: Statistical Power Analysis\n'
             '(Our study is underpowered for detecting moderate effects due to small Mod-Severe group)',
             fontweight='bold', fontsize=12, y=1.04)
plt.tight_layout()
plt.savefig(f'{OUT}/fig20_power_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
