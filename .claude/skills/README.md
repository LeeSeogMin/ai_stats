# 수업용 스킬

이 폴더에 수업에서 쓰는 스킬을 넣는다. 강사가 따로 배포한다(PDF 변환, HWPX 변환 등).

## 넣는 방법

스킬 하나는 폴더 하나다. 폴더 안에 `SKILL.md`가 있어야 한다.

```text
.claude/skills/
├── README.md          이 파일
└── <스킬 이름>/
    ├── SKILL.md       스킬 설명과 절차 (맨 위에 name, description)
    └── (스크립트 등)
```

`SKILL.md` 맨 위 형식:

```markdown
---
name: 스킬-이름
description: 이 스킬을 언제 쓰는지 한두 문장
---

# 절차
...
```

Claude Code는 이 폴더의 스킬을 자동으로 읽는다. VS Code의 GitHub Copilot도 로컬 세션에서 `.claude/skills/`를 읽는다(VS Code 공식 문서 「Agent Skills」, 2026-10-31 확인). 스킬을 넣은 뒤에는 Claude Code나 VS Code를 다시 시작한다. 스킬이 있다고 AI가 반드시 쓰는 것은 아니므로, 필요하면 "OO 스킬을 써서"라고 이름을 말해 준다.
