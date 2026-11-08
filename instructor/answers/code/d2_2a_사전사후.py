"""2회차 2교시 같은 참여자의 사전·사후 비교 (정답 예시)."""
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

df = pd.read_csv("data/프로그램_사전사후.csv")
df["사전"] = df[[f"사전_Q{i}" for i in range(1, 6)]].mean(axis=1)
df["사후"] = df[[f"사후_Q{i}" for i in range(1, 6)]].mean(axis=1)
print("집단별 인원:", df["집단"].value_counts().to_dict())
drop = df[df["사후"].isna()]
print(f"사후 응답 없음(중도탈락): {len(drop)}명 {drop['ID'].tolist()}, 출석회차 {drop['출석회차'].tolist()}")
d = df.dropna(subset=["사후"]).copy()
d["변화"] = d["사후"] - d["사전"]

print("\n[같은 참여자의 사전·사후] 분석 대상: 사전·사후 모두 응답한 사람")
for g in ["참여", "대기"]:
    s = d[d["집단"] == g]
    paired = stats.ttest_rel(s["사후"], s["사전"])
    print(f"{g} {len(s)}명: 사전 {s['사전'].mean():.2f} → 사후 {s['사후'].mean():.2f}, "
          f"변화 {s['변화'].mean():+.2f}점, 대응표본 t검정 p값 = {paired.pvalue:.6f}")

p = d[d["집단"] == "참여"]
wrong = stats.ttest_ind(p["사후"], p["사전"])
print(f"\n[틀린 분석] 참여자 사전·사후를 서로 다른 사람처럼 독립표본 t검정: p값 = {wrong.pvalue:.4f}")
print(f"참여자의 사전·사후 점수 상관계수: {p['사전'].corr(p['사후']):.2f}")

w = d[d["집단"] == "대기"]
chg = stats.ttest_ind(p["변화"], w["변화"], equal_var=False)
print(f"\n[참여자와 대기자의 변화 비교] 변화 평균 참여 {p['변화'].mean():+.2f}, 대기 {w['변화'].mean():+.2f}, "
      f"차이 {p['변화'].mean() - w['변화'].mean():.2f}점, 독립표본 t검정 p값 = {chg.pvalue:.4f}")
post = stats.ttest_ind(p["사후"], w["사후"], equal_var=False)
print(f"[사후 점수만 비교] 참여 {p['사후'].mean():.2f}, 대기 {w['사후'].mean():.2f}, p값 = {post.pvalue:.4f}")
print(f"\n참여자 만족도: 평균 {p['만족도'].mean():.2f}점 ({p['만족도'].notna().sum()}명), "
      f"출석회차 평균 {p['출석회차'].mean():.1f}회")

fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), sharey=True)
for ax, g in zip(axes, ["참여", "대기"]):
    s = d[d["집단"] == g]
    for _, r in s.iterrows():
        ax.plot([0, 1], [r["사전"], r["사후"]], color="#BBBBBB", linewidth=0.8)
    ax.plot([0, 1], [s["사전"].mean(), s["사후"].mean()], color="#C44E52", linewidth=3, marker="o",
            label=f"평균 {s['사전'].mean():.2f} → {s['사후'].mean():.2f}")
    ax.set_xticks([0, 1], ["사전", "사후"])
    ax.set_title(f"{g} ({len(s)}명)")
    ax.legend(loc="upper left")
axes[0].set_ylabel("디지털 역량(1~5점)")
fig.suptitle("같은 사람의 사전·사후 점수 (회색 선 = 한 사람)")
fig.tight_layout()
fig.savefig("instructor/answers/results/사전사후.png", dpi=150)
