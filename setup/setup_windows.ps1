# 「AI를 활용한 통계」 특강 — Windows 자동 설치 스크립트
#
# 학생이 미리 해 둘 것: VS Code 설치, GitHub 가입, 메일로 받은 실습 zip 압축 풀기(권장 위치 C:\ai_stats)
# 실행 방법: 압축 푼 폴더의 setup\install_windows.cmd 를 더블클릭
#
# 이 스크립트가 하는 일:
#   1. 실습 폴더 확인 (이 파일이 들어 있는 압축 푼 폴더를 그대로 쓴다)
#   2. uv 설치 → Python 3.12 + 실습 패키지 설치
#   3. Claude Code 설치 (설치는 무료, 사용하려면 Claude Pro 로그인 필요)
#   4. Git for Windows 설치 (선택 항목, 실패해도 수업 가능)
#   5. 점검
# VS Code 확장은 1교시에 함께 설치한다(.vscode\extensions.json).
# 이미 설치된 항목은 건너뛴다. 여러 번 실행해도 된다.
# 관리자 권한은 필요 없다(Git 설치 때만 Windows가 허용 여부를 물을 수 있다).
#
# 이 파일은 UTF-8(BOM 포함)으로 저장해야 Windows PowerShell 5.1에서 한글이 깨지지 않는다.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'   # 진행 막대를 끄면 Windows PowerShell 5.1의 다운로드가 훨씬 빠르다
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$OrigEncoding = [Console]::OutputEncoding
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
# 하위 PowerShell에도 같은 다운로드 설정을 넘긴다.
$ChildPrefix = "`$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; "

$LocalBin = Join-Path $HOME '.local\bin'

$script:Results = New-Object System.Collections.Generic.List[string]
$script:Failed = 0

