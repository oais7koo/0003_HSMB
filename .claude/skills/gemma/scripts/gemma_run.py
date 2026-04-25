#!/usr/bin/env python3
"""
gemma_run.py - 로컬 Gemma4 SLM 에이전트 스크립트 (mlx-lm, localhost:8080)
Usage: uv run python .claude/skills/gemma/scripts/gemma_run.py [help|version|status|run|models] ["프롬프트"]
"""
import sys
import re as _re
from pathlib import Path

# scripts 디렉토리를 import path에 추가 (gemma_log 임포트용)
sys.path.insert(0, str(Path(__file__).resolve().parent))

# --- oo_common inline ---
_SKILLS_DIR = Path(__file__).parent.parent.parent


def _print_skill_help(skill_name):
    if sys.stdout.encoding and sys.stdout.encoding.lower() in ("cp949", "cp1252", "ascii"):
        sys.stdout.reconfigure(encoding="utf-8")
    _sf = _SKILLS_DIR / skill_name / "SKILL.md"
    if not _sf.exists():
        print(f"[ERROR] .claude/skills/{skill_name}/SKILL.md not found")
        return
    _c = _sf.read_text(encoding="utf-8")
    _m = _re.search(r"##[^\n]*(?:서브명령어|명령어)\n\n((?:\|.+\n)+)", _c)
    if _m:
        print(f"`{skill_name} help` 서브명령어 목록:\n")
        print(_m.group(1).strip())
    else:
        print(f"[WARN] 서브명령어 섹션 없음: {skill_name}/SKILL.md")


def show_help_if_no_args(skill_name, args):
    if not args or args[0].lower() in ("help", "-h", "--help"):
        _print_skill_help(skill_name)
        return True
    return False
# --- end oo_common inline ---

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SKILL_NAME = "gemma"
VERSION = "v03"

# 서버 설정
BASE_URL = "http://localhost:8080/v1"
API_KEY = "local"  # mlx-lm은 인증 불필요, 임의값 사용

# 모델: last_model.json (컴퓨터별 마지막 선택) → 없으면 기본값
_DEFAULT_MODEL = "gemma4:e4b"
_LAST_MODEL_FILE = Path(__file__).parent.parent / "references" / "last_model.json"
_COMPUTER = __import__("os").environ.get("COMPUTERNAME", "")

def _load_model() -> str:
    if _LAST_MODEL_FILE.exists() and _COMPUTER:
        try:
            import json
            data = json.loads(_LAST_MODEL_FILE.read_text(encoding="utf-8"))
            return data.get(_COMPUTER) or _DEFAULT_MODEL
        except Exception:
            pass
    return _DEFAULT_MODEL

MODEL = _load_model()

# 화이트리스트: oo 스킬 → gemma 위임 허용 목록
_WHITELIST_FILE = Path(__file__).parent.parent / "references" / "skill_whitelist.json"


def _load_whitelist() -> dict:
    """oo 스킬 화이트리스트 로드. {스킬명: 용도설명}"""
    if not _WHITELIST_FILE.exists():
        return {}
    try:
        import json
        data = json.loads(_WHITELIST_FILE.read_text(encoding="utf-8"))
        return data.get("whitelist", {})
    except Exception:
        return {}


WHITELIST = _load_whitelist()

SYSTEM_PROMPT = (
    "You are a helpful AI assistant powered by Gemma4 running locally via mlx-lm. "
    "Answer concisely and accurately. "
    "한국어로 질문하면 한국어로 답변하세요."
)


def _get_client():
    """OpenAI 클라이언트 초기화 (mlx-lm 호환)"""
    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] openai 패키지 미설치. 다음 명령으로 설치하세요:")
        print("  uv add openai")
        sys.exit(1)
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)


def cmd_version():
    print(f"[{SKILL_NAME}] 버전: {VERSION}")


def cmd_status():
    """서버 연결 상태 확인"""
    print(f"[{SKILL_NAME} status]")
    print(f"  엔드포인트: {BASE_URL}")
    print(f"  모델: {MODEL}")
    try:
        client = _get_client()
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        print(f"  서버 상태: OK")
        print(f"  사용 가능한 모델: {', '.join(model_ids) if model_ids else '(없음)'}")
    except Exception as e:
        print(f"  서버 상태: ERROR")
        print(f"  오류: {e}")
        print(f"\n  mlx-lm 서버를 먼저 시작하세요:")
        print(f"  uv run mlx_lm.server --model <모델명> --port 8080")


def cmd_whitelist():
    """위임 허용 oo 스킬 화이트리스트 표시"""
    print(f"[{SKILL_NAME} whitelist] 위임 허용 oo 스킬")
    print(f"  파일: {_WHITELIST_FILE}")
    if not WHITELIST:
        print(f"  (등록된 스킬 없음)")
        return
    print(f"  총 {len(WHITELIST)}개\n")
    print(f"  {'스킬':<14} 용도")
    print(f"  {'-' * 14} {'-' * 40}")
    for name, desc in WHITELIST.items():
        print(f"  {name:<14} {desc}")
    print(f"\n  사용: gemma <스킬명> \"프롬프트\"")


def cmd_models():
    """사용 가능한 모델 목록 조회"""
    print(f"[{SKILL_NAME} models] {BASE_URL}")
    try:
        client = _get_client()
        models = client.models.list()
        if not models.data:
            print("  (서버에 로드된 모델 없음)")
            return
        for m in models.data:
            print(f"  - {m.id}")
    except Exception as e:
        print(f"[ERROR] 모델 목록 조회 실패: {e}")


