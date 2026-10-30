"""1회차 3교시 평균 월급 300만 원 공고를 믿어도 되는가 (정답 예시)."""
import matplotlib.pyplot as plt
import pandas as pd

hand = [230, 240, 250, 260, 1000]
s = sorted(hand)
print(f"[손 계산 예] 월급 {hand}: 평균 {sum(hand) / len(hand):.0f}, 중앙값 {s[2]}")

df = pd.read_csv("data/채용공고_월급.csv")
w = df["월급_만원"]
print(f"\n공고 수: {len(df)}건")
print(f"평균: {w.mean():.1f}만 원")
print(f"중앙값: {w.median():.1f}만 원")
print(f"최솟값 {w.min()}, 최댓값 {w.max()}")
high = w >= 600
print(f"600만 원 이상 공고: {high.sum()}건 (직무: {', '.join(df.loc[high, '직무'].unique())})")
print(f"600만 원 이상을 뺀 평균: {w[~high].mean():.1f}만 원 ({(~high).sum()}건)")
print(f"평균 이상을 받는 공고 비율: {(w >= w.mean()).mean() * 100:.1f}%")
print("\n직무별 중앙값(만 원):")
print(df.groupby("직무")["월급_만원"].agg(["count", "median"]).to_string())

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(w, bins=30, color="#4C72B0")
ax.axvline(w.mean(), color="red", linestyle="--", label=f"평균 {w.mean():.0f}")
ax.axvline(w.median(), color="green", linestyle="-", label=f"중앙값 {w.median():.0f}")
ax.set_xlabel("월급(만 원)")
ax.set_ylabel("공고 수(건)")
ax.set_title(f"채용공고 월급 분포 ({len(df)}건)")
ax.legend()
fig.tight_layout()
fig.savefig("instructor/answers/results/월급_분포.png", dpi=150)
