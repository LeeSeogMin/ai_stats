"""
학생 배포용 zip 만들기 (강사용)
==============================
포함 목록(화이트리스트)에 있는 파일만 dist/ai_stats.zip에 담는다.
강사 문서(objective.md, 작업목록.md, 강의방향.md, 사전안내문.md), instructor/, .git, .venv,
outputs의 결과물, 이 스크립트 자체는 들어가지 않는다.

zip 안 최상위 폴더 이름은 ai_stats다. 압축을 풀면 ai_stats 폴더 하나가 생긴다.

사용법 (프로젝트 최상위에서):
    python3 scripts/make_student_zip.py
    python3 scripts/make_student_zip.py --list   # 담을 파일 목록만 출력
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "ai_stats.zip"
PREFIX = "ai_stats"

# 최상위 파일
FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "CODEX.md",
    "harness.md",
    "시작하기.md",
    "강의계획서.md",
    "설치가이드.md",
    "설치가이드.pdf",
    "matplotlibrc",
    "requirements.txt",
    "setup_env.py",
    "scripts/run_and_capture.py",
    "scripts/harness.py",
    "outputs/code/.gitkeep",
    "outputs/results/.gitkeep",
]

# 폴더 전체
DIRS = [
    ".ai",
    ".claude/skills",
    ".github",
    ".vscode",
    "setup",
    "data",
    "lecture",
    "practice",
]

SKIP_NAMES = {".DS_Store", "__pycache__", ".ipynb_checkpoints"}


def collect() -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    missing: list[str] = []
    for f in FILES:
        p = ROOT / f
        if p.is_file():
            files.append(p)
        else:
            missing.append(f)
    for d in DIRS:
        p = ROOT / d
        if not p.is_dir():
            missing.append(d + "/")
            continue
        for q in sorted(p.rglob("*")):
            if q.is_file() and not any(part in SKIP_NAMES for part in q.parts):
                files.append(q)
    return files, missing


def main() -> int:
    parser = argparse.ArgumentParser(description="학생 배포용 zip 만들기")
    parser.add_argument("--list", action="store_true", help="담을 파일 목록만 출력")
    args = parser.parse_args()

    files, missing = collect()
    for m in missing:
        print(f"[없음] {m}")

    if args.list:
        for f in files:
            print(f.relative_to(ROOT).as_posix())
        print(f"\n파일 {len(files)}개")
        return 0

    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            # 한글 파일명은 zipfile이 UTF-8 표시(flag 0x800)를 붙여 저장한다.
            zf.write(f, f"{PREFIX}/{f.relative_to(ROOT).as_posix()}")
    size_kb = OUT.stat().st_size / 1024
    print(f"만든 파일: {OUT.relative_to(ROOT)} ({len(files)}개 파일, {size_kb:.0f} KB)")
    if missing:
        print(f"주의: 포함 목록 중 {len(missing)}개가 없습니다(위 [없음] 줄).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