def _chat_once(client, prompt: str, history: list, caller: str | None = None) -> str:
    """단일 추론 (스트리밍) + 로그 append"""
    import time

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})

    print(f"\n[Gemma4] ", end="", flush=True)
    full_response = ""
    t0 = time.monotonic()
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=2048,
            extra_body={"options": {"think": False}},
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full_response += delta
        print()  # 줄바꿈
    except Exception as e:
        print(f"\n[ERROR] 추론 실패: {e}")
    finally:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        try:
            from gemma_log import append_log
            append_log(
                caller=caller or __import__("os").environ.get("GEMMA_CALLER"),
                model=MODEL,
                prompt=prompt,
                response=full_response,
                elapsed_ms=elapsed_ms,
            )
        except Exception:
            pass
    return full_response


def cmd_run(prompt_arg: str | None = None):
    """
    실행 모드:
    - prompt_arg가 있으면 단일 추론 후 종료
    - 없으면 인터랙티브 채팅 모드
    """
    client = _get_client()

    # 단일 프롬프트 모드
    if prompt_arg:
        print(f"[{SKILL_NAME}] 단일 추론 모드")
        print(f"[You] {prompt_arg}")
        _chat_once(client, prompt_arg, [])
        return

    # 인터랙티브 채팅 모드
    print(f"[{SKILL_NAME}] 인터랙티브 채팅 모드 (종료: 'exit' 또는 Ctrl+C)")
    print(f"  모델: {MODEL} @ {BASE_URL}")
    print(f"  시스템: {SYSTEM_PROMPT[:60]}...")
    print("-" * 50)

    history = []
    while True:
        try:
            user_input = input("\n[You] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n[gemma] 채팅 종료.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "종료", "q"):
            print("[gemma] 채팅 종료.")
            break
        if user_input.lower() in ("clear", "초기화"):
            history.clear()
            print("[gemma] 대화 이력 초기화됨.")
            continue

        response = _chat_once(client, user_input, history)
        if response:
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})


def _extract_caller(args: list[str]) -> tuple[str | None, list[str]]:
    """--caller <skill> / -c <skill> 인자 추출 → (caller, 잔여 args)"""
    caller = None
    out: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--caller", "-c") and i + 1 < len(args):
            caller = args[i + 1]
            i += 2
            continue
        if a.startswith("--caller="):
            caller = a.split("=", 1)[1]
            i += 1
            continue
        out.append(a)
        i += 1
    return caller, out


def main():
    args = sys.argv[1:]
    if show_help_if_no_args(SKILL_NAME, args):
        return

    # --caller 선추출 후 남은 args로 일반 파싱
    caller, args = _extract_caller(args)

    cmd = args[0].lower() if args else ""

    if cmd == "version":
        cmd_version()
    elif cmd == "status":
        cmd_status()
    elif cmd == "models":
        cmd_models()
    elif cmd == "log":
        from gemma_log import cmd_log
        cmd_log(args[1:])
    elif cmd == "run":
        prompt = " ".join(args[1:]).strip() if len(args) > 1 else None
        # caller를 환경변수로도 주입 (하위 호출 경로 일관성)
        if caller:
            __import__("os").environ["GEMMA_CALLER"] = caller
        if prompt:
            client = _get_client()
            _chat_once(client, prompt, [], caller=caller)
        else:
            cmd_run(None)
    elif cmd == "check":
        print(f"[{SKILL_NAME}] references/checklist.md 체크")
        checklist_path = Path(__file__).parent.parent / "references" / "checklist.md"
        if checklist_path.exists():
            print(checklist_path.read_text(encoding="utf-8"))
        else:
            print("[WARN] checklist.md 없음")
    elif cmd in ("whitelist", "wl"):
        cmd_whitelist()
    elif cmd in WHITELIST:
        # 화이트리스트 oo 스킬: gemma <skill> "프롬프트" → caller 자동 기록
        sub_caller = cmd
        prompt = " ".join(args[1:]).strip()
        if not prompt:
            print(f"[{SKILL_NAME}] {sub_caller}: 프롬프트가 비어있습니다.")
            print(f"  용도: {WHITELIST[sub_caller]}")
            print(f"  사용: gemma {sub_caller} \"프롬프트\"")
            return
        print(f"[{SKILL_NAME}] {sub_caller} 위임 추론 ({WHITELIST[sub_caller]})")
        print(f"[You] {prompt}")
        client = _get_client()
        _chat_once(client, prompt, [], caller=sub_caller)
    elif cmd.startswith("oo") and cmd not in WHITELIST:
        # oo 스킬 형태인데 화이트리스트 미등록 → 거부
        print(f"[ERROR] '{cmd}'는 gemma 화이트리스트에 없습니다.")
        print(f"  허용 목록 확인: gemma whitelist")
        print(f"  자유 프롬프트는: gemma run \"프롬프트\" 또는 gemma --caller {cmd} \"프롬프트\"")
        sys.exit(2)
    else:
        prompt = " ".join(args).strip()
        if not prompt:
            _print_skill_help(SKILL_NAME)
            return
        print(f"[{SKILL_NAME}] 프롬프트 모드 (단일 추론)")
        client = _get_client()
        _chat_once(client, prompt, [], caller=caller)


if __name__ == "__main__":
    main()
