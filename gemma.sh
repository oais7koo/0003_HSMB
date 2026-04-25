#!/bin/bash
# gemma.sh - Gemma4 SLM mlx-lm Local Runner (macOS/bash)

PORT="8080"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAST_MODEL_FILE="$SCRIPT_DIR/.claude/skills/gemma/references/last_model.json"
COMPUTER=$(hostname -s)

# ── Colors ──────────────────────────────────────────────────────────────────
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
ORANGE='\033[0;33m'
NC='\033[0m'

write_header() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  Gemma4 SLM - mlx-lm Local Server${NC}"
    echo -e "  Port: localhost:${PORT}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
}

write_step() { echo -e "${YELLOW}[$1] $2${NC}"; }
write_ok()   { echo -e "${GREEN}      [OK] $1${NC}"; }
write_warn() { echo -e "${ORANGE}      [!]  $1${NC}"; }
write_info() { echo -e "${CYAN}      [*]  $1${NC}"; }
write_err()  { echo -e "${RED}      [ERROR] $1${NC}"; }

# ── Header ──────────────────────────────────────────────────────────────────
write_header

# ── Model Selection ──────────────────────────────────────────────────────────
MODEL_KEYS=(1 2 3 4)
MODEL_NAMES=(
    "mlx-community/gemma-4-e4b-it-4bit"
    "mlx-community/gemma-4-e2b-it-4bit"
    "mlx-community/gemma-3-27b-it-4bit"
    "mlx-community/gemma-3-12b-it-4bit"
)
MODEL_DESCS=(
    "Gemma4 4B  Q4 (default, ~5GB)"
    "Gemma4 2B  Q4 (lightweight, ~2.5GB)"
    "Gemma3 27B Q4 (high quality, ~15GB)"
    "Gemma3 12B Q4 (balanced, ~7GB)"
)

