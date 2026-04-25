# ooenv check 체크리스트

> ooenv 스킬 자체 건강 상태 검증 항목
> 템플릿: .claude/templates/oo_checklist_template.md

| ID | 항목 | 검증 내용 | 심각도 |
|----|------|----------|--------|
| C01 | 필수 파일 존재 | SKILL.md 등 핵심 파일 존재 여부 | CRITICAL |
| C02 | 버전 일치 | metadata version <-> 서브명령어 테이블 (vXX) 일치 | ERROR |
| C03 | 환경변수 체크 | PYTHONUTF8 등 필수 변수 설정 | ERROR |
| C06 | API 키 체크 | SKILLSMP_API_KEY 등 선택 변수 존재 | WARNING |
| C04 | uv 설치 확인 | uv 패키지 관리자 설치 여부 | CRITICAL |
| C05 | d0009 파일 존재 | 환경 현황 문서 존재 | ERROR |
| C07 | TEMP/TMP 경로 유효성 | settings.local.json의 TEMP/TMP 경로가 실제 존재하는 디렉토리인지 확인 | ERROR |
| C08 | OMC HUD 스크립트 존재 | ~/.claude/hud/omc-hud.mjs 파일 존재 여부 | ERROR |
| C09 | OMC statusLine 설정 | 글로벌 settings.json의 statusLine이 omc-hud를 가리키는지 확인 | ERROR |
| C10 | 글로벌 settings.json 정리 | permissions/skipDangerousModePermissionPrompt/effortLevel 등 불필요 항목 없어야 함 | WARNING |
| C11 | GSD 로컬 설치 | .claude/commands/gsd/ 존재 여부 (프로젝트 로컬 설치 필수) | WARNING |
| C12 | GSD 글로벌 중복 설치 | ~/.claude/commands/gsd/ 없어야 함 (로컬 전용) | WARNING |
| C13 | OMC 플러그인 활성화 | .claude/settings.local.json의 enabledPlugins에서 oh-my-claudecode@omc가 false면 글로벌 true를 덮어씀 → true로 설정 확인 | ERROR |
| C14 | combined-statusline.js stdin 포워딩 | .claude/hooks/combined-statusline.js에서 execSync로 omc-hud.mjs 호출 시 `input: claudeStdin` 옵션 포함 여부 확인. 없으면 HUD가 "[OMC] run /omc-setup" 출력 | ERROR |
| C15 | jq 설치 여부 | omc-setup 완전 실행에 필요. 없으면 setup-progress.sh complete 실패 → Node.js 대체 필요 (`node -e "..."` 방식) | WARNING |
| C16 | OMC setupCompleted 설정 | ~/.claude/.omc-config.json에 setupCompleted 필드 존재 여부. 없으면 omc-setup 재실행 시 전체 마법사 재실행됨 | WARNING |
| C17 | 환경설정 중복 확인 | CLAUDE.md, settings.json, settings.local.json, .mcp.json 등 모든 환경설정 파일에서 중복된 내용이 있는지 확인 | WARNING |
| C18 | Rust/cargo 설치 | ~/.cargo/bin/cargo.exe 존재 여부 (rustup으로 설치, GNU 타깃: stable-x86_64-pc-windows-gnu) | WARNING |
| C19 | MinGW gcc 설치 | /c/msys64/mingw64/bin/gcc.exe 존재 여부 (Rust GNU toolchain 링커 필수) | WARNING |
| C20 | ~/.bashrc PATH 설정 | ~/.bashrc에 ~/.cargo/bin + /c/msys64/mingw64/bin PATH 등록 여부 | WARNING |

## check 출력 형식

```
[ooenv check]

C01 필수 파일 존재             [OK]
C02 버전 일치                [OK]
C03 환경변수 체크              [OK]
C04 uv 설치 확인             [OK]
C05 d0009 파일 존재          [OK]
C07 TEMP/TMP 경로 유효성      [OK]

소계: OK:N | WARN:N | ERROR:N
```

## 심각도 기준

| 심각도 | 기호 | 의미 |
|--------|------|------|
| CRITICAL | [ERROR] | 스킬 동작 불가 수준 |
| ERROR | [ERROR] | 즉시 수정 필요 |
| WARNING | [WARN] | 권장 수정 |
| INFO | [INFO] | 참고용 |
