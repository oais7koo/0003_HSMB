from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

DEFAULT_STATE_DIR = ".agents/skills/.ccporting_state"
DEFAULT_TARGET_ROOT = ".agents/skills"
DEFAULT_ALL_MANIFEST = ".agents/skills/ccporting_manifest_all.json"

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

CODEX_COMPAT_PATTERNS = [
    ("CLAUDE_TOOL_READ", r"\bRead\s*\("),
    ("CLAUDE_TOOL_WRITE", r"\bWrite\s*\("),
    ("CLAUDE_TOOL_EDIT", r"\bEdit\s*\("),
    ("CLAUDE_TOOL_BASH", r"\bBash\b|mcp__desktop-commander__start_process"),
    ("CLAUDE_AGENT_KEYWORD", r"\bClaude Code\b"),
    ("CLAUDE_COMMAND_PREFIX", r"`oo[a-z0-9_]+(?:\s+[a-z0-9_\-]+)?`"),
    ("CLAUDE_PATH_HINT", r"\.claude/skills/"),
]

AUTOFIX_REPLACEMENTS = [
    (r"\bClaude Code\b", "Codex"),
    (r"\bClaude\b", "Codex"),
    (r"\bclaude\b", "codex"),
    (r"\.claude/skills/", ".agents/skills/"),
    (r"\.codex/skills/", ".agents/skills/"),
    (r"\.codex/commands/", ".claude/commands/"),
    (r"\.codex/templates/", ".claude/templates/"),
    (r"`oo([a-z0-9_]+)\b", r"`cc\1"),
]


def load_manifest(repo_root: Path, manifest_path: str | None) -> dict:
    if manifest_path:
        return json.loads((repo_root / manifest_path).read_text(encoding="utf-8"))
    all_manifest = repo_root / DEFAULT_ALL_MANIFEST
    if all_manifest.exists():
        return json.loads(all_manifest.read_text(encoding="utf-8"))
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


def has_yaml_frontmatter(text: str) -> bool:
    return text.startswith("---\n") or text.startswith("---\r\n")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not has_yaml_frontmatter(text):
        return None, text
    lines = text.splitlines(keepends=True)
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "".join(lines[: idx + 1]), "".join(lines[idx + 1 :]).lstrip()
    return None, text


