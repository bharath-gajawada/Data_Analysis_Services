"""Figures 7, 8, 9: Headtracking Speed by Depression/Distress Groups."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_data_helper import load_and_setup
df, OUT = load_and_setup()

import matplotlib.pyplot as plt
import seaborn as sns
from importlib.machinery import SourceFileLoader
mod = SourceFileLoader('ld', os.path.join(os.path.dirname(__file__), '01_load_data.py')).load_module()
VIDEOS = mod.VIDEOS
VIDEO_NAMES = mod.VIDEO_NAMES
PHQ_ORDER = mod.PHQ_ORDER

# ── Figure 7: Total Speed by PHQ-9 Group ─────────────────────────────────
speed_cols = [f'speed_total_{v}' for v in VIDEOS]
df_long = df.melt(id_vars=['participant', 'phq_group'], value_vars=speed_cols,
                  var_name='video', value_name='speed')
df_long = df_long.dropna(subset=['speed'])
df_long['vlabel'] = df_long['video'].map({f'speed_total_{v}': VIDEO_NAMES[v] for v in VIDEOS})

fig, ax = plt.subplots(figsize=(13, 6))
sns.boxplot(data=df_long, x='vlabel', y='speed', hue='phq_group',
            hue_order=PHQ_ORDER, palette=['#59a14f', '#edc948', '#e15759'], ax=ax)
ax.set_xlabel('Video'); ax.set_ylabel('Mean Rotational Speed (°/s)')
ax.set_title('Figure 7: Headtracking Speed by Video × PHQ-9 Depression Group', fontweight='bold')
ax.legend(title='PHQ-9 Group')
plt.tight_layout(); plt.savefig(f'{OUT}/fig7_ht_speed_phq_groups.png'); plt.close()

# ── Figure 8: Yaw Speed by PHQ-9 Group ───────────────────────────────────
yaw_cols = [f'speed_y_{v}' for v in VIDEOS]
df_yaw = df.melt(id_vars=['participant', 'phq_group'], value_vars=yaw_cols,
                 var_name='video', value_name='yaw_speed')
df_yaw = df_yaw.dropna(subset=['yaw_speed'])
df_yaw['vlabel'] = df_yaw['video'].map({f'speed_y_{v}': VIDEO_NAMES[v] for v in VIDEOS})

fig, ax = plt.subplots(figsize=(13, 6))
sns.boxplot(data=df_yaw, x='vlabel', y='yaw_speed', hue='phq_group',
            hue_order=PHQ_ORDER, palette=['#59a14f', '#edc948', '#e15759'], ax=ax)
ax.set_xlabel('Video'); ax.set_ylabel('Mean Yaw Speed (°/s)')
ax.set_title('Figure 8: Yaw (Horizontal Scanning) Speed by Depression Group\n'
             '(Key metric from Srivastava & Lahane, 2025)', fontweight='bold')
ax.legend(title='PHQ-9 Group')
plt.tight_layout(); plt.savefig(f'{OUT}/fig8_yaw_speed_phq.png'); plt.close()

# ── Figure 9: Speed by Distress Group ────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
distress_order = ['None', 'Both Mild (BMD)', 'Either Distress\n(Dep only)',
                  'Either Distress\n(Anx only)', 'Both Distress (BD)']
existing = [d for d in distress_order if d in df['distress'].values]
df_dist = df[df['distress'].isin(existing)]
sns.boxplot(data=df_dist, x='distress', y='avg_speed', order=existing,
            palette='RdYlGn_r', ax=ax)
ax.set_xlabel('Distress Group (PHQ-9 × GAD-7)')
ax.set_ylabel('Avg. Rotational Speed (°/s)')
ax.set_title('Figure 9: Headtracking Speed by Co-occurring Distress Group', fontweight='bold')
plt.tight_layout(); plt.savefig(f'{OUT}/fig9_distress_groups.png'); plt.close()
