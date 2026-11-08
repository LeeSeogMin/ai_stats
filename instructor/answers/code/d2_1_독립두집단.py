"""2회차 1교시 독립된 두 집단 비교: 독거 대 동거 어르신 (정답 예시)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("data/욕구조사.csv")
items = [f"디지털역량_Q{i}" for i in range(1, 6)]
df["디지털역량"] = df[items].replace(9, np.nan).mean(axis=1)
df["독거여부"] = np.where(df["가구형태"] == "독거", "독거", "동거(부부·자녀)")

print("[평균 비교] 디지털 역량 점수(1~5점)")
g = df.groupby("독거여부")["디지털역량"].agg(["count", "mean", "std"]).round(2)
print(g.to_string())
a = df.loc[df["독거여부"] == "독거", "디지털역량"]
b = df.loc[df["독거여부"] != "독거", "디지털역량"]
t = stats.ttest_ind(a, b, equal_var=False)
print(f"평균 차이(독거 - 동거): {a.mean() - b.mean():.2f}점")
print(f"독립표본 t검정(Welch): t = {t.statistic:.2f}, p값 = {t.pvalue:.4f}")
print("\n가구형태 3분류 평균:")
print(df.groupby("가구형태")["디지털역량"].agg(["count", "mean"]).round(2).to_string())

print("\n[비율 비교] 교육 참여 의향 (분모 = 각 행의 인원)")
ct = pd.crosstab(df["독거여부"], df["교육참여의향"])
print(ct.to_string())
print((pd.crosstab(df["독거여부"], df["교육참여의향"], normalize="index") * 100).round(1).to_string())
chi2, p, dof, _ = stats.chi2_contingency(ct)
print(f"카이제곱 검정: 카이제곱 = {chi2:.2f}, 자유도 {dof}, p값 = {p:.4f}")

fig, ax = plt.subplots(figsize=(5, 3.5))
ax.bar(g.index, g["mean"], color=["#DD8452", "#4C72B0"])
for i, (n, mu) in enumerate(zip(g["count"], g["mean"])):
    ax.text(i, mu + 0.04, f"{mu:.2f}점 ({n}명)", ha="center")
ax.set_ylim(1, 4)
ax.set_ylabel("디지털 역량 평균(1~5점)")
ax.set_title("가구형태별 디지털 역량")
fig.tight_layout()
fig.savefig("instructor/answers/results/독거_동거_역량.png", dpi=150)
