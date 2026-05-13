from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

DEFAULT_MANIFEST = {
    "ports": [
        {
            "name": "oostart_to_ccstart",
            "source": ".claude/skills/oostart",
            "target": "ccstart",
        },
        {
            "name": "ooskill_to_ccskill",
            "source": ".claude/skills/ooskill",
            "target": "ccskill",
        },
    ]
}


def load_manifest(repo_root: Path, manifest_path: str | None) -> dict:
    if manifest_path:
        return json.loads((repo_root / manifest_path).read_text(encoding="utf-8"))
    return DEFAULT_MANIFEST


def list_files(src: Path) -> list[str]:
    out: list[str] = []
    for p in src.rglob("*"):
        if p.is_file():
            out.append(p.relative_to(src).as_posix())
    return sorted(out)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def port_iter(manifest: dict, port_name: str | None):
    for port in manifest.get("ports", []):
        if port_name and port["name"] != port_name:
            continue
        yield port


def sync_agents(repo_root: Path) -> bool:
    src = repo_root / "CLAUDE.md"
    dst = repo_root / "AGENTS.md"
    if not src.exists() or not dst.exists():
        return False
    s = src.read_text(encoding="utf-8", errors="ignore")
    start = "<!-- ccporting:claude-sync:start -->"
    end = "<!-- ccporting:claude-sync:end -->"
    if start not in s or end not in s:
        return False
    block = s[s.index(start) : s.index(end) + len(end)]
    d = dst.read_text(encoding="utf-8", errors="ignore")
    if start in d and end in d:
        ns = d[: d.index(start)] + block + d[d.index(end) + len(end) :]
    else:
        ns = d.rstrip() + "\n\n" + block + "\n"
    dst.write_text(ns, encoding="utf-8")
    return True


def cmd_sync(repo_root: Path, manifest: dict, port_name: str | None, state_dir: Path, do_sync_agents: bool):
    for port in port_iter(manifest, port_name):
        src = repo_root / port["source"]
        files = list_files(src) if src.exists() else []
        plan = {
            "name": port["name"],
            "source": port["source"],
            "target": port["target"],
            "files": files,
        }
        write_json(state_dir / f"plan_{port['name']}.json", plan)
        print(f"planned: {port['name']} ({len(files)} files)")
        if do_sync_agents and sync_agents(repo_root):
            print(f"agents synced: {port['name']}")


def ensure_skill_doc(path: Path, target: str):
    if path.exists():
        return
    path.write_text(
        "---\n"
        f"name: {target}\n"
        "description: Codex port skill\n"
        "---\n\n"
        f"# {target}\n\n"
        "upstream 동기화 결과는 `upstream/` 폴더를 참조한다.\n",
        encoding="utf-8",
    )


def cmd_apply(repo_root: Path, manifest: dict, port_name: str | None, state_dir: Path, do_sync_agents: bool, target_root: Path):
    for port in port_iter(manifest, port_name):
        plan_path = state_dir / f"plan_{port['name']}.json"
        if not plan_path.exists():
            raise SystemExit(f"missing plan: {port['name']} (run sync first)")
        plan = read_json(plan_path)
        src = repo_root / plan["source"]
        base = target_root / plan["target"]
        upstream = base / "upstream"
        ensure_dir(upstream)
        for rel in plan["files"]:
            sp = src / rel
            dp = upstream / rel
            ensure_dir(dp.parent)
            shutil.copy2(sp, dp)
        ensure_skill_doc(base / "SKILL.md", plan["target"])
        write_json(state_dir / f"applied_{port['name']}.json", {"target_root": str(target_root), "target": plan["target"]})
        print(f"applied: {port['name']} -> {upstream}")
        if do_sync_agents and sync_agents(repo_root):
            print(f"agents synced: {port['name']}")


def cmd_status(repo_root: Path, manifest: dict, state_dir: Path, target_root: Path):
    for port in manifest.get("ports", []):
        plan_path = state_dir / f"plan_{port['name']}.json"
        applied_path = state_dir / f"applied_{port['name']}.json"
        fs_path = target_root / port["target"] / "upstream"
        plan = plan_path.exists()
        applied_state = applied_path.exists()
        applied_fs = fs_path.exists() and any(fs_path.rglob("*"))
        applied = plan and applied_state and applied_fs
        print(f"[{port['name']}] {Path(port['source']).name} -> {port['target']}")
        print(f"  plan: {'yes' if plan else 'no'}")
        print(f"  applied(state): {'yes' if applied_state else 'no'}")
        print(f"  applied(fs): {'yes' if applied_fs else 'no'}")
        print(f"  applied: {'yes' if applied else 'no'}")


def main():
    parser = argparse.ArgumentParser(description="ccporting separated management pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ["status", "sync", "apply"]:
        p = sub.add_parser(name)
        p.add_argument("--port", help="Port name from manifest")
        p.add_argument("--manifest", help="External manifest JSON path")
        p.add_argument("--state-dir", default=".claude/skills_to_codex/.ccporting_state", help="State dir")
        p.add_argument("--sync-agents", action="store_true", help="Also sync CLAUDE.md -> AGENTS.md")
        p.add_argument("--target-root", default=".claude/skills_to_codex", help="Apply target root")

    args = parser.parse_args()
    repo_root = Path.cwd()
    state_dir = (repo_root / args.state_dir).resolve()
    target_root = (repo_root / args.target_root).resolve()
    ensure_dir(state_dir)
    manifest = load_manifest(repo_root, args.manifest)

    if args.cmd == "status":
        cmd_status(repo_root, manifest, state_dir, target_root)
    elif args.cmd == "sync":
        cmd_sync(repo_root, manifest, args.port, state_dir, args.sync_agents)
    elif args.cmd == "apply":
        cmd_apply(repo_root, manifest, args.port, state_dir, args.sync_agents, target_root)


if __name__ == "__main__":
    main()

