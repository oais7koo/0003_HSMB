"""ccsync ftp - SP별 FTP 동기화 스크립트"""
import ftplib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Windows cp949 인코딩 이슈 방지
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 프로젝트 루트 (ccsync 스킬 기준 4단계 상위)
PROJECT_ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = PROJECT_ROOT / ".codex" / "skills" / "ccsync" / "references" / "ftp_config.json"
ENV_PATH = PROJECT_ROOT / ".env"


def load_env() -> dict[str, str]:
    """프로젝트 .env 파일에서 환경변수 로드"""
    env_vars: dict[str, str] = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env_vars[key.strip()] = val.strip()
    return env_vars


def load_config() -> dict:
    """FTP config 로드"""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] 설정 파일 없음: {CONFIG_PATH}")
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def get_password(profile: dict, config: dict, env_vars: dict) -> str:
    """프로필에서 비밀번호 조회 (프로필 개별 > 기본값)"""
    pw_env = profile.get("password_env") or config.get("default_password_env", "FTP_PASS")
    password = env_vars.get(pw_env, "") or os.environ.get(pw_env, "")
    if not password:
        print(f"[ERROR] 비밀번호 없음: .env에 {pw_env} 설정 필요")
        sys.exit(1)
    return password


def connect_ftp(profile: dict, password: str) -> ftplib.FTP:
    """FTP 접속"""
    ftp = ftplib.FTP()
    ftp.connect(profile["host"], profile.get("port", 21), timeout=10)
    ftp.login(profile["user"], password)
    ftp.encoding = profile.get("encoding", "utf-8")
    return ftp


def get_remote_files(ftp: ftplib.FTP, remote_dir: str, base: str = "") -> list[dict]:
    """리모트 디렉토리의 파일 목록을 재귀적으로 수집 (단일 파일도 처리)"""
    files = []
    try:
        # list()로 즉시 실행 (mlsd는 generator라 지연 실행됨)
        items = list(ftp.mlsd(remote_dir))
    except ftplib.error_perm as e:
        # 단일 파일인 경우 (디렉토리가 아닌 경우)
        err_msg = str(e).lower()
        if "not a directory" in err_msg or "is not a" in err_msg:
            try:
                size = ftp.size(remote_dir)
                return [{"name": base or remote_dir.rsplit("/", 1)[-1], "type": "file", "size": size or 0, "modify": ""}]
            except ftplib.error_perm:
                return [{"name": base or remote_dir.rsplit("/", 1)[-1], "type": "file", "size": 0, "modify": ""}]
        # mlsd 미지원 시 nlst 폴백
        try:
            names = ftp.nlst(remote_dir)
        except ftplib.error_perm:
            return files
        for name in names:
            basename = name.rsplit("/", 1)[-1] if "/" in name else name
            if basename in (".", ".."):
                continue
            rel = f"{base}/{basename}" if base else basename
            files.append({"name": rel, "type": "unknown", "size": 0})
        return files

    for name, facts in items:
        if name in (".", ".."):
            continue
        rel = f"{base}/{name}" if base else name
        entry_type = facts.get("type", "file")
        if entry_type == "dir":
            files.extend(get_remote_files(ftp, f"{remote_dir}/{name}", rel))
        else:
            size = int(facts.get("size", 0))
            modify = facts.get("modify", "")
            files.append({"name": rel, "type": "file", "size": size, "modify": modify})
    return files


def get_local_files(local_dir: Path, targets: list[str]) -> list[dict]:
    """로컬 디렉토리의 파일 목록 수집 (targets 기준)"""
    files = []
    for target in targets:
        target_path = local_dir / target
        if target_path.is_file():
            stat = target_path.stat()
            files.append({
                "name": target,
                "type": "file",
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y%m%d%H%M%S"),
            })
        elif target_path.is_dir():
            for fp in sorted(target_path.rglob("*")):
                if fp.is_file():
                    rel = fp.relative_to(local_dir).as_posix()
                    stat = fp.stat()
                    files.append({
                        "name": rel,
                        "type": "file",
                        "size": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y%m%d%H%M%S"),
                    })
    return files


def resolve_profiles(config: dict, sp_arg: str | None) -> list[tuple[str, dict]]:
    """SP 인자에 따라 프로필 목록 반환"""
    profiles = config["profiles"]
    if sp_arg:
        key = sp_arg.upper()
        if key not in profiles:
            print(f"[ERROR] 프로필 없음: {key}")
            print(f"  사용 가능: {', '.join(profiles.keys())}")
            sys.exit(1)
        return [(key, profiles[key])]
    return list(profiles.items())