# 마지막 사용 모델 불러오기 (per computer, JSON)
DEFAULT_KEY=1
LAST_MODEL_HINT=""
if [ -f "$LAST_MODEL_FILE" ] && command -v python3 &>/dev/null; then
    LAST_MODEL=$(python3 -c "
import json, sys
try:
    d = json.load(open('$LAST_MODEL_FILE'))
    print(d.get('$COMPUTER', ''))
except: pass
" 2>/dev/null)
    if [ -n "$LAST_MODEL" ]; then
        for i in 0 1 2 3; do
            if [ "${MODEL_NAMES[$i]}" = "$LAST_MODEL" ]; then
                DEFAULT_KEY=$((i + 1))
                LAST_MODEL_HINT=" (last: $LAST_MODEL)"
                break
            fi
        done
    fi
fi

echo -e "  Select a model to use: [${COMPUTER}${LAST_MODEL_HINT}]"
for i in 0 1 2 3; do
    KEY=$((i + 1))
    MARKER=" "
    [ "$KEY" -eq "$DEFAULT_KEY" ] && MARKER="*"
    printf "   ${GRAY}%s %d) %-42s %s${NC}\n" "$MARKER" "$KEY" "${MODEL_NAMES[$i]}" "${MODEL_DESCS[$i]}"
done
echo ""
read -rp "  Choice (default: $DEFAULT_KEY): " MODEL_CHOICE
[ -z "$MODEL_CHOICE" ] && MODEL_CHOICE=$DEFAULT_KEY

# 유효성 검사
if [[ "$MODEL_CHOICE" =~ ^[1-4]$ ]]; then
    IDX=$((MODEL_CHOICE - 1))
    MODEL="${MODEL_NAMES[$IDX]}"
else
    write_warn "Invalid choice. Falling back to default model."
    IDX=$((DEFAULT_KEY - 1))
    MODEL="${MODEL_NAMES[$IDX]}"
fi

# 선택 모델 저장 (per computer)
if command -v python3 &>/dev/null; then
    python3 -c "
import json, os
path = '$LAST_MODEL_FILE'
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    d = json.load(open(path)) if os.path.exists(path) else {}
except: d = {}
d['$COMPUTER'] = '$MODEL'
json.dump(d, open(path, 'w'), ensure_ascii=False, indent=2)
" 2>/dev/null
fi

write_ok "Selected model: $MODEL"
echo ""

# ── 1. mlx-lm 설치 확인 ──────────────────────────────────────────────────────
write_step "1/4" "Checking mlx-lm installation..."

MLX_CMD=""
if command -v mlx_lm.server &>/dev/null; then
    MLX_CMD="mlx_lm.server"
elif python3 -c "import mlx_lm" &>/dev/null 2>&1; then
    MLX_CMD="python3 -m mlx_lm.server"
fi

if [ -z "$MLX_CMD" ]; then
    write_warn "mlx-lm is not installed."
    echo ""

    # brew 설치 시도 (sudo 불필요)
    if command -v brew &>/dev/null; then
        write_info "Trying: brew install mlx-lm"
        echo ""
        brew install mlx-lm
        BREW_RC=$?
        echo ""
        if [ $BREW_RC -ne 0 ]; then
            write_warn "brew install failed (exit code: $BREW_RC)."
        fi
    else
        write_warn "Homebrew not found."
    fi

    # 재확인 후 pip3 --user 시도 (sudo 불필요)
    if ! command -v mlx_lm.server &>/dev/null && ! python3 -c "import mlx_lm" &>/dev/null 2>&1; then
        if command -v pip3 &>/dev/null; then
            write_info "Trying: pip3 install --user mlx-lm"
            echo ""
            pip3 install --user mlx-lm
            PIP_RC=$?
            echo ""
            if [ $PIP_RC -ne 0 ]; then
                write_warn "pip3 install --user failed (exit code: $PIP_RC)."
            fi
        else
            write_warn "pip3 not found."
        fi
    fi

    # 최종 확인
    if command -v mlx_lm.server &>/dev/null; then
        MLX_CMD="mlx_lm.server"
    elif python3 -c "import mlx_lm" &>/dev/null 2>&1; then
        MLX_CMD="python3 -m mlx_lm.server"
    else
        write_err "Automatic installation failed."
        echo ""
        echo -e "      ${GRAY}Please install manually (no sudo required):${NC}"
        echo -e "      ${GRAY}  [Option 1] brew install mlx-lm${NC}"
        echo -e "      ${GRAY}  [Option 2] pip3 install --user mlx-lm${NC}"
        echo -e "      ${GRAY}  [Option 3] python3 -m pip install --user mlx-lm${NC}"
        echo ""
        echo -e "      ${GRAY}If admin/sudo is required on your system:${NC}"
        echo -e "      ${GRAY}  sudo pip3 install mlx-lm${NC}"
        echo ""
        echo -e "      ${GRAY}After installation, restart terminal and re-run this script.${NC}"
        echo ""
        read -rp "Press Enter to exit" _
        exit 1
    fi
    write_ok "mlx-lm installed successfully! ($MLX_CMD)"
else
    write_ok "mlx-lm confirmed ($MLX_CMD)"
fi
echo ""

# ── 2. 포트 충돌 확인 ────────────────────────────────────────────────────────
write_step "2/4" "Checking port $PORT availability..."

PORT_PID=$(lsof -ti:"$PORT" 2>/dev/null | head -1)
if [ -n "$PORT_PID" ]; then
    PROC_NAME=$(ps -p "$PORT_PID" -o comm= 2>/dev/null || echo "unknown")
    write_warn "Port $PORT is already in use."
    echo -e "      ${GRAY}[>] Process: $PROC_NAME (PID: $PORT_PID)${NC}"
    echo ""
    echo -e "      Select an option:"
    echo "        1) Kill existing process and restart"
    echo "        2) Switch to port 11434"
    echo "        3) Try connecting anyway (OK if existing is mlx-lm)"
    echo "        0) Cancel"
    echo ""
    read -rp "      Choice (0/1/2/3): " PORT_CHOICE

    case "$PORT_CHOICE" in
        1)
            echo ""
            write_info "Killing PID $PORT_PID ($PROC_NAME)..."
            kill -9 "$PORT_PID" 2>/dev/null
            sleep 1
            write_ok "Process terminated"
            ;;
        2)
            echo ""
            PORT="11434"
            write_ok "Switched to port 11434."
            ;;
        3)
            echo ""
            write_info "Attempting to connect to existing server..."
            ;;
        *)
            echo ""
            write_info "Cancelled."
            exit 0
            ;;
    esac
else
    write_ok "Port $PORT is available"
fi
echo ""

# ── 3. 모델 캐시 확인 ────────────────────────────────────────────────────────
write_step "3/4" "Checking model cache: $MODEL"

# mlx-lm은 ~/.cache/huggingface/hub/ 또는 직접 경로에 저장
MODEL_SLUG=$(echo "$MODEL" | tr '/' '--')
HF_CACHE="${HF_HOME:-$HOME/.cache/huggingface}/hub"
MODEL_CACHE_DIR="$HF_CACHE/models--${MODEL_SLUG}"

echo -e "      ${GRAY}[>] Cache: $MODEL_CACHE_DIR${NC}"

if [ -d "$MODEL_CACHE_DIR" ]; then
    CACHE_SIZE=$(du -sh "$MODEL_CACHE_DIR" 2>/dev/null | cut -f1)
    write_ok "Model found in cache ($CACHE_SIZE)"
else
    write_warn "Model not found in cache."
    write_info "Will download on first run (~5GB for 4B model)..."
    write_info "This may take several minutes depending on network speed."
    echo ""
    read -rp "      Continue? [Y/n]: " CONFIRM
    [[ "$CONFIRM" =~ ^[Nn]$ ]] && { write_info "Cancelled."; exit 0; }
fi
echo ""

# ── 4. 서버 실행 ─────────────────────────────────────────────────────────────
write_step "4/4" "Starting Gemma4 mlx-lm server..."
echo -e "      ${GRAY}Model: $MODEL${NC}"
echo -e "      ${GRAY}URL:   http://localhost:$PORT/v1${NC}"
echo -e "      ${GRAY}Exit:  Ctrl+C${NC}"
echo ""
echo -e "${CYAN}============================================${NC}"
echo ""

$MLX_CMD --model "$MODEL" --port "$PORT"
