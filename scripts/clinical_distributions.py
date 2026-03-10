"""Figure 2: PHQ-9 & GAD-7 Distributions with Clinical Cutoffs."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# PHQ-9
sns.histplot(df['score_phq'], bins=range(0, 28), kde=True, color='#4e79a7', ax=axes[0])
axes[0].axvline(4.5, color='green', ls='--', lw=1.5, label='Minimal/Mild cutoff (5)')
axes[0].axvline(9.5, color='orange', ls='--', lw=1.5, label='Mild/Moderate cutoff (10)')
axes[0].axvline(14.5, color='red', ls='--', lw=1.5, label='Moderate/Severe cutoff (15)')
axes[0].set_title('PHQ-9 (Depression) Score Distribution')
axes[0].set_xlabel('PHQ-9 Score (0-27)'); axes[0].legend(fontsize=8)

# GAD-7
sns.histplot(df['score_gad'], bins=range(0, 22), kde=True, color='#e15759', ax=axes[1])
axes[1].axvline(4.5, color='green', ls='--', lw=1.5, label='Minimal/Mild cutoff (5)')
axes[1].axvline(9.5, color='orange', ls='--', lw=1.5, label='Mild/Moderate cutoff (10)')
axes[1].axvline(14.5, color='red', ls='--', lw=1.5, label='Moderate/Severe cutoff (15)')
axes[1].set_title('GAD-7 (Anxiety) Score Distribution')
axes[1].set_xlabel('GAD-7 Score (0-21)'); axes[1].legend(fontsize=8)

fig.suptitle('Figure 2: Clinical Score Distributions with Standard Cutoffs', fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig(f'{OUT}/fig2_clinical_distributions.png'); plt.close()

