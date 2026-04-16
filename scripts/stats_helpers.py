"""Shared statistical helpers for assumption checks and adaptive test selection."""

from math import sqrt

import numpy as np
from scipy import stats


def clean_pair(a, b):
    paired = [(x, y) for x, y in zip(a, b) if np.isfinite(x) and np.isfinite(y)]
    if not paired:
        return np.array([]), np.array([])
    x, y = zip(*paired)
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def shapiro_safe(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 3:
        return np.nan
    if len(values) > 5000:
        values = values[:5000]
    return stats.shapiro(values).pvalue


def fisher_r_ci(r, n, alpha=0.05):
    if n < 4 or not np.isfinite(r):
        return (np.nan, np.nan)
    r = np.clip(r, -0.999999, 0.999999)
    z = np.arctanh(r)
    se = 1 / sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - alpha / 2)
    return tuple(np.tanh([z - z_crit * se, z + z_crit * se]))


def mean_diff_ci(a, b, alpha=0.05, paired=False):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if paired:
        diff = a - b
        diff = diff[np.isfinite(diff)]
        n = len(diff)
        if n < 2:
            return np.nan, np.nan, np.nan
        mean_diff = diff.mean()
        sem = stats.sem(diff, nan_policy='omit')
        if not np.isfinite(sem):
            return mean_diff, np.nan, np.nan
        tcrit = stats.t.ppf(1 - alpha / 2, df=n - 1)
        return mean_diff, mean_diff - tcrit * sem, mean_diff + tcrit * sem

    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return np.nan, np.nan, np.nan
    mean_diff = a.mean() - b.mean()
    se = sqrt(a.var(ddof=1) / n1 + b.var(ddof=1) / n2)
    if not np.isfinite(se) or se == 0:
        return mean_diff, mean_diff, mean_diff
    df_num = (a.var(ddof=1) / n1 + b.var(ddof=1) / n2) ** 2
    df_den = 0
    if n1 > 1:
        df_den += (a.var(ddof=1) / n1) ** 2 / (n1 - 1)
    if n2 > 1:
        df_den += (b.var(ddof=1) / n2) ** 2 / (n2 - 1)
    df = df_num / df_den if df_den > 0 else min(n1, n2) - 1
    tcrit = stats.t.ppf(1 - alpha / 2, df=df)
    return mean_diff, mean_diff - tcrit * se, mean_diff + tcrit * se


def benjamini_hochberg(p_values):
    p_values = np.asarray(p_values, dtype=float)
    corrected = np.full_like(p_values, np.nan, dtype=float)
    finite_idx = np.where(np.isfinite(p_values))[0]
    if len(finite_idx) == 0:
        return corrected
    ordered = finite_idx[np.argsort(p_values[finite_idx])]
    m = len(ordered)
    prev = 1.0
    for rank, idx in enumerate(ordered[::-1], start=1):
        q = p_values[idx] * m / (m - rank + 1)
        prev = min(prev, q)
        corrected[idx] = prev
    return corrected


def adaptive_two_group_test(a, b, alpha=0.05):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return {"test": "insufficient", "stat": np.nan, "p": np.nan, "ci": (np.nan, np.nan), "normal": (np.nan, np.nan), "note": "too few observations"}

    p_a = shapiro_safe(a)
    p_b = shapiro_safe(b)
    normal = (p_a >= alpha if np.isfinite(p_a) else False, p_b >= alpha if np.isfinite(p_b) else False)
    levene_p = stats.levene(a, b, center='median').pvalue if len(a) >= 2 and len(b) >= 2 else np.nan

    if normal[0] and normal[1]:
        stat, p = stats.ttest_ind(a, b, equal_var=not (np.isfinite(levene_p) and levene_p < alpha))
        ci = mean_diff_ci(a, b, alpha=alpha, paired=False)[1:]
        return {"test": "welch_t" if np.isfinite(levene_p) and levene_p < alpha else "student_t", "stat": stat, "p": p, "ci": ci, "normal": (p_a, p_b), "levene_p": levene_p}

    stat, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    return {"test": "mannwhitney", "stat": stat, "p": p, "ci": (np.nan, np.nan), "normal": (p_a, p_b), "levene_p": levene_p}


def adaptive_paired_test(a, b, alpha=0.05):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    a = a[mask]
    b = b[mask]
    if len(a) < 2:
        return {"test": "insufficient", "stat": np.nan, "p": np.nan, "ci": (np.nan, np.nan), "normal": np.nan}

    diff = a - b
    p_diff = shapiro_safe(diff)
    if np.isfinite(p_diff) and p_diff >= alpha:
        stat, p = stats.ttest_rel(a, b)
        _, ci_low, ci_high = mean_diff_ci(a, b, alpha=alpha, paired=True)
        return {"test": "paired_t", "stat": stat, "p": p, "ci": (ci_low, ci_high), "normal": p_diff}

    stat, p = stats.wilcoxon(a, b, zero_method='wilcox', alternative='two-sided', mode='auto')
    return {"test": "wilcoxon", "stat": stat, "p": p, "ci": (np.nan, np.nan), "normal": p_diff}


def adaptive_correlation(a, b, alpha=0.05):
    a, b = clean_pair(a, b)
    if len(a) < 3:
        return {"test": "insufficient", "stat": np.nan, "p": np.nan, "ci": (np.nan, np.nan), "normal": (np.nan, np.nan)}

    p_a = shapiro_safe(a)
    p_b = shapiro_safe(b)
    if (np.isfinite(p_a) and p_a >= alpha) and (np.isfinite(p_b) and p_b >= alpha):
        r, p = stats.pearsonr(a, b)
        return {"test": "pearson", "stat": r, "p": p, "ci": fisher_r_ci(r, len(a), alpha=alpha), "normal": (p_a, p_b)}

    rho, p = stats.spearmanr(a, b)
    return {"test": "spearman", "stat": rho, "p": p, "ci": (np.nan, np.nan), "normal": (p_a, p_b)}