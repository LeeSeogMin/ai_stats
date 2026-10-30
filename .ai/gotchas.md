# Gotchas — 반복해서 밟는 함정

같은 실수가 두 번째 나오면 여기에 한 줄로 적는다. 한 번 푼 문제의 자세한 기록은 `.ai/lessons-learned.md`에 남긴다.

## 실행 결과

- 숫자는 `scripts/run_and_capture.py`로 실행한 로그(`outputs/results/*.log`)에서만 가져온다. 로그가 없는 숫자는 쓰지 않는다.
- 코드를 고친 뒤에는 다시 실행한다. `python scripts/harness.py`가 낡은 결과를 잡는다.

## 환경

- Python은 `.venv` 안의 것만 쓴다 (Windows `.venv\Scripts\python.exe`, macOS `.venv/bin/python`).
- 패키지 버전을 올리지 않는다. Windows 스마트 앱 컨트롤이 최신 패키지를 막아 import가 실패한다(`.ai/lessons-learned.md` 2026-09-12).
- 코드는 프로젝트 최상위에서 실행한다. 다른 폴더에서 실행하면 그래프의 한글이 네모(□)로 나온다.

## 분석

- 평균만 보고 결론 내지 않는다. 중앙값과 분포(그래프)를 함께 본다.
- 빠진 값(결측)을 몇 개 뺐는지 적는다.
- 같이 움직이는 두 값(상관)을 원인과 결과(인과)로 쓰지 않는다.