# ── 서브커맨드 ──────────────────────────────────────────────


def cmd_status(config: dict, env_vars: dict, sp_arg: str | None):
    """FTP 접속 테스트 + 요약"""
    print("# ccsync ftp status\n")
    items = resolve_profiles(config, sp_arg)

    for sp_key, profile in items:
        print(f"## {sp_key} — {profile['name']}")
        print(f"  호스트: {profile['host']}")
        print(f"  계정:  {profile['user']}")
        print(f"  리모트: {profile['remote_root']}")
        local_dir = PROJECT_ROOT / profile["local_dir"]
        print(f"  로컬:  {profile['local_dir']}/ ({'존재' if local_dir.exists() else '없음'})")

        password = get_password(profile, config, env_vars)
        try:
            ftp = connect_ftp(profile, password)
            print(f"  접속:  OK — {ftp.getwelcome()}")
            ftp.quit()
        except Exception as e:
            print(f"  접속:  FAIL — {e}")
        print()


def cmd_list(config: dict, env_vars: dict, sp_arg: str | None):
    """리모트 파일 목록"""
    print("# ccsync ftp list\n")
    items = resolve_profiles(config, sp_arg)

    for sp_key, profile in items:
        password = get_password(profile, config, env_vars)
        print(f"## {sp_key} — {profile['name']} ({profile['host']}:{profile['remote_root']})\n")
        try:
            ftp = connect_ftp(profile, password)
            remote_root = profile["remote_root"]
            for target in profile["targets"]:
                remote_path = f"{remote_root.rstrip('/')}/{target}"
                rfiles = get_remote_files(ftp, remote_path, target)
                if rfiles:
                    for rf in rfiles:
                        size_str = f"{rf['size']:>8,}" if rf.get("size") else "       ?"
                        print(f"  {size_str}  {rf['name']}")
                else:
                    print(f"  (비어있음) {target}")
            ftp.quit()
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()


def cmd_diff(config: dict, env_vars: dict, sp_arg: str | None):
    """로컬 vs 리모트 비교"""
    print("# ccsync ftp diff\n")
    items = resolve_profiles(config, sp_arg)

    for sp_key, profile in items:
        password = get_password(profile, config, env_vars)
        local_dir = PROJECT_ROOT / profile["local_dir"]
        print(f"## {sp_key} — {profile['name']}\n")

        if not local_dir.exists():
            print(f"  [WARN] 로컬 디렉토리 없음: {profile['local_dir']}")
            print()
            continue

        local_files = get_local_files(local_dir, profile["targets"])
        local_map = {f["name"]: f for f in local_files}

        try:
            ftp = connect_ftp(profile, password)
            remote_root = profile["remote_root"]
            remote_files = []
            for target in profile["targets"]:
                remote_path = f"{remote_root.rstrip('/')}/{target}"
                remote_files.extend(get_remote_files(ftp, remote_path, target))
            ftp.quit()
        except Exception as e:
            print(f"  [ERROR] FTP 접속 실패: {e}")
            print()
            continue

        remote_map = {f["name"]: f for f in remote_files}

        all_names = sorted(set(list(local_map.keys()) + list(remote_map.keys())))

        only_local = 0
        only_remote = 0
        size_diff = 0
        same = 0

        print(f"  {'상태':^4}  {'크기(로컬)':>10}  {'크기(리모트)':>10}  파일명")
        print(f"  {'─'*4}  {'─'*10}  {'─'*10}  {'─'*30}")

        for name in all_names:
            lf = local_map.get(name)
            rf = remote_map.get(name)

            if lf and not rf:
                print(f"  {'->':^4}  {lf['size']:>10,}  {'':>10}  {name}")
                only_local += 1
            elif rf and not lf:
                print(f"  {'<-':^4}  {'':>10}  {rf['size']:>10,}  {name}")
                only_remote += 1
            elif lf and rf:
                if lf["size"] == rf["size"]:
                    print(f"  {'==':^4}  {lf['size']:>10,}  {rf['size']:>10,}  {name}")
                    same += 1
                else:
                    print(f"  {'!=':^4}  {lf['size']:>10,}  {rf['size']:>10,}  {name}")
                    size_diff += 1

        print(f"\n  요약: 동일={same} | 로컬만={only_local} | 리모트만={only_remote} | 크기다름={size_diff}")
        print()


