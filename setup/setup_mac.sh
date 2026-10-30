#!/usr/bin/env bash
# 「AI를 활용한 통계」 특강 — macOS 자동 설치 스크립트
#
# 학생이 미리 해 둘 것: VS Code 설치, GitHub 가입, 메일로 받은 실습 zip 압축 풀기
# 실행 방법: 터미널에 `bash ` 를 입력하고 이 파일을 터미널 창으로 끌어다 놓은 뒤 Enter
#
# 이 스크립트가 하는 일:
#   1. 실습 폴더 확인 (이 파일이 들어 있는 압축 푼 폴더를 그대로 쓴다)
#   2. uv 설치 → Python 3.12 + 실습 패키지 설치
#   3. Claude Code 설치 (설치는 무료, 사용하려면 Claude Pro 로그인 필요)
#   4. 점검
# VS Code 확장은 1교시에 함께 설치한다(.vscode/extensions.json).
# 이미 설치된 항목은 건너뛴다. 여러 번 실행해도 된다.

RESULTS=()
FAILED=0

say()  { printf '\n\033[1;34m▶ %s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m[성공]\033[0m %s\n' "$1"; RESULTS+=("[성공] $1"); }
skip() { printf '  \033[36m[건너뜀]\033[0m %s\n' "$1"; RESULTS+=("[건너뜀] $1"); }
warn() { printf '  \033[33m[주의]\033[0m %s\n' "$1"; RESULTS+=("[주의] $1"); }
fail() { printf '  \033[31m[실패]\033[0m %s\n' "$1"; RESULTS+=("[실패] $1"); FAILED=$((FAILED + 1)); }

summary() {
  echo
  echo "=================================================="
  echo " 설치 결과"
  echo "=================================================="
  for r in "${RESULTS[@]}"; do echo "  $r"; done
  echo
  if [ "$FAILED" -eq 0 ]; then
    echo "모든 설치를 마쳤습니다. 이 화면을 캡처해서 회신해 주세요."
    echo "VS Code 확장 설치와 Copilot·Claude 로그인은 1교시에 함께 합니다."
    echo "실습 폴더: $1"
  else
    echo "실패한 항목이 $FAILED 개 있습니다. 이 화면을 캡처해서 조교에게 보내 주세요."
    echo "스크립트는 여러 번 실행해도 됩니다. 문제를 고친 뒤 다시 실행하세요."
  fi
}

main() {
  export PATH="$HOME/.local/bin:$PATH"

  echo "=================================================="
  echo " 「AI를 활용한 통계」 실습 환경 자동 설치 (macOS)"
  echo "=================================================="

  # ---------------------------------------------------------------- 0. VS Code
  say "0단계: VS Code 확인"
  local found=""
  if command -v code >/dev/null 2>&1; then
    found=1
  else
    for app in "/Applications/Visual Studio Code.app" "$HOME/Applications/Visual Studio Code.app"; do
      if [ -d "$app" ]; then found=1; break; fi
    done
  fi
  if [ -n "$found" ]; then
    ok "VS Code 찾음"
  else
    fail "VS Code를 찾지 못함 — https://code.visualstudio.com 에서 설치하고 '응용 프로그램' 폴더로 옮기세요"
  fi

  # ---------------------------------------------------------------- 1. 실습 폴더
  say "1단계: 실습 폴더 확인"
  local script_dir target
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  target="$(cd "$script_dir/.." && pwd)"
  if [ ! -f "$target/setup_env.py" ] || [ ! -f "$target/requirements.txt" ]; then
    fail "실습 폴더가 아닙니다: $target — 메일로 받은 zip의 압축을 모두 푼 뒤, 그 안의 setup/setup_mac.sh를 실행하세요"
    summary "$target"
    return
  fi
  ok "실습 폴더: $target"
  case "$target" in
    *"Library/Mobile Documents"*|*CloudStorage*)
      warn "iCloud·클라우드 동기화 폴더 안에 있습니다. 오류가 나면 폴더를 홈 폴더(~/ai_stats)로 옮긴 뒤 다시 실행하세요" ;;
  esac

  # ---------------------------------------------------------------- 2. uv + Python
  say "2단계: Python과 실습 패키지 설치"
  if command -v uv >/dev/null 2>&1; then
    skip "uv 이미 설치됨"
  elif curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 && command -v uv >/dev/null 2>&1; then
    ok "uv 설치"
  else
    fail "uv 설치 실패 — 인터넷 연결을 확인하세요"
  fi

  local py="$target/.venv/bin/python"
  if command -v uv >/dev/null 2>&1; then
    if [ -x "$py" ]; then
      skip "가상환경(.venv) 이미 있음"
    elif uv venv --python 3.12 "$target/.venv" >/dev/null 2>&1; then
      ok "Python 3.12 가상환경 생성"
    else
      fail "가상환경 생성 실패"
    fi
    if [ -x "$py" ]; then
      if uv pip install --python "$py" -r "$target/requirements.txt"; then
        ok "실습 패키지 설치"
      else
        fail "실습 패키지 설치 실패"
      fi
    fi
  fi

  # ---------------------------------------------------------------- 3. Claude Code
  say "3단계: Claude Code 설치 (권장 도구)"
  if command -v claude >/dev/null 2>&1; then
    skip "Claude Code 이미 설치됨"
  elif curl -fsSL https://claude.ai/install.sh | bash && command -v claude >/dev/null 2>&1; then
    ok "Claude Code 설치 (사용하려면 Claude Pro 로그인 필요)"
  else
    warn "Claude Code 설치 실패 — 기본 도구인 Copilot으로 수업할 수 있습니다"
  fi

  # 새 터미널에서도 claude·uv를 찾을 수 있게 PATH를 등록한다.
  for rc in "$HOME/.zshrc" "$HOME/.bash_profile"; do
    # zsh(macOS 기본)는 항상, bash는 설정 파일이 있을 때만 등록한다.
    if [ "$rc" = "$HOME/.bash_profile" ] && [ ! -f "$rc" ]; then continue; fi
    grep -qs '.local/bin' "$rc" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc"
  done

  # ---------------------------------------------------------------- 4. 점검
  say "4단계: 점검"
  if [ -x "$py" ]; then
    if "$py" "$target/setup_env.py" --check; then
      ok "Python 패키지·한글 글꼴 점검"
    else
      fail "Python 패키지·한글 글꼴 점검"
    fi
  fi
  if command -v claude >/dev/null 2>&1; then
    ok "Claude Code 버전: $(claude --version 2>/dev/null)"
  fi

  summary "$target"
}

# 함수 전체를 읽은 뒤 실행한다. 하위 설치 프로그램이 표준입력을 읽지 않게 막는다.
main "$@" </dev/null
