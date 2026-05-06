"""
Report 2 — Figures 15 & 16: Linear Regression Analysis
PHQ-9 as continuous predictor of scanning speed, with regression diagnostics.
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

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("WARNING: statsmodels not installed.")

if HAS_STATSMODELS:
    reg_df = df[['avg_speed', 'avg_speed_y', 'score_phq', 'score_gad', 'score_stai_t']].dropna()

    # Model 1: Simple regression
    model1 = ols('avg_speed ~ score_phq', data=reg_df).fit()

    # Model 2: Multiple regression
    model2 = ols('avg_speed ~ score_phq + score_gad', data=reg_df).fit()

    # Model 3: Full model
    model3 = ols('avg_speed ~ score_phq + score_gad + score_stai_t', data=reg_df).fit()

    # Model 4: Yaw Speed
    model4 = ols('avg_speed_y ~ score_phq + score_gad', data=reg_df).fit()

    # VIF (Multicollinearity)
    X = reg_df[['score_phq', 'score_gad', 'score_stai_t']]
    X_const = sm.add_constant(X)
    vif_data = pd.DataFrame()
    vif_data['Variable'] = X.columns
    vif_data['VIF'] = [variance_inflation_factor(X_const.values, i+1) for i in range(len(X.columns))]

    # FIGURE 15: Regression Scatter
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: PHQ-9 vs Total Speed
    ax = axes[0]
    scatter = ax.scatter(reg_df['score_phq'], reg_df['avg_speed'],
                         c=reg_df['score_gad'], cmap='RdYlGn_r',
                         s=70, edgecolors='black', linewidth=0.5, alpha=0.8)
    # Regression line with CI
    x_pred = np.linspace(reg_df['score_phq'].min()-1, reg_df['score_phq'].max()+1, 100)
    pred_df = pd.DataFrame({'score_phq': x_pred,
                            'score_gad': [reg_df['score_gad'].mean()] * 100})
    y_pred = model2.predict(pred_df)
    ax.plot(x_pred, y_pred, 'r-', lw=2, label=f'Regression (β={model2.params["score_phq"]:.2f})')
    # CI band from model
    pred_res = model2.get_prediction(pred_df)
    ci = pred_res.conf_int(alpha=0.05)
    ax.fill_between(x_pred, ci[:, 0], ci[:, 1], alpha=0.15, color='red')
    r, p = stats.pearsonr(reg_df['score_phq'], reg_df['avg_speed'])
    ax.set_xlabel('PHQ-9 Score')
    ax.set_ylabel('Average Scan Speed (°/s)')
    ax.set_title(f'PHQ-9 vs Total Scan Speed\nr={r:.3f}, p={p:.3f}, R²={model2.rsquared:.3f}',
                 fontweight='bold')
    ax.legend(fontsize=9)
    plt.colorbar(scatter, ax=ax, label='GAD-7 Score')

    # Panel B: PHQ-9 vs Yaw Speed
    ax = axes[1]
    scatter2 = ax.scatter(reg_df['score_phq'], reg_df['avg_speed_y'],
                          c=reg_df['score_gad'], cmap='RdYlGn_r',
                          s=70, edgecolors='black', linewidth=0.5, alpha=0.8)
    pred_df_y = pd.DataFrame({'score_phq': x_pred,
                              'score_gad': [reg_df['score_gad'].mean()] * 100})
    y_pred_y = model4.predict(pred_df_y)
    ax.plot(x_pred, y_pred_y, 'r-', lw=2, label=f'Regression (β={model4.params["score_phq"]:.2f})')
    pred_res_y = model4.get_prediction(pred_df_y)
    ci_y = pred_res_y.conf_int(alpha=0.05)
    ax.fill_between(x_pred, ci_y[:, 0], ci_y[:, 1], alpha=0.15, color='red')
    r_y, p_y = stats.pearsonr(reg_df['score_phq'], reg_df['avg_speed_y'])
    ax.set_xlabel('PHQ-9 Score')
    ax.set_ylabel('Average Yaw Speed (°/s)')
    ax.set_title(f'PHQ-9 vs Yaw Speed\nr={r_y:.3f}, p={p_y:.3f}, R²={model4.rsquared:.3f}',
                 fontweight='bold')
    ax.legend(fontsize=9)
    plt.colorbar(scatter2, ax=ax, label='GAD-7 Score')

    fig.suptitle('Figure 15: Linear Regression — PHQ-9 as Continuous Predictor of Scanning Speed\n'
                 '(Color = GAD-7 score; shaded = 95% CI; controlling for anxiety)',
                 fontweight='bold', fontsize=12, y=1.04)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig15_regression_scatter.png', dpi=150, bbox_inches='tight')
    plt.close()


    # FIGURE 16: Regression Diagnostic Plots (Model 2)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    residuals = model2.resid
    fitted = model2.fittedvalues
    std_resid = model2.get_influence().resid_studentized_internal

    # (a) Residuals vs Fitted
    ax = axes[0, 0]
    ax.scatter(fitted, residuals, alpha=0.7, edgecolors='black', linewidth=0.5, color='#4e79a7')
    ax.axhline(0, color='red', ls='--', lw=1.5)
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('Residuals')
    ax.set_title('(a) Residuals vs Fitted\n(Check: homoscedasticity)', fontweight='bold')

    # (b) Q-Q of Residuals
    ax = axes[0, 1]
    stats.probplot(residuals, dist="norm", plot=ax)
    w, p = stats.shapiro(residuals)
    ax.set_title(f'(b) Q-Q of Residuals\nShapiro-Wilk: W={w:.3f}, p={p:.3f}', fontweight='bold')
    ax.get_lines()[0].set_markerfacecolor('#4e79a7')
    ax.get_lines()[1].set_color('#e15759')

    # (c) Scale-Location
    ax = axes[1, 0]
    ax.scatter(fitted, np.sqrt(np.abs(std_resid)), alpha=0.7, edgecolors='black',
               linewidth=0.5, color='#59a14f')
    ax.set_xlabel('Fitted Values')
    ax.set_ylabel('√|Standardized Residuals|')
    ax.set_title('(c) Scale-Location\n(Check: constant variance)', fontweight='bold')

    # (d) Cook's Distance
    ax = axes[1, 1]
    influence = model2.get_influence()
    cooks_d = influence.cooks_distance[0]
    ax.stem(range(len(cooks_d)), cooks_d, linefmt='#e15759', markerfmt='o', basefmt='k-')
    ax.axhline(4/len(cooks_d), color='red', ls='--', lw=1.5, label=f'Threshold (4/n = {4/len(cooks_d):.3f})')
    ax.set_xlabel('Observation Index')
    ax.set_ylabel("Cook's Distance")
    ax.set_title("(d) Cook's Distance\n(Check: influential observations)", fontweight='bold')
    ax.legend(fontsize=8)
    n_influential = (cooks_d > 4/len(cooks_d)).sum()

    fig.suptitle('Figure 16: Regression Diagnostics — Model: Speed ~ PHQ-9 + GAD-7\n'
                 '(Checking linearity, normality of residuals, homoscedasticity, influence)',
                 fontweight='bold', fontsize=12, y=1.03)
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig16_regression_diagnostics.png', dpi=150, bbox_inches='tight')
    plt.close()


    # Breusch-Pagan test for heteroscedasticity
    try:
        from statsmodels.stats.diagnostic import het_breuschpagan
        bp_stat, bp_p, bp_f, bp_fp = het_breuschpagan(model2.resid, model2.model.exog)
    except ImportError:
        pass

else:
    print("Skipping regression — statsmodels not available.")