def infer_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def infer_description(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            return stripped.lstrip("> ").strip() or fallback
    return fallback


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_codex_skill_doc(upstream_skill: Path, target: str) -> str:
    if not upstream_skill.exists():
        return (
            "---\n"
            f"name: {target}\n"
            "description: \"Codex port skill\"\n"
            "---\n\n"
            f"# {target}\n\n"
            "upstream 동기화 결과는 `upstream/` 폴더를 참조한다.\n"
        )
    text = upstream_skill.read_text(encoding="utf-8", errors="ignore")
    _, body = split_frontmatter(text)
    title = infer_title(body, target)
    description = infer_description(body, f"Codex port of {title}")
    return (
        "---\n"
        f"name: {target}\n"
        f"description: {yaml_quote(description)}\n"
        "---\n\n"
        "<!-- ccporting:generated-from-upstream -->\n"
        "<!-- 원본 스킬은 upstream/ 폴더에 보관된다. -->\n\n"
        + body
    )


def ensure_upstream_skill_frontmatter(path: Path, target: str) -> None:
    if path.name != "SKILL.md" or not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    if has_yaml_frontmatter(text):
        return
    title = infer_title(text, target)
    path.write_text(
        "---\n"
        f"name: {target}-upstream\n"
        f"description: {yaml_quote(f'Upstream reference for {title}')}\n"
        "---\n\n"
        + text,
        encoding="utf-8",
    )


def copy_port_file(src: Path, base: Path, upstream: Path, rel: str) -> None:
    sp = src / rel
    upstream_dp = upstream / rel
    ensure_dir(upstream_dp.parent)
    shutil.copy2(sp, upstream_dp)
    if rel != "SKILL.md":
        skill_dp = base / rel
        ensure_dir(skill_dp.parent)
        shutil.copy2(sp, skill_dp)


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
            copy_port_file(src, base, upstream, rel)
            ensure_upstream_skill_frontmatter(upstream / rel, plan["target"])
        skill_doc = render_codex_skill_doc(upstream / "SKILL.md", plan["target"])
        ensure_dir(base)
        (base / "SKILL.md").write_text(skill_doc, encoding="utf-8")
        write_json(state_dir / f"applied_{port['name']}.json", {"target_root": str(target_root), "target": plan["target"]})
        print(f"applied: {port['name']} -> {base}")
        if do_sync_agents and sync_agents(repo_root):
            print(f"agents synced: {port['name']}")


def cmd_status(repo_root: Path, manifest: dict, port_name: str | None, state_dir: Path, target_root: Path):
    for port in port_iter(manifest, port_name):
        plan_path = state_dir / f"plan_{port['name']}.json"
        applied_path = state_dir / f"applied_{port['name']}.json"
        fs_path = target_root / port["target"]
        skill_path = fs_path / "SKILL.md"
        plan = plan_path.exists()
        applied_state = applied_path.exists()
        applied_fs = fs_path.exists() and skill_path.exists()
        applied = plan and applied_state and applied_fs
        print(f"[{port['name']}] {Path(port['source']).name} -> {port['target']}")
        print(f"  plan: {'yes' if plan else 'no'}")
        print(f"  applied(state): {'yes' if applied_state else 'no'}")
        print(f"  applied(fs): {'yes' if applied_fs else 'no'}")
        print(f"  applied: {'yes' if applied else 'no'}")


def cmd_run(repo_root: Path, manifest: dict, port_name: str | None, state_dir: Path, do_sync_agents: bool, target_root: Path):
    cmd_sync(repo_root, manifest, port_name, state_dir, do_sync_agents)
    cmd_apply(repo_root, manifest, port_name, state_dir, do_sync_agents, target_root)
    cmd_autofix(repo_root, manifest, port_name, target_root)
    cmd_audit(repo_root, manifest, port_name, target_root, include_upstream=False, include_bash=False)


def iter_audit_files(skill_root: Path, include_upstream: bool):
    candidates = [skill_root / "SKILL.md"]
    if include_upstream:
        candidates.append(skill_root / "upstream" / "SKILL.md")
    scripts_dir = skill_root / "scripts"
    if scripts_dir.exists():
        candidates.extend(scripts_dir.rglob("*.py"))
    for p in candidates:
        if p.exists() and p.is_file():
            yield p


def iter_autofix_files(skill_root: Path):
    candidates = [skill_root / "SKILL.md"]
    scripts_dir = skill_root / "scripts"
    if scripts_dir.exists():
        candidates.extend(scripts_dir.rglob("*.py"))
    for p in candidates:
        if p.exists() and p.is_file():
            yield p


def scan_text_for_patterns(text: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for code, pattern in CODEX_COMPAT_PATTERNS:
        flags = re.MULTILINE
        if code == "CLAUDE_AGENT_KEYWORD":
            flags |= re.IGNORECASE
        m = re.search(pattern, text, flags)
        if m:
            snippet = text[m.start() : m.start() + 120].splitlines()[0]
            hits.append((code, snippet.strip()))
    return hits


def build_skill_name_replacements(manifest: dict) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for port in manifest.get("ports", []):
        src_name = Path(port["source"]).name
        target = port["target"]
        if src_name.startswith("oo") and target.startswith("cc"):
            pairs.append((src_name, target))
    return sorted(pairs, key=lambda item: len(item[0]), reverse=True)


def apply_autofix_text(text: str, skill_name_replacements: list[tuple[str, str]]) -> str:
    out = text
    for pattern, repl in AUTOFIX_REPLACEMENTS:
        out = re.sub(pattern, repl, out)
    for src_name, target in skill_name_replacements:
        out = re.sub(rf"\b{re.escape(src_name)}\b", target, out)
    return out


def cmd_autofix(repo_root: Path, manifest: dict, port_name: str | None, target_root: Path):
    changed_files = 0
    scanned_files = 0
    skill_name_replacements = build_skill_name_replacements(manifest)
    for port in port_iter(manifest, port_name):
        target = port["target"]
        skill_root = target_root / target
        target_scanned = 0
        target_changed = 0
        for fp in iter_autofix_files(skill_root):
            old = fp.read_text(encoding="utf-8", errors="ignore")
            new = apply_autofix_text(old, skill_name_replacements)
            scanned_files += 1
            target_scanned += 1
            if new != old:
                fp.write_text(new, encoding="utf-8")
                changed_files += 1
                target_changed += 1
        print(f"autofix: {target} scanned={target_scanned} changed={target_changed}")
    print(f"autofix summary: scanned={scanned_files} changed={changed_files}")


def cmd_audit(
    repo_root: Path,
    manifest: dict,
    port_name: str | None,
    target_root: Path,
    include_upstream: bool,
    include_bash: bool,
):
    report: dict[str, list[dict[str, str]]] = {}
    total = 0
    for port in port_iter(manifest, port_name):
        target = port["target"]
        skill_root = target_root / target
        findings: list[dict[str, str]] = []
        for fp in iter_audit_files(skill_root, include_upstream):
            text = fp.read_text(encoding="utf-8", errors="ignore")
            for code, snippet in scan_text_for_patterns(text):
                if code == "CLAUDE_TOOL_BASH" and not include_bash:
                    continue
                findings.append(
                    {
                        "code": code,
                        "file": str(fp.relative_to(repo_root)),
                        "snippet": snippet,
                    }
                )
        if findings:
            report[target] = findings
            total += len(findings)
        print(f"audit: {target} findings={len(findings)}")

    report_path = target_root / ".ccporting_audit_report.json"
    write_json(report_path, {"total_findings": total, "report": report})
    print(f"audit report: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="ccporting separated management pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ["status", "sync", "apply", "run", "audit", "autofix"]:
        p = sub.add_parser(name)
        p.add_argument("--port", help="Port name from manifest")
        p.add_argument("--manifest", help="External manifest JSON path")
        p.add_argument("--state-dir", default=DEFAULT_STATE_DIR, help="State dir")
        p.add_argument("--sync-agents", action="store_true", help="Also sync CLAUDE.md -> AGENTS.md")
        p.add_argument("--target-root", default=DEFAULT_TARGET_ROOT, help="Apply target root")
        p.add_argument("--include-upstream", action="store_true", help="Include upstream files in audit")
        p.add_argument("--include-bash", action="store_true", help="Include bash-related findings in audit")

    args = parser.parse_args()
    repo_root = Path.cwd()
    state_dir = (repo_root / args.state_dir).resolve()
    target_root = (repo_root / args.target_root).resolve()
    ensure_dir(state_dir)
    manifest = load_manifest(repo_root, args.manifest)

    if args.cmd == "status":
        cmd_status(repo_root, manifest, args.port, state_dir, target_root)
    elif args.cmd == "sync":
        cmd_sync(repo_root, manifest, args.port, state_dir, args.sync_agents)
    elif args.cmd == "apply":
        cmd_apply(repo_root, manifest, args.port, state_dir, args.sync_agents, target_root)
    elif args.cmd == "run":
        cmd_run(repo_root, manifest, args.port, state_dir, args.sync_agents, target_root)
    elif args.cmd == "audit":
        cmd_audit(
            repo_root,
            manifest,
            args.port,
            target_root,
            include_upstream=args.include_upstream,
            include_bash=args.include_bash,
        )
    elif args.cmd == "autofix":
        cmd_autofix(repo_root, manifest, args.port, target_root)


if __name__ == "__main__":
    main()