function Say($msg)  { Write-Host ''; Write-Host "▶ $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "  [성공] $msg" -ForegroundColor Green;  $script:Results.Add("[성공] $msg") }
function Skip($msg) { Write-Host "  [건너뜀] $msg" -ForegroundColor DarkCyan; $script:Results.Add("[건너뜀] $msg") }
function Warn($msg) { Write-Host "  [주의] $msg" -ForegroundColor Yellow; $script:Results.Add("[주의] $msg") }
function Fail($msg) { Write-Host "  [실패] $msg" -ForegroundColor Red;    $script:Results.Add("[실패] $msg"); $script:Failed++ }

function Has($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

function Add-ToPath($dir) {
    # 현재 창과 새로 여는 창 모두에서 프로그램을 찾을 수 있게 PATH에 등록한다.
    if (-not (($env:Path -split ';') -contains $dir)) { $env:Path = "$dir;$env:Path" }
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if (-not $userPath) { $userPath = '' }
    if (-not (($userPath -split ';') -contains $dir)) {
        [Environment]::SetEnvironmentVariable('Path', ($dir + ';' + $userPath).TrimEnd(';'), 'User')
    }
}

function Show-Summary($target) {
    Write-Host ''
    Write-Host '=================================================='
    Write-Host ' 설치 결과'
    Write-Host '=================================================='
    foreach ($r in $script:Results) { Write-Host "  $r" }
    Write-Host ''
    if ($script:Failed -eq 0) {
        Write-Host '모든 설치를 마쳤습니다. 이 화면을 캡처해서 회신해 주세요.' -ForegroundColor Green
        Write-Host 'VS Code 확장 설치와 Copilot·Claude 로그인은 1교시에 함께 합니다.'
        Write-Host "실습 폴더: $target"
    }
    else {
        Write-Host "실패한 항목이 $($script:Failed) 개 있습니다. 이 화면을 캡처해서 조교에게 보내 주세요." -ForegroundColor Red
        Write-Host '스크립트는 여러 번 실행해도 됩니다. 문제를 고친 뒤 다시 실행하세요.'
    }
    try { [Console]::OutputEncoding = $OrigEncoding } catch {}
}

Write-Host '=================================================='
Write-Host ' 「AI를 활용한 통계」 실습 환경 자동 설치 (Windows)'
Write-Host '=================================================='

# ---------------------------------------------------------------- 0. VS Code
Say '0단계: VS Code 확인'
$codeFound = (Has 'code') -or
    (Test-Path (Join-Path $env:LOCALAPPDATA 'Programs\Microsoft VS Code\Code.exe')) -or
    (Test-Path (Join-Path $env:ProgramFiles 'Microsoft VS Code\Code.exe'))
if ($codeFound) { Ok 'VS Code 찾음' }
else { Fail 'VS Code를 찾지 못함 — https://code.visualstudio.com 에서 설치한 뒤 다시 실행하세요' }

# ---------------------------------------------------------------- 1. 실습 폴더
Say '1단계: 실습 폴더 확인'
$Target = $null
if ($PSScriptRoot) { $Target = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path }
if (-not $Target -or -not (Test-Path (Join-Path $Target 'setup_env.py')) -or -not (Test-Path (Join-Path $Target 'requirements.txt'))) {
    Fail "실습 폴더가 아닙니다: $Target — 메일로 받은 zip의 압축을 모두 푼 뒤, 그 안의 setup\install_windows.cmd 를 실행하세요"
    Show-Summary $Target
    return
}
Ok "실습 폴더: $Target"
if ($Target -match '[^\x00-\x7F]' -or $Target -match 'OneDrive') {
    Warn '폴더 경로에 한글 또는 OneDrive가 있습니다. 오류가 나면 폴더를 C:\ai_stats 로 옮긴 뒤 다시 실행하세요'
}

# ---------------------------------------------------------------- 2. uv + Python
Say '2단계: Python과 실습 패키지 설치'
Add-ToPath $LocalBin
if (Has 'uv') { Skip 'uv 이미 설치됨' }
else {
    powershell -NoProfile -ExecutionPolicy Bypass -Command ($ChildPrefix + 'irm https://astral.sh/uv/install.ps1 | iex') | Out-Null
    if (Has 'uv') { Ok 'uv 설치' } else { Fail 'uv 설치 실패 — 인터넷 연결을 확인하세요' }
}

$VenvPython = Join-Path $Target '.venv\Scripts\python.exe'
if (Has 'uv') {
    if (Test-Path $VenvPython) { Skip '가상환경(.venv) 이미 있음' }
    else {
        uv venv --python 3.12 (Join-Path $Target '.venv') | Out-Null
        if ($LASTEXITCODE -eq 0 -and (Test-Path $VenvPython)) { Ok 'Python 3.12 가상환경 생성' }
        else { Fail '가상환경 생성 실패' }
    }
    if (Test-Path $VenvPython) {
        uv pip install --python $VenvPython -r (Join-Path $Target 'requirements.txt')
        if ($LASTEXITCODE -eq 0) { Ok '실습 패키지 설치' } else { Fail '실습 패키지 설치 실패' }
    }
}

# ---------------------------------------------------------------- 3. Claude Code
Say '3단계: Claude Code 설치 (권장 도구)'
if (Has 'claude') { Skip 'Claude Code 이미 설치됨' }
else {
    powershell -NoProfile -ExecutionPolicy Bypass -Command ($ChildPrefix + 'irm https://claude.ai/install.ps1 | iex')
    Add-ToPath $LocalBin
    if (Has 'claude') { Ok 'Claude Code 설치 (사용하려면 Claude Pro 로그인 필요)' }
    else { Warn 'Claude Code 설치 실패 — 기본 도구인 Copilot으로 수업할 수 있습니다' }
}

# ---------------------------------------------------------------- 4. Git (선택)
Say '4단계: Git for Windows 설치 (선택 항목)'
if (Has 'git') { Skip 'Git 이미 설치됨' }
elseif (Has 'winget') {
    Write-Host '  Windows가 설치 허용 여부를 물으면 [예]를 누르세요.'
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
    $gitCmd = Join-Path $env:ProgramFiles 'Git\cmd'
    if (Test-Path $gitCmd) { Add-ToPath $gitCmd }
    if (Has 'git') { Ok 'Git 설치' } else { Warn 'Git 설치 실패 — 수업 진행에는 지장이 없습니다' }
}
else { Warn 'winget이 없어 Git을 설치하지 못함 — 수업 진행에는 지장이 없습니다' }

# ---------------------------------------------------------------- 5. 점검
Say '5단계: 점검'
if (Test-Path $VenvPython) {
    & $VenvPython (Join-Path $Target 'setup_env.py') --check
    if ($LASTEXITCODE -eq 0) { Ok 'Python 패키지·한글 글꼴 점검' } else { Fail 'Python 패키지·한글 글꼴 점검' }
}
if (Has 'claude') { Ok ("Claude Code 버전: " + (claude --version 2>$null)) }

Show-Summary $Target
