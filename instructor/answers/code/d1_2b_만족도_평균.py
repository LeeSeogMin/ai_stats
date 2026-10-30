"""1회차 2교시 ② 만족도 평균 4.1점은 좋은 점수인가 (정답 예시)."""
import matplotlib.pyplot as plt
import pandas as pd

hand = [5, 5, 4, 4, 1]
print(f"[손 계산 예] 점수 {hand}: 평균 {sum(hand) / len(hand):.1f}, 중앙값 {sorted(hand)[2]}")

df = pd.read_csv("data/만족도조사.csv")
x = df["만족도_전반"]
print(f"\n전체 응답자: {len(df)}명, 응답한 사람: {x.notna().sum()}명, 빈칸(결측): {x.isna().sum()}명")
print(f"평균: {x.mean():.2f}점 (분모 = 응답한 {x.notna().sum()}명)")
print(f"중앙값: {x.median():.0f}점")
print(f"작년 평균(비교 기준): 4.3점 → 올해와의 차이 {x.mean() - 4.3:+.2f}점")

counts = x.value_counts().sort_index()
pct = (counts / x.notna().sum() * 100).round(1)
print("\n점수별 인원과 비율(%):")
print(pd.DataFrame({"인원": counts.astype(int), "비율(%)": pct}).to_string())
print(f"\n1~2점(불만) 응답: {int(counts.loc[[1, 2]].sum())}명, {pct.loc[[1, 2]].sum():.1f}%")

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(counts.index.astype(int).astype(str), counts.values, color="#4C72B0")
ax.axvline(x.mean() - 1, color="red", linestyle="--", label=f"평균 {x.mean():.2f}")
ax.set_xlabel("만족도 점수")
ax.set_ylabel("인원(명)")
ax.set_title(f"전반적 만족도 분포 (응답 {x.notna().sum()}명)")
ax.legend()
fig.tight_layout()
fig.savefig("instructor/answers/results/만족도_분포.png", dpi=150)
