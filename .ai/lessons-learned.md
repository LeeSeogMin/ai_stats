# Lessons Learned — 문제와 해결 기록

## 기록 형식

```text
## YYYY-MM-DD: 주제
### 상황
[무엇이 문제였나]
### 해결책
[어떻게 풀었나]
### 규칙
- [다음에 지킬 것]
```

## 2026-09-12: Windows 스마트 앱 컨트롤이 최신 패키지를 막는다 (geoAI 과목에서 옮겨 온 기록)

### 상황

Windows의 스마트 앱 컨트롤이 켜진 컴퓨터에서 `pip install`은 성공했는데 import가 실패했다. 메시지는 `DLL load failed ... 애플리케이션 제어 정책에서 이 파일을 차단했습니다`였다. 차단된 버전: pandas 3.0.5, matplotlib 3.11.2, statsmodels 0.15.0.

### 해결책

한두 단계 낮은 안정 버전(pandas 2.3.3, matplotlib 3.9.4, statsmodels 0.14.6, numpy 2.2.6)으로 고정했다. 스마트 앱 컨트롤은 끄지 않았다. 끄면 다시 켤 수 없고 컴퓨터 전체의 보호가 낮아진다.

### 규칙

- `requirements.txt`의 버전을 올리지 않는다.
- 설치 성공은 검증이 아니다. import까지 확인한다(`python setup_env.py --check`).
