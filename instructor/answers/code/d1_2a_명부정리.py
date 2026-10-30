"""1회차 2교시 ① 이용자 명부를 표로 정리한다 (정답 예시)."""
import re

import pandas as pd

raw = pd.read_excel("data/이용자명부_원본.xlsx", dtype=str).fillna("")
print(f"원본 행 수: {len(raw)}")


def to_date(s: str) -> str:
    s = s.strip()
    m = re.match(r"(\d{4})[-.](\d{1,2})[-.](\d{1,2})", s)
    if m:
        y, mo, d = m.groups()
    else:
        m = re.match(r"(\d{1,2})월\s*(\d{1,2})일", s)
        y, (mo, d) = "2026", m.groups()
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


score = {"매우 만족": 5, "만족": 4, "보통": 3, "불만": 2, "매우 불만": 1}
df = raw.copy()
df["방문일"] = df["방문일"].map(to_date)
df["연령대"] = df["연령대"].str.replace(" ", "")
df["프로그램"] = df["프로그램"].str.replace(" ", "").replace({"스마트폰교실": "스마트폰 교실"})
df["만족도"] = df["만족도"].map(lambda s: score.get(s, int(s) if s.isdigit() else None))

dup = df.duplicated(subset=["이용자", "방문일", "프로그램"], keep="first")
print(f"중복 입력 행: {dup.sum()}")
df = df[~dup].drop(columns="비고").sort_values("이용자").reset_index(drop=True)
print(f"정리 후 행 수: {len(df)}")
print(f"만족도 빈칸: {df['만족도'].isna().sum()}")
print("\n프로그램별 인원:")
print(df["프로그램"].value_counts().to_string())
print("\n정리한 표 (앞 5행):")
print(df.head().to_string(index=False))
df.to_csv("instructor/answers/results/이용자명부_정리.csv", index=False, encoding="utf-8-sig")
