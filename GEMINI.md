# GEMINI.md - Project Guidance & Mandates

## 1. Core Mandates

### 1.1 Communication & Logic
- **Primary Language**: Always respond in **Korean**.
- **Intent-First**: If the user's intent is ambiguous, ask for clarification before taking action. Clarity over assumption.
- **Autonomous Execution**: Once the scope is clear, complete the task without repeated "Should I do X?" questions. Report results upon completion.
- **Context Efficiency**: Minimize unnecessary file reads. Use `grep_search` and `glob` strategically.

### 1.2 Windows Environment Protocol
- **OS**: Windows (win32). Paths and shell commands must be Windows-compatible.
- **Path Handling**: Use absolute paths whenever possible. Be cautious with `TEMP`/`TMP` environment variables during Git operations.
- **Shell**: Prefer PowerShell/CMD syntax for shell commands.

## 2. Tool & Skill Policies

### 2.1 Skill Usage (cc* Skills)
- **Status**: `cc*` skills are the primary specialized tools for this workspace (Codex-native).
- **ccwiki**: Use for knowledge base lookups and wiki management.
- **ccreview**: Use for code, security, and design reviews.
- **ccporting**: Follow the protocol: Port to `.claude/skills_to_codex/`, verify in `.agents/skills/`.
- **Activation**: Use `activate_skill(name)` to trigger specialized guidance.

### 2.2 Search & Discovery
- **Discovery First**: Complete project-wide discovery before making systemic changes.
- **Validation**: Always run tests/linters (`npm run lint`, `tsc`, etc.) before marking a task complete.

## 3. Project Structure & Reference

### 3.1 Essential Documents (Auto-load)
| Document | Purpose |
| :--- | :--- |
| `00_doc/sp00/d0001_prd.md` | PRD - Project Requirements |
| `00_doc/sp00/d0004_todo.md` | TODO & Debugging Tracker |

### 3.2 On-Demand Reference
- `AGENTS.md`: Shared behavior rules for all agents.
- `00_doc/sp00/d0002_plan.md`: Implementation plans.
- `00_doc/sp00/d0005_lib.md`: Library and dependency info.

## 4. Engineering Standards

### 4.1 Documentation
- **Standard Numbering**: All `.md` files must use hierarchical numbering (e.g., `## 1. Title`, `### 1.1 Subtitle`).
- **Traceability**: Record bugs and reproduction steps in `d0004_todo.md` before fixing.

### 4.2 Code Integrity
- Adhere to existing naming conventions and architectural patterns.
- Never suppress warnings or bypass type systems unless explicitly instructed.
- Validation is mandatory: Reproduce bugs with tests before applying fixes.

## 5. Deployment & Git
- Never stage or commit changes unless explicitly asked ("Commit this", "Prepare a PR").
- Use `git status && git diff HEAD` to review changes before proposing a commit message.