def ftp_rmdir_recursive(ftp: ftplib.FTP, path: str):
    """FTP 디렉토리 재귀 삭제"""
    try:
        items = ftp.nlst(path)
    except ftplib.error_perm:
        return

    for full in items:
        basename = full.rsplit("/", 1)[-1] if "/" in full else full
        if basename in (".", ".."):
            continue
        try:
            ftp.delete(full)
        except ftplib.error_perm:
            ftp_rmdir_recursive(ftp, full)
            try:
                ftp.rmd(full)
            except ftplib.error_perm:
                pass


def ftp_upload_dir(ftp: ftplib.FTP, local_dir: Path, remote_dir: str) -> int:
    """로컬 디렉토리를 FTP에 재귀 업로드, 업로드 파일 수 반환"""
    try:
        ftp.mkd(remote_dir)
    except ftplib.error_perm:
        pass

    count = 0
    for item in sorted(os.listdir(local_dir)):
        local_path = local_dir / item
        remote_path = f"{remote_dir}/{item}"

        if local_path.is_dir():
            count += ftp_upload_dir(ftp, local_path, remote_path)
        else:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            print(f"  UP  {remote_path}")
            count += 1
    return count


def cmd_push(config: dict, env_vars: dict, sp_arg: str | None, dry_run: bool = False):
    """로컬 → 리모트 업로드 (기존 삭제 후 전체 업로드)"""
    print("# ccsync ftp push\n")
    items = resolve_profiles(config, sp_arg)

    for sp_key, profile in items:
        local_dir = PROJECT_ROOT / profile["local_dir"]
        print(f"## {sp_key} — {profile['name']}")
        print(f"  {profile['local_dir']}/ → {profile['host']}:{profile['remote_root']}")

        if not local_dir.exists():
            print(f"  [ERROR] 로컬 디렉토리 없음: {profile['local_dir']}")
            print()
            continue

        targets = profile["targets"]
        print(f"  대상: {', '.join(targets)}")

        if dry_run:
            local_files = get_local_files(local_dir, targets)
            print(f"  [DRY-RUN] 업로드 예정: {len(local_files)} 파일")
            for lf in local_files:
                print(f"    {lf['name']}")
            print()
            continue

        password = get_password(profile, config, env_vars)
        try:
            ftp = connect_ftp(profile, password)
            remote_root = profile["remote_root"]

            if remote_root != "/":
                ftp.cwd(remote_root)

            # 1단계: 기존 삭제
            print("  --- 기존 파일 삭제 ---")
            for target in targets:
                remote_path = f"{remote_root.rstrip('/')}/{target}"
                target_local = local_dir / target
                if target_local.is_dir():
                    ftp_rmdir_recursive(ftp, remote_path)
                    try:
                        ftp.rmd(remote_path)
                        print(f"  DEL {remote_path}/")
                    except ftplib.error_perm:
                        pass
                else:
                    try:
                        ftp.delete(remote_path)
                        print(f"  DEL {remote_path}")
                    except ftplib.error_perm:
                        pass

            # 2단계: 업로드
            print("  --- 파일 업로드 ---")
            total = 0
            for target in targets:
                target_local = local_dir / target
                remote_path = f"{remote_root.rstrip('/')}/{target}"
                if target_local.is_dir():
                    total += ftp_upload_dir(ftp, target_local, remote_path)
                elif target_local.is_file():
                    with open(target_local, "rb") as f:
                        ftp.storbinary(f"STOR {remote_path}", f)
                    print(f"  UP  {remote_path}")
                    total += 1

            ftp.quit()
            print(f"\n  완료: {total} 파일 업로드")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()


