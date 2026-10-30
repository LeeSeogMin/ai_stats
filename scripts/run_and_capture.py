"""
실행 증거 게이트 (Execution Evidence Gate)
==========================================
AI가 실행하지 않은 숫자를 답변에 쓰지 못하게 하는 장치다.
mlops_public/scripts/run_and_capture.py를 이 수업에 맞게 줄였다.

분석 코드(.py)를 실제로 실행하여:
  1. 화면 출력 전체를 로그로 저장          → results/{파일}.log
  2. 소스 코드와 출력의 SHA-256 해시 기록  → results/{파일}.evidence.json
  3. 실행 시각·소요시간·종료코드·Python 버전·운영체제, 이번 실행에서 만든 그림 파일 기록

답변의 숫자는 반드시 이 로그에서만 가져온다.

사용법 (프로젝트 최상위에서, 가상환경 Python으로):
    # 파일 하나 실행
    .venv/bin/python scripts/run_and_capture.py outputs/code/만족도_평균.py

    # outputs/code 안의 모든 파일 실행
    .venv/bin/python scripts/run_and_capture.py --all

    # 검증만: 로그를 만든 뒤 코드가 바뀌었는지(= 결과가 낡았는지) 확인
    .venv/bin/python scripts/run_and_capture.py --verify --all

결과 폴더: 코드가 `.../code/` 안에 있으면 형제 폴더 `.../results/`, 아니면 코드 옆 `results/`.
Windows에서는 `.venv\\Scripts\\python.exe scripts\\run_and_capture.py ...`로 실행한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CODE_DIR = PROJECT_ROOT / "outputs" / "code"


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def results_dir_for(py_file: Path) -> Path:
    if py_file.parent.name == "code":
        return py_file.parent.parent / "results"
    return py_file.parent / "results"


def rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def collect_files(paths: list[str], use_all: bool, code_dir: Path) -> list[Path]:
    files: list[Path] = []
    if use_all:
        files += sorted(p for p in code_dir.glob("*.py") if not p.name.startswith("_"))
    for p in paths:
        f = Path(p)
        if not f.is_absolute():
            f = (Path.cwd() / f).resolve()
        if not f.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {p}")
        files.append(f)
    return files


def run_one(py_file: Path, timeout: int) -> dict:
    source = py_file.read_text(encoding="utf-8")
    results_dir = results_dir_for(py_file)
    results_dir.mkdir(parents=True, exist_ok=True)

    exts = {".png", ".jpg", ".jpeg", ".svg", ".csv", ".xlsx"}

    def snapshot() -> dict[Path, float]:
        return {p: p.stat().st_mtime for p in results_dir.glob("*") if p.suffix.lower() in exts}

    before = snapshot()
    started = time.perf_counter()
    started_iso = datetime.now(timezone.utc).astimezone().isoformat()

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"         # Windows에서도 한글 출력을 UTF-8로 받는다
    env["PYTHONIOENCODING"] = "utf-8"
    env["MPLBACKEND"] = "Agg"       # plt.show()가 창을 띄워 멈추지 않게 한다

    try:
        # 프로젝트 최상위에서 실행한다: matplotlibrc(한글 글꼴)와 data/ 상대 경로가 맞는다.
        proc = subprocess.run(
            [sys.executable, str(py_file)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        exit_code = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
        timed_out = False
    except subprocess.TimeoutExpired as e:
        exit_code = None
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\n[TIMEOUT] {timeout}초를 넘겨 중단함"
        timed_out = True
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")

    duration = round(time.perf_counter() - started, 2)
    combined = (
        f"$ python {rel(py_file)}\n\n=== 화면 출력(STDOUT) ===\n{stdout}\n"
        f"=== 오류·경고(STDERR) ===\n{stderr}"
    )

    # 이번 실행에서 새로 생기거나 바뀐 그림·표 파일
    created = sorted(rel(p) for p, t in snapshot().items() if before.get(p) != t)

    log_path = results_dir / f"{py_file.stem}.log"
    log_path.write_text(combined, encoding="utf-8")

    evidence = {
        "file": rel(py_file),
        "started_at": started_iso,
        "duration_sec": duration,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "success": exit_code == 0,
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "source_sha256": sha256_of_text(source),
        "output_sha256": sha256_of_text(combined),
        "output_log": rel(log_path),
        "created_files": created,
    }
    ev_path = results_dir / f"{py_file.stem}.evidence.json"
    ev_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence


def verify(files: list[Path]) -> int:
    problems = 0
    for py_file in files:
        ev_path = results_dir_for(py_file) / f"{py_file.stem}.evidence.json"
        if not ev_path.exists():
            print(f"  [증거 없음] {rel(py_file)} — 아직 run_and_capture.py로 실행하지 않음")
            problems += 1
            continue
        ev = json.loads(ev_path.read_text(encoding="utf-8"))
        current = sha256_of_text(py_file.read_text(encoding="utf-8"))
        if current != ev["source_sha256"]:
            print(f"  [낡은 결과] {rel(py_file)} — 로그를 만든 뒤 코드가 바뀜. 다시 실행 필요")
            problems += 1
        elif not ev.get("success"):
            print(f"  [실패한 실행] {rel(py_file)} — 종료코드 {ev.get('exit_code')}")
            problems += 1
        else:
            print(f"  [유효] {rel(py_file)} (코드 일치, 정상 종료)")
    return problems


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    parser = argparse.ArgumentParser(description="실행 증거 게이트")
    parser.add_argument("files", nargs="*", help="실행할 .py 파일")
    parser.add_argument("--all", action="store_true", help="코드 폴더의 모든 .py 실행")
    parser.add_argument("--code-dir", default=str(DEFAULT_CODE_DIR), help="--all의 대상 폴더 (기본: outputs/code)")
    parser.add_argument("--verify", action="store_true", help="실행 없이 무결성만 검증")
    parser.add_argument("--timeout", type=int, default=600, help="파일당 제한시간(초)")
    args = parser.parse_args()

    code_dir = Path(args.code_dir)
    if not code_dir.is_absolute():
        code_dir = (Path.cwd() / code_dir).resolve()
    files = collect_files(args.files, args.all, code_dir)
    if not files:
        print(f"실행할 .py 파일이 없습니다: {rel(code_dir)}")
        return 0 if args.verify else 1

    if args.verify:
        print(f"[검증] {len(files)}개 파일")
        problems = verify(files)
        print(f"\n검증 완료: 문제 {problems}건")
        return 1 if problems else 0

    all_ok = True
    for py_file in files:
        print(f"▶ {rel(py_file)} 실행 중...")
        ev = run_one(py_file, args.timeout)
        status = "성공" if ev["success"] else f"실패(종료코드 {ev['exit_code']})"
        print(f"  [{status}] {ev['duration_sec']}초 → {ev['output_log']}")
        for f in ev["created_files"]:
            print(f"    만든 파일: {f}")
        all_ok = all_ok and ev["success"]

    print("\n답변의 숫자는 위 .log 파일에서만 가져올 것.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
