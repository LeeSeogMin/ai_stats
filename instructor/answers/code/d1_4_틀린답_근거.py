"""1회차 4교시 틀린 AI 답 5개에 쓰는 숫자(틀린 값과 바른 값)를 실제로 계산한다 (강사용)."""
import pandas as pd

s = pd.read_csv("data/만족도조사.csv")
x = s["만족도_전반"]
low = int(x.isin([1, 2]).sum())
print("[1 분모 오류]")
print(f"  1~2점 응답 {low}명 / 전체 {len(s)}명 = {low / len(s) * 100:.1f}%  (틀린 분모)")
print(f"  1~2점 응답 {low}명 / 응답 {x.notna().sum()}명 = {low / x.notna().sum() * 100:.1f}%  (바른 분모)")

w = pd.read_csv("data/채용공고_월급.csv")["월급_만원"]
print("[2 평균만 보고 결론]")
print(f"  평균 {w.mean():.1f}, 중앙값 {w.median():.1f}, 평균 이상 공고 비율 {(w >= w.mean()).mean() * 100:.1f}%")

print("[3 결측을 0점으로 처리]")
print(f"  빈칸을 0점으로 넣은 평균 {x.fillna(0).mean():.2f} / 빈칸을 뺀 평균 {x.mean():.2f}")

print("[4 상관을 인과로]")
print(f"  이용기간과 만족도 상관계수 {s['이용기간_개월'].corr(x):.2f}")

r = pd.read_csv("instructor/answers/results/이용자명부_정리.csv")
print("[5 표본 수 누락] 정리한 명부의 프로그램별 만족도")
print(r.groupby("프로그램")["만족도"].agg(["count", "mean"]).round(2).to_string())