def ftp_download_dir(ftp: ftplib.FTP, remote_dir: str, local_dir: Path) -> int:
    """리모트 디렉토리를 로컬에 재귀 다운로드, 다운로드 파일 수 반환"""
    local_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    try:
        items = list(ftp.mlsd(remote_dir))
    except ftplib.error_perm:
        try:
            names = ftp.nlst(remote_dir)
        except ftplib.error_perm:
            return 0
        for name in names:
            basename = name.rsplit("/", 1)[-1] if "/" in name else name
            if basename in (".", ".."):
                continue
            local_path = local_dir / basename
            try:
                with open(local_path, "wb") as f:
                    ftp.retrbinary(f"RETR {name}", f.write)
                print(f"  DL  {name}")
                count += 1
            except ftplib.error_perm:
                count += ftp_download_dir(ftp, name, local_path)
        return count

    for name, facts in items:
        if name in (".", ".."):
            continue
        remote_path = f"{remote_dir}/{name}"
        local_path = local_dir / name
        if facts.get("type") == "dir":
            count += ftp_download_dir(ftp, remote_path, local_path)
        else:
            with open(local_path, "wb") as f:
                ftp.retrbinary(f"RETR {remote_path}", f.write)
            print(f"  DL  {remote_path}")
            count += 1
    return count


def cmd_pull(config: dict, env_vars: dict, sp_arg: str | None, dry_run: bool = False):
    """리모트 → 로컬 다운로드"""
    print("# ccsync ftp pull\n")
    items = resolve_profiles(config, sp_arg)

    for sp_key, profile in items:
        local_dir = PROJECT_ROOT / profile["local_dir"]
        print(f"## {sp_key} — {profile['name']}")
        print(f"  {profile['host']}:{profile['remote_root']} → {profile['local_dir']}/")

        password = get_password(profile, config, env_vars)
        targets = profile["targets"]
        print(f"  대상: {', '.join(targets)}")

        if dry_run:
            try:
                ftp = connect_ftp(profile, password)
                remote_root = profile["remote_root"]
                total = 0
                for target in targets:
                    remote_path = f"{remote_root.rstrip('/')}/{target}"
                    rfiles = get_remote_files(ftp, remote_path, target)
                    total += len(rfiles)
                    for rf in rfiles:
                        print(f"    {rf['name']}")
                ftp.quit()
                print(f"  [DRY-RUN] 다운로드 예정: {total} 파일")
            except Exception as e:
                print(f"  [ERROR] {e}")
            print()
            continue

        try:
            ftp = connect_ftp(profile, password)
            remote_root = profile["remote_root"]

            print("  --- 파일 다운로드 ---")
            total = 0
            for target in targets:
                remote_path = f"{remote_root.rstrip('/')}/{target}"
                target_local = local_dir / target

                # 단일 파일인지 디렉토리인지 판별
                try:
                    ftp.cwd(remote_path)
                    ftp.cwd(remote_root)
                    # 디렉토리
                    total += ftp_download_dir(ftp, remote_path, target_local)
                except ftplib.error_perm:
                    # 파일
                    local_dir.mkdir(parents=True, exist_ok=True)
                    with open(target_local, "wb") as f:
                        ftp.retrbinary(f"RETR {remote_path}", f.write)
                    print(f"  DL  {remote_path}")
                    total += 1

            ftp.quit()
            print(f"\n  완료: {total} 파일 다운로드")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()


def cmd_help():
    """도움말"""
    print("# ccsync ftp - SP별 FTP 동기화\n")
    print("사용법: ccsync ftp <command> [SP] [--dry-run]\n")
    print("  status [SP]     접속 테스트 + 프로필 요약")
    print("  list   [SP]     리모트 파일 목록")
    print("  diff   [SP]     로컬 vs 리모트 비교")
    print("  push   [SP]     로컬 → 리모트 업로드")
    print("  pull   [SP]     리모트 → 로컬 다운로드")
    print("  help            이 도움말")
    print()
    print("SP 생략 시 전체 프로필 대상. --dry-run은 push/pull에서 미리보기.")
    print()
    print("설정: .agents/skills/ccsync/references/ftp_config.json")
    print("비밀번호: .env의 FTP_PASS")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "help":
        cmd_help()
        return

    subcmd = args[0]
    sp_arg = args[1] if len(args) > 1 and not args[1].startswith("-") else None
    dry_run = "--dry-run" in args

    config = load_config()
    env_vars = load_env()

    if subcmd == "status":
        cmd_status(config, env_vars, sp_arg)
    elif subcmd == "list":
        cmd_list(config, env_vars, sp_arg)
    elif subcmd == "diff":
        cmd_diff(config, env_vars, sp_arg)
    elif subcmd == "push":
        cmd_push(config, env_vars, sp_arg, dry_run)
    elif subcmd == "pull":
        cmd_pull(config, env_vars, sp_arg, dry_run)
    else:
        print(f"[ERROR] 알 수 없는 명령: {subcmd}")
        cmd_help()


if __name__ == "__main__":
    main()
