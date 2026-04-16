"""Figure 5: PANAS Pre vs Post VR (Mood Change)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import matplotlib.pyplot as plt
from stats_helpers import adaptive_paired_test

fig, axes = plt.subplots(1, 2, figsize=(11, 5))

# Positive Affect
data_pa = [df['positive_affect_start'], df['positive_affect_end']]
bp1 = axes[0].boxplot(data_pa, tick_labels=['Pre-VR', 'Post-VR'], patch_artist=True,
                       boxprops=dict(alpha=0.7))
bp1['boxes'][0].set_facecolor('#4e79a7'); bp1['boxes'][1].set_facecolor('#76b7b2')
pa_result = adaptive_paired_test(df['positive_affect_start'], df['positive_affect_end'])
pa_ci = ''
if all(map(lambda x: x == x, pa_result['ci'])):
    pa_ci = f"\n95% CI [{pa_result['ci'][0]:.2f}, {pa_result['ci'][1]:.2f}]"
axes[0].set_title(f'Positive Affect\n{pa_result["test"]}: stat={pa_result["stat"]:.2f}, p={pa_result["p"]:.3f}{pa_ci}')
axes[0].set_ylabel('Score')

# Negative Affect
data_na = [df['negative_affect_start'], df['negative_affect_end']]
bp2 = axes[1].boxplot(data_na, tick_labels=['Pre-VR', 'Post-VR'], patch_artist=True,
                       boxprops=dict(alpha=0.7))
bp2['boxes'][0].set_facecolor('#e15759'); bp2['boxes'][1].set_facecolor('#f28e2b')
na_result = adaptive_paired_test(df['negative_affect_start'], df['negative_affect_end'])
na_ci = ''
if all(map(lambda x: x == x, na_result['ci'])):
    na_ci = f"\n95% CI [{na_result['ci'][0]:.2f}, {na_result['ci'][1]:.2f}]"
axes[1].set_title(f'Negative Affect\n{na_result["test"]}: stat={na_result["stat"]:.2f}, p={na_result["p"]:.3f}{na_ci}')
axes[1].set_ylabel('Score')

fig.suptitle('Figure 5: PANAS Mood — Before vs. After VR Experience', fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig(f'{OUT}/fig5_panas_pre_post.png'); plt.close()

