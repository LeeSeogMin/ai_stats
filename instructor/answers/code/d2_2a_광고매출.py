"""2회차 2교시 ① 광고비를 늘린 달에 매출이 올랐다. 광고 덕분인가 (정답 예시)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("data/가게_월별매출.csv")
print(f"분석 기간: {df['연월'].iloc[0]} ~ {df['연월'].iloc[-1]} ({len(df)}개월)")
print(f"광고비와 매출의 상관계수: {df['광고비_만원'].corr(df['매출_만원']):.2f}")

m1 = smf.ols("매출_만원 ~ 광고비_만원", data=df).fit()
print(f"\n[성수기 고려 안 함] 광고비 1만 원당 매출 변화: {m1.params['광고비_만원']:.2f}만 원")
m2 = smf.ols("매출_만원 ~ 광고비_만원 + C(성수기)", data=df).fit()
print(f"[성수기 고려] 광고비 1만 원당 매출 변화: {m2.params['광고비_만원']:.2f}만 원, p값 {m2.pvalues['광고비_만원']:.3f}")
print(f"[성수기 고려] 성수기 달의 매출 차이: {m2.params['C(성수기)[T.예]']:.0f}만 원")
print("\n성수기 여부별 평균:")
print(df.groupby("성수기")[["광고비_만원", "매출_만원"]].mean().round(0).to_string())

fig, ax = plt.subplots(figsize=(6, 4))
for k, c in [("아니오", "#999999"), ("예", "#DD8452")]:
    s = df[df["성수기"] == k]
    ax.scatter(s["광고비_만원"], s["매출_만원"], color=c, label=f"성수기 {k}")
xs = np.linspace(df["광고비_만원"].min(), df["광고비_만원"].max(), 50)
ax.plot(xs, m1.params["Intercept"] + m1.params["광고비_만원"] * xs, color="black", linestyle="--", label="전체 회귀선")
ax.set_xlabel("광고비(만 원)")
ax.set_ylabel("매출(만 원)")
ax.set_title("월별 광고비와 매출 (36개월)")
ax.legend()
fig.tight_layout()
fig.savefig("instructor/answers/results/광고비_매출.png", dpi=150)
