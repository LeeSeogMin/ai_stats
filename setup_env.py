#!/usr/bin/env python3
"""
「AI를 활용한 통계」 실습 환경 부트스트랩.

- 이 폴더에 가상환경(.venv/)을 만든다
- requirements.txt의 패키지를 설치한다
- --check: 패키지 import와 그래프 한글 글꼴을 확인한다 (설치는 하지 않음)

보통은 setup/setup_windows.ps1, setup/setup_mac.sh가 uv로 환경을 만든 뒤
이 스크립트를 --check로만 호출한다. uv 없이 직접 만들 때도 쓸 수 있다.
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _print_header() -> None:
    print("=" * 60)
    print("setup_env.py: 실습 환경 점검")
    print("=" * 60)
    print(f"OS: {platform.platform()}")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")


def create_venv(venv_dir: Path) -> None:
    if venv_dir.exists():
        return
    print(f"[1/3] 가상환경을 만듭니다: {venv_dir}")
    builder = venv.EnvBuilder(with_pip=True, clear=False, symlinks=False, upgrade=False)
    builder.create(str(venv_dir))


def install_packages(python_exe: Path) -> None:
    print("[2/3] 패키지를 설치합니다...")
    _run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    _run([str(python_exe), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])


def check(python_exe: Path) -> int:
    print("[3/3] 패키지와 한글 글꼴을 확인합니다...")
    code = r"""
import importlib

mods = ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "seaborn", "openpyxl"]
failed = []
for m in mods:
    try:
        importlib.import_module(m)
        print(f"OK   {m}")
    except Exception as e:
        failed.append(m)
        print(f"FAIL {m}: {e}")

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager as fm
font = fm.findfont(fm.FontProperties(family=["sans-serif"]))
if "DejaVu" in font:
    failed.append("korean-font")
    print(f"FAIL 한글 글꼴: 찾지 못함 ({font}) - 그래프의 한글이 네모로 보일 수 있습니다")
else:
    print(f"OK   한글 글꼴: {font}")

raise SystemExit(1 if failed else 0)
"""
    # matplotlibrc는 현재 폴더에서 읽으므로 이 폴더를 작업 폴더로 지정한다.
    result = subprocess.call([str(python_exe), "-c", code], cwd=str(ROOT))
    if result == 0:
        print("\n모든 점검을 통과했습니다.")
    else:
        print("\n일부 점검에 실패했습니다. 위 FAIL 줄을 조교에게 보여 주세요.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="「AI를 활용한 통계」 실습 환경을 만든다.")
    parser.add_argument("--venv-dir", default=".venv", help="가상환경 폴더 (기본값: .venv)")
    parser.add_argument("--check", action="store_true", help="설치 없이 점검만 한다.")
    args = parser.parse_args()

    sys.stdout.reconfigure(line_buffering=True)
    _print_header()

    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10 이상이 필요합니다.")
        return 2

    venv_dir = (ROOT / args.venv_dir).resolve()
    if not args.check:
        create_venv(venv_dir)
    python_exe = _venv_python(venv_dir)
    if not python_exe.exists():
        print(f"ERROR: 가상환경 Python이 없습니다: {python_exe}")
        print("설치 스크립트(setup 폴더)를 먼저 실행하세요.")
        return 2

    if not args.check:
        install_packages(python_exe)
    return check(python_exe)


if __name__ == "__main__":
    raise SystemExit(main())
