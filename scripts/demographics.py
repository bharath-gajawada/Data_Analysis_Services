"""Figure 1: Demographics — Age, Gender, VR Experience."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import matplotlib.pyplot as plt

gender_map = {1: 'Male', 2: 'Female'}
vr_map = {1: 'No prior VR', 2: 'Some VR exp.'}

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# Age
import seaborn as sns
sns.histplot(df['age'], bins=range(18, 30), kde=False, color='#4e79a7', ax=axes[0])
axes[0].set_title('Age Distribution'); axes[0].set_xlabel('Age'); axes[0].set_ylabel('Count')

# Gender
gc = df['gender'].map(gender_map).value_counts()
axes[1].bar(gc.index, gc.values, color=['#4e79a7', '#e15759'])
for i, v in enumerate(gc.values): axes[1].text(i, v+0.3, str(v), ha='center', fontweight='bold')
axes[1].set_title('Gender'); axes[1].set_ylabel('Count')

# VR exp
vc = df['vr_experience'].map(vr_map).value_counts()
axes[2].bar(vc.index, vc.values, color=['#76b7b2', '#f28e2b'])
for i, v in enumerate(vc.values): axes[2].text(i, v+0.3, str(v), ha='center', fontweight='bold')
axes[2].set_title('VR Experience'); axes[2].set_ylabel('Count')

fig.suptitle('Figure 1: Participant Demographics (N = 40)', fontweight='bold', y=1.02)
plt.tight_layout(); plt.savefig(f'{OUT}/fig1_demographics.png'); plt.close()

