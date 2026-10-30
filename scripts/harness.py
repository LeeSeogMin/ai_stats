"""
하네스: 실습 폴더 전체 점검
===========================
basic_DL/scripts/harness.sh를 Windows에서도 돌도록 Python으로 옮겼다.

검사 항목:
  1. 실습 환경 (setup_env.py --check: 패키지·한글 글꼴)
  2. outputs/code의 모든 분석 코드에 유효한 실행 증거가 있는지 (run_and_capture.py --verify)

통과하면 HARNESS_PASS, 하나라도 실패하면 HARNESS_FAIL을 출력한다.
검사를 하나도 하지 못했으면 통과로 보지 않는다.

사용법 (프로젝트 최상위에서):
    Windows: .venv\\Scripts\\python.exe scripts\\harness.py
    macOS:   .venv/bin/python scripts/harness.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    print(f"=== 하네스 시작 ({datetime.now():%Y-%m-%d %H:%M:%S}) ===")
    checks = 0
    failed: list[str] = []

    steps = [
        ("실습 환경", [sys.executable, str(ROOT / "setup_env.py"), "--check"]),
    ]
    if any((ROOT / "outputs" / "code").glob("*.py")):
        steps.append(("실행 증거", [sys.executable, str(ROOT / "scripts" / "run_and_capture.py"), "--verify", "--all"]))
    else:
        print("[건너뜀] 실행 증거 — outputs/code에 분석 코드가 아직 없음")

    for name, cmd in steps:
        print(f"\n--- {name}")
        code = subprocess.call(cmd, cwd=ROOT)
        checks += 1
        if code != 0:
            failed.append(name)

    print()
    if checks == 0:
        print("HARNESS_FAIL: 검사를 하나도 수행하지 못했다. 통과로 볼 근거가 없다.")
        return 1
    if failed:
        print(f"HARNESS_FAIL: {', '.join(failed)}")
        return 1
    print(f"=== 수행한 검사 {checks}건 ===")
    print("HARNESS_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
