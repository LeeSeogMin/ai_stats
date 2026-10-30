"""2회차 1교시 프로그램 효과가 있다고 보고해도 되는가 (정답 예시)."""
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

df = pd.read_csv("data/만족도조사.csv")
d = df.dropna(subset=["만족도_전반"])
print(f"분석 대상: {len(d)}명 (전체 {len(df)}명 중 빈칸 {len(df) - len(d)}명 제외)")
g = d.groupby("프로그램참여")["만족도_전반"].agg(["count", "mean", "median"])
print(g.round(2).to_string())
a = d.loc[d["프로그램참여"] == "참여", "만족도_전반"]
b = d.loc[d["프로그램참여"] == "미참여", "만족도_전반"]
t = stats.ttest_ind(a, b, equal_var=False)
print(f"\n평균 차이(참여 - 미참여): {a.mean() - b.mean():.2f}점")
print(f"t검정(Welch) p값: {t.pvalue:.4f}")

print("\n이용기간(개월) 평균:")
print(d.groupby("프로그램참여")["이용기간_개월"].mean().round(1).to_string())
print(f"이용기간과 만족도의 상관계수: {d['이용기간_개월'].corr(d['만족도_전반']):.2f}")

m = smf.ols("만족도_전반 ~ C(프로그램참여, Treatment('미참여')) + 이용기간_개월", data=d).fit()
coef = m.params.iloc[1]
p = m.pvalues.iloc[1]
print(f"\n이용기간을 함께 고려한 참여자-미참여자 차이: {coef:.2f}점, p값 {p:.4f}")

fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(g.index, g["mean"], color=["#999999", "#4C72B0"])
for i, (n, mu) in enumerate(zip(g["count"], g["mean"])):
    ax.text(i, mu + 0.03, f"{mu:.2f}점\n({n}명)", ha="center")
ax.set_ylim(3, 4.6)
ax.set_ylabel("전반적 만족도 평균")
ax.set_title("프로그램 참여 여부별 만족도")
fig.tight_layout()
fig.savefig("instructor/answers/results/참여별_만족도.png", dpi=150)
