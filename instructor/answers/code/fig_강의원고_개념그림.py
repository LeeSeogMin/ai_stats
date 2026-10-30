"""강의원고에 넣는 개념 그림 (실습 데이터의 답이 드러나지 않게 작은 예로 그린다)."""
import matplotlib.pyplot as plt
import numpy as np

# 그림 1: 평균과 중앙값 — 월급 5건 손 계산 예
w = [230, 240, 250, 260, 1000]
fig, ax = plt.subplots(figsize=(6, 2.6))
ax.scatter(w, [0] * len(w), s=80, color="#4C72B0", zorder=3)
for v in w:
    ax.annotate(str(v), (v, 0), textcoords="offset points", xytext=(0, 10), ha="center")
ax.axvline(np.mean(w), color="red", linestyle="--", label=f"평균 {np.mean(w):.0f}")
ax.axvline(np.median(w), color="green", label=f"중앙값 {np.median(w):.0f}")
ax.set_yticks([])
ax.set_xlabel("월급(만 원)")
ax.set_title("공고 5건: 고액 공고 1건 때문에 평균이 중앙값보다 146 크다")
ax.legend(loc="upper center")
fig.tight_layout()
fig.savefig("lecture/images/평균과_중앙값.png", dpi=150)
print(f"그림 1: 평균 {np.mean(w):.0f}, 중앙값 {np.median(w):.0f}")

# 그림 2: 세 번째 요인 — 기온이 아이스크림 판매와 물놀이 사고를 함께 늘린다 (그림용 가상 수치)
rng = np.random.default_rng(1)
temp = np.linspace(5, 33, 24)
ice = 20 + 4 * temp + rng.normal(0, 8, 24)
acc = np.clip(np.round(1 + 0.25 * temp + rng.normal(0, 1, 24)), 0, None)
fig, axes = plt.subplots(1, 3, figsize=(10, 3))
axes[0].scatter(ice, acc, color="#4C72B0")
axes[0].set_xlabel("아이스크림 판매(개)")
axes[0].set_ylabel("물놀이 사고(건)")
axes[0].set_title(f"상관계수 {np.corrcoef(ice, acc)[0, 1]:.2f}")
axes[1].scatter(temp, ice, color="#DD8452")
axes[1].set_xlabel("기온(℃)")
axes[1].set_ylabel("아이스크림 판매(개)")
axes[1].set_title("기온 → 판매")
axes[2].scatter(temp, acc, color="#DD8452")
axes[2].set_xlabel("기온(℃)")
axes[2].set_ylabel("물놀이 사고(건)")
axes[2].set_title("기온 → 사고")
fig.suptitle("같이 움직인다고 원인은 아니다 (그림용 가상 수치)")
fig.tight_layout()
fig.savefig("lecture/images/세번째_요인.png", dpi=150)
print(f"그림 2: 아이스크림-사고 상관계수 {np.corrcoef(ice, acc)[0, 1]:.2f}")
