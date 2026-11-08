"""
교육용 가상 데이터 생성 (강사용, 학생 zip에 넣지 않음)
=====================================================
seed를 고정해 실행할 때마다 같은 파일을 만든다. 결과는 data/에 저장한다.
모든 데이터는 실제 사람·기관과 무관한 가상 데이터다.

공통 시나리오: ○○종합사회복지관 어르신 디지털 역량 강화 프로그램(스마트폰 교실, 8주)

파일과 쓰는 교시:
  욕구조사.csv            1회차 4교시(빈도·기술통계), 2회차 1교시(독립 두 집단 비교)
  프로그램_사전사후.csv   2회차 2교시(같은 참여자의 사전·사후 비교)

사용법 (프로젝트 최상위에서):
    .venv/bin/python instructor/make_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEED = 20261221

# 디지털 역량 5문항: 문항별 난이도(값이 클수록 쉬움)
ITEMS = {
    "Q1": 0.6,   # 전화를 걸고 문자를 보낼 수 있다
    "Q2": 0.2,   # 사진을 찍어 다른 사람에게 보낼 수 있다
    "Q3": 0.0,   # 카카오톡으로 대화할 수 있다
    "Q4": -0.5,  # 무인주문기(키오스크)로 주문할 수 있다
    "Q5": -0.7,  # 인터넷뱅킹으로 돈을 보낼 수 있다
}
FUNCS = ["전화·문자", "사진·영상", "카카오톡", "무인주문기(키오스크)", "인터넷뱅킹"]


def to_items(rng: np.random.Generator, ability: np.ndarray, noise: float) -> np.ndarray:
    """잠재 역량을 1~5점 문항 5개로 바꾼다."""
    cols = [
        np.clip(np.round(ability + off + rng.normal(0, noise, len(ability))), 1, 5)
        for off in ITEMS.values()
    ]
    return np.column_stack(cols).astype(int)


def make_needs(rng: np.random.Generator) -> pd.DataFrame:
    """기획 단계: 지역 어르신 디지털 이용 욕구조사 300명.

    설계: 독거 어르신의 역량이 낮다. 나이가 많을수록 낮고, 교육수준이 높을수록 높다.
    문항마다 2% 안팎으로 무응답(9)을 넣는다.
    """
    n = 300
    gender = rng.choice(["여", "남"], n, p=[0.6, 0.4])
    age = np.clip(np.round(65 + rng.gamma(2.2, 4.2, n)), 65, 92).astype(int)
    house = rng.choice(["독거", "부부", "자녀동거"], n, p=[0.35, 0.45, 0.20])
    edu_level = rng.choice([0, 1, 2], n, p=[0.4, 0.3, 0.3])
    phone = rng.random(n) < 0.86

    ability = (
        3.25
        - 0.045 * (age - 65)
        + 0.35 * edu_level
        - 0.35 * (house == "독거")
        - 0.6 * (~phone)
        + rng.normal(0, 0.5, n)
    )
    items = to_items(rng, ability, 0.55)
    hardest = [FUNCS[int(np.argmin(row + rng.uniform(0, 0.9, 5)))] for row in items]

    p_will = 0.42 + 0.16 * (house == "독거") - 0.05 * (ability - ability.mean())
    u = rng.random(n)
    will = np.where(u < p_will, "있다", np.where(u < p_will + 0.3, "모르겠다", "없다"))

    df = pd.DataFrame({
        "응답자ID": [f"N{i:03d}" for i in range(1, n + 1)],
        "성별": gender,
        "연령": age,
        "연령대": pd.cut(age, [64, 69, 74, 79, 200], labels=["65~69세", "70~74세", "75~79세", "80세 이상"]).astype(str),
        "가구형태": house,
        "교육수준": np.array(["초졸 이하", "중졸", "고졸 이상"])[edu_level],
        "스마트폰보유": np.where(phone, "예", "아니오"),
        "가장어려운기능": hardest,
    })
    for j, q in enumerate(ITEMS):
        col = items[:, j].copy()
        col[rng.random(n) < 0.02] = 9      # 무응답 코드
        df[f"디지털역량_{q}"] = col
    df["교육참여의향"] = will
    return df


def make_prepost(rng: np.random.Generator) -> pd.DataFrame:
    """평가 단계: 참여자 40명과 대기자 36명의 사전·사후 설문.

    설계: 사람마다 원래 역량 차이가 크고(사람 간 표준편차 약 0.75), 8주 동안의 변화는
    참여자 +0.4점, 대기자 +0.05점 안팎이다. 같은 사람의 사전·사후가 강하게 연결되므로
    대응표본 검정은 차이를 뚜렷하게 잡고, 독립표본 검정으로 잘못 분석하면 p값이 훨씬 크다.
    참여자 2명은 중도탈락해 사후 응답이 없다.
    """
    groups = [("참여", "P", 40, 0.40), ("대기", "W", 36, 0.05)]
    rows = []
    for name, prefix, n, gain in groups:
        base = rng.normal(2.45, 0.75, n)
        change = gain + rng.normal(0, 0.25, n)
        pre = to_items(rng, base, 0.35)
        post = to_items(rng, base + change, 0.35)
        age = np.clip(np.round(65 + rng.gamma(2.2, 4.0, n)), 65, 88).astype(int)
        gender = rng.choice(["여", "남"], n, p=[0.65, 0.35])
        for i in range(n):
            rows.append({
                "ID": f"{prefix}{i + 1:02d}",
                "집단": name,
                "성별": gender[i],
                "연령": age[i],
                **{f"사전_{q}": pre[i, j] for j, q in enumerate(ITEMS)},
                **{f"사후_{q}": post[i, j] for j, q in enumerate(ITEMS)},
                "출석회차": int(rng.integers(5, 9)) if name == "참여" else 0,
                "만족도": int(np.clip(np.round(rng.normal(4.2, 0.7)), 1, 5)) if name == "참여" else np.nan,
            })
    df = pd.DataFrame(rows)
    drop = df.index[df["ID"].isin(["P07", "P23"])]
    df.loc[drop, [f"사후_{q}" for q in ITEMS] + ["만족도"]] = np.nan
    df.loc[drop, "출석회차"] = [2, 3]
    for c in [f"사후_{q}" for q in ITEMS] + ["만족도"]:
        df[c] = df[c].astype("Int64")
    return df


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    # Excel에서 한글이 깨지지 않게 BOM 포함 UTF-8로 저장한다.
    make_needs(rng).to_csv(DATA / "욕구조사.csv", index=False, encoding="utf-8-sig")
    make_prepost(rng).to_csv(DATA / "프로그램_사전사후.csv", index=False, encoding="utf-8-sig")
    for p in sorted(DATA.glob("*.csv")):
        print(f"만든 파일: {p.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
