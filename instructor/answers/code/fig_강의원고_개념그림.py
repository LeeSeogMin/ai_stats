"""강의원고에 넣는 개념 그림 (실습 데이터의 답이 드러나지 않게 작은 예로 그린다)."""
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# 그림 1: 평균과 중앙값 — 어르신 5명의 한 달 복지관 이용 횟수
v = [2, 3, 3, 4, 20]
fig, ax = plt.subplots(figsize=(6, 2.6))
ax.scatter(v, [0] * len(v), s=80, color="#4C72B0", zorder=3)
for x in sorted(set(v)):
    ax.annotate(f"{x}회" + (" ×2" if v.count(x) > 1 else ""), (x, 0), textcoords="offset points", xytext=(0, 10), ha="center")
ax.axvline(np.mean(v), color="red", linestyle="--", label=f"평균 {np.mean(v):.1f}회")
ax.axvline(np.median(v), color="green", label=f"중앙값 {np.median(v):.0f}회")
ax.set_yticks([])
ax.set_xlabel("한 달 이용 횟수")
ax.set_title("5명 중 1명의 20회 때문에 평균이 중앙값의 2배를 넘는다")
ax.legend(loc="upper center")
fig.tight_layout()
fig.savefig("lecture/images/평균과_중앙값.png", dpi=150)
print(f"그림 1: 평균 {np.mean(v):.1f}, 중앙값 {np.median(v):.0f}")

# 그림 2: 독립 대 대응 — 같은 숫자 10개를 「서로 다른 5명씩」으로 볼 때와 「같은 5명의 사전·사후」로 볼 때
pre = np.array([1.6, 2.2, 2.8, 3.4, 4.0])
post = pre + np.array([0.4, 0.3, 0.5, 0.3, 0.4])
p_ind = stats.ttest_ind(post, pre).pvalue
p_rel = stats.ttest_rel(post, pre).pvalue
fig, axes = plt.subplots(1, 2, figsize=(8, 3.4), sharey=True)
axes[0].scatter([0] * 5, pre, s=60, color="#999999")
axes[0].scatter([1] * 5, post, s=60, color="#4C72B0")
axes[0].set_title(f"서로 다른 사람으로 보면\n독립표본 t검정 p = {p_ind:.2f}")
for a, b in zip(pre, post):
    axes[1].plot([0, 1], [a, b], color="#4C72B0", marker="o")
axes[1].set_title(f"같은 사람의 전후로 보면\n대응표본 t검정 p = {p_rel:.4f}")
for ax in axes:
    ax.set_xticks([0, 1], ["사전", "사후"])
    ax.set_xlim(-0.5, 1.5)
axes[0].set_ylabel("점수")
fig.suptitle("같은 숫자 10개, 다른 분석 (그림용 가상 수치)")
fig.tight_layout()
fig.savefig("lecture/images/독립과_대응.png", dpi=150)
print(f"그림 2: 사전 평균 {pre.mean():.2f}, 사후 평균 {post.mean():.2f}, 독립 p {p_ind:.2f}, 대응 p {p_rel:.4f}")
