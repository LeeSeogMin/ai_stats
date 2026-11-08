"""1회차 4교시 욕구조사: 자료 정리, 빈도분석, 기술통계 (정답 예시)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("data/욕구조사.csv")
items = [f"디지털역량_Q{i}" for i in range(1, 6)]
print(f"응답자: {len(df)}명")

print("\n[자료 정리] 무응답 코드 9의 개수(문항별):")
print((df[items] == 9).sum().to_string())
x = df[items].replace(9, np.nan)
df["디지털역량"] = x.mean(axis=1)          # 응답한 문항의 평균(1~5점)
print(f"무응답이 하나라도 있는 응답자: {x.isna().any(axis=1).sum()}명 (역량 점수는 응답한 문항의 평균으로 계산)")
print("9를 그대로 두고 계산한 Q1 평균(틀린 값): "
      f"{df['디지털역량_Q1'].mean():.2f} / 9를 뺀 평균: {x['디지털역량_Q1'].mean():.2f}")

print("\n[빈도분석] 분모 = 응답자 300명")
for col in ["성별", "연령대", "가구형태", "교육수준", "스마트폰보유", "가장어려운기능", "교육참여의향"]:
    order = {"연령대": ["65~69세", "70~74세", "75~79세", "80세 이상"], "교육수준": ["초졸 이하", "중졸", "고졸 이상"]}
    t = df[col].value_counts()
    if col in order:
        t = t.reindex(order[col])
    print(f"\n{col}:")
    print(pd.DataFrame({"인원": t, "비율(%)": (t / len(df) * 100).round(1)}).to_string())

print("\n[문항별 기술통계] 무응답 제외")
desc = x.agg(["count", "mean", "median", "std"]).T.round(2)
desc.columns = ["응답 수", "평균", "중앙값", "표준편차"]
print(desc.to_string())

s = df["디지털역량"]
print(f"\n디지털 역량 점수(5문항 평균): 평균 {s.mean():.2f}, 중앙값 {s.median():.2f}, "
      f"표준편차 {s.std():.2f}, 최솟값 {s.min():.1f}, 최댓값 {s.max():.1f}")
low = (s < 2.5).sum()
print(f"2.5점 미만(대체로 「못 한다」 쪽): {low}명, {low / len(df) * 100:.1f}%")
print(f"연령: 평균 {df['연령'].mean():.1f}세, 중앙값 {df['연령'].median():.0f}세")

fig, ax = plt.subplots(figsize=(6, 3.5))
m = x.mean()
labels = ["Q1 전화·문자", "Q2 사진", "Q3 카카오톡", "Q4 키오스크", "Q5 뱅킹"]
ax.barh(labels[::-1], m.values[::-1], color="#4C72B0")
for i, v in enumerate(m.values[::-1]):
    ax.text(v + 0.03, i, f"{v:.2f}", va="center")
ax.set_xlim(1, 5)
ax.set_xlabel("평균(1=전혀 못 한다 ~ 5=혼자 잘 한다)")
ax.set_title(f"디지털 역량 문항별 평균 (응답자 {len(df)}명, 무응답 제외)")
fig.tight_layout()
fig.savefig("instructor/answers/results/문항별_평균.png", dpi=150)
