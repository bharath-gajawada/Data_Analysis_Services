"""Figure 6: Valence, Arousal & Presence per Video (Why Different Videos?)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import numpy as np
import matplotlib.pyplot as plt
from importlib.machinery import SourceFileLoader
mod = SourceFileLoader('ld', os.path.join(os.path.dirname(__file__), '01_load_data.py')).load_module()
VIDEOS = mod.VIDEOS
VIDEO_NAMES = mod.VIDEO_NAMES

x = np.arange(5)
xlbl = [VIDEO_NAMES[v] for v in VIDEOS]
val_m = [df[f'valence_{v}'].mean() for v in VIDEOS]
val_s = [df[f'valence_{v}'].std() for v in VIDEOS]
aro_m = [df[f'arousal_{v}'].mean() for v in VIDEOS]
aro_s = [df[f'arousal_{v}'].std() for v in VIDEOS]
imm_m = [df[f'immersion_{v}'].mean() for v in VIDEOS]
imm_s = [df[f'immersion_{v}'].std() for v in VIDEOS]

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

axes[0].bar(x, val_m, yerr=val_s, capsize=4, color='#59a14f', alpha=0.85)
axes[0].axhline(5, color='gray', ls=':', alpha=0.6, label='Neutral (5)')
axes[0].set_xticks(x); axes[0].set_xticklabels(xlbl, fontsize=7)
axes[0].set_ylabel('Valence (1-9)'); axes[0].set_title('Valence'); axes[0].legend(fontsize=8)

axes[1].bar(x, aro_m, yerr=aro_s, capsize=4, color='#edc948', alpha=0.85)
axes[1].axhline(5, color='gray', ls=':', alpha=0.6, label='Neutral (5)')
axes[1].set_xticks(x); axes[1].set_xticklabels(xlbl, fontsize=7)
axes[1].set_ylabel('Arousal (1-9)'); axes[1].set_title('Arousal'); axes[1].legend(fontsize=8)

axes[2].bar(x, imm_m, yerr=imm_s, capsize=4, color='#b07aa1', alpha=0.85)
axes[2].set_xticks(x); axes[2].set_xticklabels(xlbl, fontsize=7)
axes[2].set_ylabel('Presence Score'); axes[2].set_title('Presence')

fig.suptitle('Figure 6: Why Different Videos? — Valence, Arousal & Presence Across Emotional Conditions',
             fontweight='bold', y=1.03)
plt.tight_layout(); plt.savefig(f'{OUT}/fig6_valence_arousal_presence.png'); plt.close()

