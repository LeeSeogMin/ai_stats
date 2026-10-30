"""2회차 2교시 ② 설문 교차표: 프로그램 참여와 재이용 의향 (정답 예시)."""
import pandas as pd
from scipy import stats

df = pd.read_csv("data/만족도조사.csv")
print(f"분석 대상: {len(df)}명 (재이용의향은 빈칸 없음)")
tab = pd.crosstab(df["프로그램참여"], df["재이용의향"], margins=True, margins_name="합계")
print("\n인원:")
print(tab.to_string())
row_pct = pd.crosstab(df["프로그램참여"], df["재이용의향"], normalize="index") * 100
print("\n행 비율(%) — 분모는 각 행(참여자 전체, 미참여자 전체):")
print(row_pct.round(1).to_string())
col_pct = pd.crosstab(df["프로그램참여"], df["재이용의향"], normalize="columns") * 100
print("\n열 비율(%) — 분모는 각 열(「예」라고 답한 사람 전체 등):")
print(col_pct.round(1).to_string())
chi2, p, _, _ = stats.chi2_contingency(pd.crosstab(df["프로그램참여"], df["재이용의향"]))
print(f"\n카이제곱 검정 p값: {p:.4f}")
