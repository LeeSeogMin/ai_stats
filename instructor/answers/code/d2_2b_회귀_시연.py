"""2회차 2교시 선택 시연: 회귀분석으로 여러 요인을 함께 보기 (강사 시연용)."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("data/욕구조사.csv")
df["디지털역량"] = df[[f"디지털역량_Q{i}" for i in range(1, 6)]].replace(9, np.nan).mean(axis=1)
df["독거"] = (df["가구형태"] == "독거").astype(int)

m1 = smf.ols("디지털역량 ~ 독거", data=df).fit()
print(f"[독거만 넣음] 독거의 차이 {m1.params['독거']:.2f}점, p값 {m1.pvalues['독거']:.4f}")

m2 = smf.ols("디지털역량 ~ 독거 + 연령 + C(교육수준, Treatment('초졸 이하')) + C(스마트폰보유)", data=df).fit()
print(f"\n[연령·교육수준·스마트폰 보유를 함께 넣음] 분석 대상 {int(m2.nobs)}명, 설명력(R제곱) {m2.rsquared:.2f}")
print(pd.DataFrame({"계수": m2.params.round(3), "p값": [f"{v:.4f}" if v >= 0.001 else "<0.001" for v in m2.pvalues]}).to_string())
print(f"\n연령 1세 많을 때 역량 변화: {m2.params['연령']:.3f}점 (10세면 {m2.params['연령'] * 10:.2f}점)")
