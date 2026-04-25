---
name: ccusage
description: "GitHub 계정 사용량과 Copilot 사용량을 함께 조사해 요약할 때 사용한다. GitHub billing, usage, metered usage, Copilot usage, Copilot premium requests, Actions, Codespaces, Packages, Git LFS, 저장용량, storage usage, 과금, 포함 사용량, billed amount 조회 요청에 적합하다. `run` 서브명령어는 이번 달 GitHub+Copilot 사용량과 남은 포함량을 표시한다."
argument-hint: "run | storage | current month | copilot only | github + copilot"
user-invocable: true
---

# ccusage

## What It Does

- GitHub 계정의 billing/usage 정보를 조사한다.
- Copilot 사용량과 GitHub 자체 사용량을 한 번에 정리한다.
- 포함 사용량, 실제 청구 금액, 현재 플랜을 구분해서 보여준다.
- 확인 가능한 범위의 저장용량 사용량을 함께 정리한다.
- `run` 서브명령어로 이번 달 GitHub+Copilot 사용량과 남은 포함량을 우선 표시한다.

## Subcommands

- `run`: 이번 달 기준으로 GitHub 전체 사용량과 Copilot 사용량을 함께 조사하고, 확인 가능한 범위에서 남은 포함량까지 계산해 보여준다.
- `storage`: storage 관련 사용량을 우선 표시한다. Codespaces storage, Packages storage, Actions artifact/cache storage, Git LFS 같은 billing storage와 일반 repository 크기를 구분해서 설명한다.
- `repos`: 현재 인증된 GitHub 계정이 소유한 repository 목록을 표시한다. 공개/비공개, fork 여부, 최근 업데이트 시각을 함께 보여준다.

## When To Use

- 사용자가 "github 사용량 보여줘", "copilot 사용량 확인", "billing 확인", "이번 달 과금 얼마야"처럼 묻는 경우
- 사용자가 "저장용량 얼마나 썼어", "storage usage 확인", "LFS 용량", "Codespaces storage", "Packages storage"를 묻는 경우
- 사용자가 "내 repo 보여줘", "repository 목록", "repo list", "내 저장소 리스트업"처럼 묻는 경우
- GitHub Pro, Copilot Pro, metered usage, included usage, billed amount를 함께 확인해야 하는 경우
- CLI 인증이 없어서 웹 청구 페이지까지 포함한 우회 확인이 필요한 경우

## Procedure

1. 사용자가 `run`을 붙였으면 기본 범위를 `이번 달 GitHub + Copilot`으로 고정한다.
2. 사용자가 `storage`를 붙였으면 storage 관련 사용량을 우선 조사한다.
3. 사용자가 `repos`를 붙였으면 현재 인증된 계정의 repository 목록을 우선 조사한다.
4. 먼저 [ccusage_run.py](./scripts/ccusage_run.py)를 실행해 GitHub CLI 인증 여부와 공개 billing API 결과를 확인한다.
5. `repos` 모드에서는 `gh repo list <owner>` 기반으로 repository 목록을 정리한다.
6. 인증되어 있으면 스크립트가 `gh api /user/settings/billing/usage/summary` 같은 billing API 결과를 정리한다.
7. 인증이 없거나 API가 실패하면 GitHub billing 페이지를 브라우저로 열어 플랜, metered usage, billed amount, Copilot usage를 읽는다.
   - overview: `https://github.com/settings/billing/summary`
   - usage: `https://github.com/settings/billing/usage?period=3&group=0`
8. 반드시 다음 항목을 구분해서 정리한다.
   - 현재 구독 플랜
   - GitHub 전체 metered usage
   - included usage 또는 할인으로 상쇄된 금액
   - billed amount
   - Copilot usage
   - Copilot premium requests
   - 확인 가능한 storage usage
9. `run`에서는 확인 가능한 범위에서 남은 포함량도 계산한다.
   - billed amount가 0이고 included usage가 동일 금액으로 보이면 `현재 포함량 내 사용`으로 해석한다.
   - 화면이나 API에 남은 수치가 직접 없으면 `남은 포함량은 화면상 직접 제공되지 않음`이라고 명시한다.
   - Codespaces, Actions, LFS처럼 별도 quota가 있는 항목은 숫자가 보일 때만 남은 양을 계산한다.
10. 가능하면 제품별 사용량도 확인한다.

- Actions
- Codespaces
- Git LFS
- Packages
- Copilot
- Models

11. 저장용량 질문이 포함되면 아래를 구분해서 답한다.

- billing 대상 storage: Codespaces storage, Packages storage, Actions artifact/cache storage, Git LFS storage/bandwidth
- 일반 repository 자체 크기: billing quota가 아니라 저장소 크기/권장치 관점이라고 명시한다.
- 로컬 저장소 크기가 필요하면 `git count-objects -vH` 같은 로컬 git 크기 확인 결과를 참고한다.

12. repository 목록 질문이 포함되면 아래를 구분해서 답한다.

- owner 기준 repository 목록인지 명시한다.
- private/public 여부를 구분한다.
- fork 여부를 함께 적는다.

13. 최종 응답은 짧고 명확하게 작성한다.

## Output Format

- 현재 플랜
- 이번 달 GitHub 총 사용량
- 이번 달 Copilot 사용량
- 실제 청구 금액
- 포함 사용량으로 상쇄된 금액
- 남은 포함량 또는 남은 포함량 계산 가능 여부
- storage usage 또는 storage 조사 가능 여부
- Copilot 관련 사용량
- 필요 시 repository 목록
- 필요 시 제품별 세부 사용량

## Rules

- GitHub 사용량과 Copilot 사용량을 분리해서 보여준다.
- "사용량이 있다"와 "실제 과금이 발생했다"를 혼동하지 않는다.
- `run`이면 기본적으로 `이번 달` 기준으로 응답한다.
- 스크립트 출력이 연간 aggregate API 기준이면 그 사실을 숨기지 말고, 현재 달의 정확한 billed amount와 included usage는 웹 화면 fallback으로 보완한다.
- 남은 포함량을 정확히 계산할 근거가 없으면 추정값을 만들지 말고 불명확하다고 적는다.
- storage는 billing storage와 repository size를 혼동하지 않는다.
- repository 자체 크기는 과금 quota처럼 설명하지 않는다.
- repository 목록은 현재 인증된 owner 기준이라는 점을 숨기지 않는다.
- CLI 결과와 웹 화면 결과가 다르면 그 차이를 명시한다.
- 인증이 없어서 API를 못 쓰는 경우 그 사실을 숨기지 않는다.
- 숫자가 보이면 기간도 함께 적는다.

## Example Prompts

- `/ccusage run`
- `/ccusage run current month`
- `/ccusage current month`
- `/ccusage copilot only`
- `/ccusage github + copilot`
- `/ccusage storage`
- `/ccusage repos`
- `github 저장용량 사용량 보여줘`
- `이번 달 github랑 copilot 사용량 같이 보여줘`
- `copilot premium request 얼마나 썼는지 확인해줘`
- `내 repo 리스트업해줘`
