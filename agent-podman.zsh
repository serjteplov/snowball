#!/usr/bin/env zsh
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 {claude|opencode} [-- TOOL_ARGS...]" >&2
  exit 1
fi

TOOL="$1"
shift || true

if [[ "${1:-}" == "--" ]]; then
  shift
fi

if ! command -v podman >/dev/null 2>&1; then
  echo "podman is required" >&2
  exit 1
fi

if [[ "$TOOL" != "claude" && "$TOOL" != "opencode" ]]; then
  echo "First argument must be 'claude' or 'opencode'" >&2
  exit 1
fi

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
PROJECT_NAME="${PROJECT_ROOT:t}"
CONTAINER_PROJECT_ROOT="$PROJECT_ROOT"
HOST_CLAUDE_DIR="${HOME}/.claude"
OPENCODE_CONFIG_DIR_GLOBAL="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
OPENCODE_CONFIG_DIR_LOCAL="$PROJECT_ROOT/.opencode"

SANDBOX_DIR="$PROJECT_ROOT/.agent-sandbox"
HOME_DIR="$SANDBOX_DIR/home"
TMP_DIR="$SANDBOX_DIR/tmp"
mkdir -p "$HOME_DIR" "$TMP_DIR"
chmod 700 "$HOME_DIR"
chmod 1777 "$TMP_DIR"

IMAGE_NAME="localhost/agent-tools:latest"
SCRIPT_DIR="${0:A:h}"

if ! podman image exists "$IMAGE_NAME"; then
  echo "Building $IMAGE_NAME ..." >&2
  podman build -t "$IMAGE_NAME" -f "$SCRIPT_DIR/Containerfile.agent-tools" "$SCRIPT_DIR"
fi

ENV_ARGS=(
  -e HOME=/home/agent
  -e USER=agent
  -e LOGNAME=agent
  -e SHELL=/bin/zsh
  -e TERM="${TERM:-xterm-256color}"
  -e COLORTERM="${COLORTERM:-truecolor}"
  -e TMPDIR="$CONTAINER_PROJECT_ROOT/.agent-sandbox/tmp"
  -e XDG_CACHE_HOME=/home/agent/.cache
  -e NPM_CONFIG_CACHE=/home/agent/.cache/npm
  -e NPX_CACHE=/home/agent/.cache/npx
)

MOUNTS=(
  --volume "$PROJECT_ROOT:$CONTAINER_PROJECT_ROOT:Z,rw"
  --volume "$HOME_DIR:/home/agent:Z,rw"
)

COMMON_ARGS=(
  --rm -it
  --name "${TOOL}-${PROJECT_NAME}-$(date +%s)"
  --workdir "$CONTAINER_PROJECT_ROOT"
  --userns keep-id
  --user "$(id -u):$(id -g)"
  --cap-drop ALL
  --security-opt no-new-privileges
  --pids-limit 512
  --ipc private
  --hostname agent-sandbox
)

NETWORK_ARGS=(--network bridge)
if [[ "${AGENT_NET:-on}" == "off" ]]; then
  NETWORK_ARGS=(--network none)
fi

if [[ "$TOOL" == "claude" ]]; then
  if [[ ! -d "$HOST_CLAUDE_DIR" ]]; then
    echo "Host Claude config directory not found: $HOST_CLAUDE_DIR" >&2
    exit 1
  fi

  if [[ ! -f "$HOST_CLAUDE_DIR/settings.json" ]]; then
    echo "Host Claude settings file not found: $HOST_CLAUDE_DIR/settings.json" >&2
    exit 1
  fi

  exec podman run \
    "${COMMON_ARGS[@]}" \
    "${NETWORK_ARGS[@]}" \
    "${ENV_ARGS[@]}" \
    "${MOUNTS[@]}" \
    --volume "$HOST_CLAUDE_DIR:/home/agent/.claude:Z,ro" \
    "$IMAGE_NAME" \
    claude "$@"
else
  exec podman run \
    "${COMMON_ARGS[@]}" \
    "${NETWORK_ARGS[@]}" \
    "${ENV_ARGS[@]}" \
    "${MOUNTS[@]}" \
    --volume "$OPENCODE_CONFIG_DIR_GLOBAL:/home/agent/.config/opencode:Z,ro" \
    "$IMAGE_NAME" \
    opencode "$@"
fi
