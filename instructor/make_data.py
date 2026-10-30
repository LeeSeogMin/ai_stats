"""
교육용 가상 데이터 생성 (강사용, 학생 zip에 넣지 않음)
=====================================================
seed를 고정해 실행할 때마다 같은 파일을 만든다. 결과는 data/에 저장한다.
모든 데이터는 실제 사람·기관과 무관한 가상 데이터다.

파일과 쓰는 교시:
  이용자명부_원본.xlsx   1회차 2교시  지저분한 기록을 표로 정리하는 연습
  만족도조사.csv         1회차 2교시, 2회차 1·2교시  평균·분포, 집단 비교, 교차표
  채용공고_월급.csv      1회차 3교시  치우친 분포, 평균과 중앙값
  가게_월별매출.csv      2회차 2교시  상관과 인과, 회귀선

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


def make_survey(rng: np.random.Generator) -> pd.DataFrame:
    """복지관 이용자 만족도 조사 300명.

    설계: 이용기간이 길수록 프로그램 참여 확률과 만족도가 함께 높다.
    그래서 참여자와 미참여자의 만족도 차이 일부는 이용기간 때문이다.
    """
    n = 300
    gender = rng.choice(["여", "남"], size=n, p=[0.62, 0.38])
    age = rng.choice(["20대", "30대", "40대", "50대", "60대", "70대 이상"], size=n,
                     p=[0.06, 0.10, 0.16, 0.22, 0.26, 0.20])
    months = np.clip(np.round(rng.gamma(shape=2.0, scale=10.0, size=n)), 1, 72).astype(int)
    p_join = 1 / (1 + np.exp(-(months - 20) / 8))
    joined = rng.random(n) < p_join

    latent = 4.25 + 0.012 * months + 0.12 * joined + rng.normal(0, 0.55, n)
    # 일부 응답자는 불만이 크다: 낮은 점수 쪽 꼬리
    unhappy = rng.random(n) < 0.07
    latent[unhappy] = rng.uniform(0.6, 2.4, unhappy.sum())
    overall = np.clip(np.round(latent), 1, 5).astype(int)
    staff = np.clip(np.round(latent + rng.normal(0.15, 0.5, n)), 1, 5).astype(int)
    facility = np.clip(np.round(latent + rng.normal(-0.35, 0.6, n)), 1, 5).astype(int)
    revisit = np.where(overall >= 4, rng.random(n) < 0.9, rng.random(n) < 0.35)

    df = pd.DataFrame({
        "응답자ID": [f"R{i:03d}" for i in range(1, n + 1)],
        "성별": gender,
        "연령대": age,
        "이용기간_개월": months,
        "프로그램참여": np.where(joined, "참여", "미참여"),
        "만족도_전반": overall.astype(float),
        "만족도_직원친절": staff,
        "만족도_시설": facility,
        "재이용의향": np.where(revisit, "예", "아니오"),
    })
    missing = rng.choice(n, size=12, replace=False)
    df.loc[missing, "만족도_전반"] = np.nan
    df["만족도_전반"] = df["만족도_전반"].astype("Int64")
    return df


def make_salary(rng: np.random.Generator) -> pd.DataFrame:
    """채용공고 200건. 대부분 220~300만 원, 관리직 소수가 고액."""
    n_normal, n_high = 186, 14
    jobs = ["사회복지사", "요양보호사", "사무보조", "상담원", "생활지도원", "행정직"]
    regions = ["서울", "경기", "인천", "충청", "기타"]
    normal = np.clip(np.round(rng.normal(255, 24, n_normal) / 5) * 5, 210, 330)
    high = np.round(rng.uniform(600, 1200, n_high) / 10) * 10
    df = pd.DataFrame({
        "직무": list(rng.choice(jobs, n_normal)) + ["센터장·관리직"] * n_high,
        "지역": rng.choice(regions, n_normal + n_high, p=[0.3, 0.35, 0.1, 0.15, 0.1]),
        "고용형태": list(rng.choice(["정규직", "계약직"], n_normal, p=[0.55, 0.45])) + ["정규직"] * n_high,
        "월급_만원": np.concatenate([normal, high]).astype(int),
    })
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    df.insert(0, "공고ID", [f"J{i:03d}" for i in range(1, len(df) + 1)])
    return df


def make_store(rng: np.random.Generator) -> pd.DataFrame:
    """동네 카페 36개월. 성수기(7·8·12월)에 광고비와 매출이 함께 오른다.

    설계상 광고비 1만 원이 늘 때 매출은 약 0.8만 원만 는다.
    성수기를 고려하지 않으면 광고비의 효과가 훨씬 크게 보인다.
    """
    months = pd.period_range("2024-01", "2026-12", freq="M")
    peak = np.isin(months.month, [7, 8, 12])
    ad = np.round(100 + 150 * peak + rng.normal(0, 35, len(months)))
    sales = np.round(2000 + 1500 * peak + 0.8 * ad + rng.normal(0, 120, len(months)))
    return pd.DataFrame({
        "연월": months.astype(str),
        "성수기": np.where(peak, "예", "아니오"),
        "광고비_만원": ad.astype(int),
        "매출_만원": sales.astype(int),
    })


def make_roster(rng: np.random.Generator) -> pd.DataFrame:
    """손으로 적은 이용자 명부를 옮긴 듯한 지저분한 기록 40행(37명 + 중복 3행)."""
    n = 37
    days = pd.to_datetime("2026-03-02") + pd.to_timedelta(rng.integers(0, 60, n), unit="D")
    fmt = rng.choice(["iso", "dot", "kor"], n, p=[0.5, 0.3, 0.2])
    date_txt = [
        d.strftime("%Y-%m-%d") if f == "iso"
        else f"{d.year}.{d.month}.{d.day}" if f == "dot"
        else f"{d.month}월 {d.day}일"
        for d, f in zip(days, fmt)
    ]
    sat_num = rng.choice([5, 4, 3, 2], n, p=[0.4, 0.35, 0.18, 0.07])
    word = {5: "매우 만족", 4: "만족", 3: "보통", 2: "불만"}
    style = rng.choice(["num", "word", "blank"], n, p=[0.6, 0.32, 0.08])
    sat = [str(s) if st == "num" else word[s] if st == "word" else "" for s, st in zip(sat_num, style)]
    df = pd.DataFrame({
        "이용자": [f"이용자{i:02d}" for i in range(1, n + 1)],
        "방문일": date_txt,
        "연령대": rng.choice(["50대", "60대", "70대", "70대 이상", "60 대"], n, p=[0.2, 0.3, 0.25, 0.2, 0.05]),
        "프로그램": rng.choice(["건강체조", "스마트폰 교실", "노래교실", "건강 체조"], n, p=[0.35, 0.3, 0.25, 0.1]),
        "만족도": sat,
        "비고": [""] * n,
    })
    dup = df.iloc[[3, 11, 25]].copy()
    dup["비고"] = "재입력"
    df = pd.concat([df, dup]).sample(frac=1, random_state=SEED).reset_index(drop=True)
    return df


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    make_roster(rng).to_excel(DATA / "이용자명부_원본.xlsx", index=False)
    # Excel에서 한글이 깨지지 않게 BOM 포함 UTF-8로 저장한다.
    make_survey(rng).to_csv(DATA / "만족도조사.csv", index=False, encoding="utf-8-sig")
    make_salary(rng).to_csv(DATA / "채용공고_월급.csv", index=False, encoding="utf-8-sig")
    make_store(rng).to_csv(DATA / "가게_월별매출.csv", index=False, encoding="utf-8-sig")
    for p in sorted(DATA.glob("*.*")):
        print(f"만든 파일: {p.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
