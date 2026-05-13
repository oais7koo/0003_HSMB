import sys
import subprocess
import os
import platform
from datetime import datetime

LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../00_doc/yyy.md")
)


def log_section(title, content):
    return f"\n### {title}\n```\n{content.strip()}\n```\n"


def main():
    if len(sys.argv) < 2:
        print("[ggrun] 실행할 명령어를 입력하세요.")
        sys.exit(1)
    cmd = sys.argv[1:]
    start_time = datetime.now()
    env_info = f"OS: {platform.system()} {platform.release()} | Python: {platform.python_version()} | venv: {os.environ.get('VIRTUAL_ENV', 'N/A')}"
    cwd = os.getcwd()

    # 파일 읽기 명령어라면 Python에서 직접 처리
    is_file_read = False
    if (cmd[0] in ["cat", "type"]) and len(cmd) > 1:
        file_path = cmd[1]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                stdout = f.read()
            stderr = ""
            code = 0
            is_file_read = True
        except Exception as e:
            stdout = ""
            stderr = str(e)
            code = -1
            is_file_read = True
    if not is_file_read:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            code = proc.returncode
            stdout = proc.stdout
            stderr = proc.stderr
        except Exception as e:
            code = -1
            stdout = ""
            stderr = str(e)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # 작업 내용 요약 생성
    def summarize_action(cmd, stdout, stderr):
        cmd_str = " ".join(cmd)
        if cmd[0] in ["cat", "type"] and len(cmd) > 1:
            return f"- 작업 내용: 파일 `{cmd[1]}`의 내용을 읽어 출력함. 주요 내용 일부:\n\n" + (
                stdout[:300] + ("..." if len(stdout) > 300 else "")
            )
        if cmd[0] in ["ls", "dir"]:
            return f"- 작업 내용: 디렉토리 목록 조회. 결과 파일/폴더 수: {len(stdout.splitlines())}"
        if "pytest" in cmd_str:
            return f"- 작업 내용: 테스트 실행 결과. {'실패 있음' if 'FAIL' in stdout or 'FAIL' in stderr else '모든 테스트 통과'}"
        if "build" in cmd_str or "make" in cmd_str:
            return f"- 작업 내용: 빌드/컴파일 명령 실행. 로그 참조."
        if code != 0:
            return f"- 작업 내용: 명령 실행 중 오류 발생. STDERR 참조."
        return f"- 작업 내용: 명령 '{cmd_str}' 실행. 상세 결과는 아래 로그 참조."

    action_summary = summarize_action(cmd, stdout, stderr)

    # 로그 작성
    log = f"## [{start_time.strftime('%Y-%m-%d %H:%M:%S')}] ggrun: {' '.join(cmd)}\n"
    log += f"- 실행 환경: {env_info}\n"
    log += f"- 명령어: {' '.join(cmd)}\n"
    log += f"- 실행 디렉토리: {cwd}\n"
    log += f"- 종료 코드: {code}\n"
    log += f"- 실행 시간: {duration:.2f}초\n"
    log += action_summary + "\n"
    log += log_section("STDOUT", stdout)
    log += log_section("STDERR", stderr)
    log += "\n---\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log)
    print(f"[ggrun] 로그가 {LOG_PATH}에 저장되었습니다.")


if __name__ == "__main__":
    main()
