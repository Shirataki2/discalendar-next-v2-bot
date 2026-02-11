#!/bin/bash
set -e

# =============================================================================
# DisCalendar Bot - Lightsail サーバー管理スクリプト
# Usage: ./scripts/server.sh <command> [options]
# =============================================================================

# --- 設定 ---
SSH_USER="ubuntu"
APP_DIR="/opt/discalendar-bot"
INSTANCE_NAME="discalendar-bot"
AWS_REGION="ap-northeast-1"
CLOUDWATCH_LOG_GROUP="/aws/lightsail/discalendar-bot"
CLOUDWATCH_LOG_STREAM="discalendar-bot"

# SSH鍵のパス（環境変数で上書き可能）
if [ -n "$SSH_KEY_PATH" ]; then
  SSH_KEY="${SSH_KEY_PATH/#\~/$HOME}"
  SSH_KEY="${SSH_KEY//\$HOME/$HOME}"
else
  SSH_KEY="$HOME/.ssh/lightsail_key"
fi

# --- ヘルパー関数 ---
color_red="\033[0;31m"
color_green="\033[0;32m"
color_yellow="\033[0;33m"
color_cyan="\033[0;36m"
color_reset="\033[0m"

info() { echo -e "${color_cyan}[INFO]${color_reset} $*"; }
success() { echo -e "${color_green}[OK]${color_reset} $*"; }
warn() { echo -e "${color_yellow}[WARN]${color_reset} $*"; }
error() { echo -e "${color_red}[ERROR]${color_reset} $*" >&2; }

get_public_ip() {
  if [ -n "$LIGHTSAIL_IP" ]; then
    echo "$LIGHTSAIL_IP"
    return
  fi

  if command -v aws &>/dev/null; then
    local ip
    ip=$(aws lightsail get-instance \
      --instance-name "$INSTANCE_NAME" \
      --region "$AWS_REGION" \
      --query 'instance.publicIpAddress' \
      --output text 2>/dev/null) || true
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "$ip"
      return
    fi
  fi

  error "パブリックIPを取得できません"
  error "以下のいずれかの方法で指定してください:"
  error "  1. 環境変数: export LIGHTSAIL_IP=<ip>"
  error "  2. AWS CLIを設定する (aws configure)"
  exit 1
}

ssh_cmd() {
  ssh -i "${SSH_KEY}" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o LogLevel=ERROR \
    "${SSH_USER}@$(get_public_ip)" "$@"
}

show_usage() {
  cat <<'USAGE'
DisCalendar Bot - Lightsail サーバー管理スクリプト

Usage: ./scripts/server.sh <command> [options]

Commands:
  ssh                サーバーにSSH接続（インタラクティブシェル）
  status             Botコンテナの状態を確認
  logs [options]     Dockerコンテナのログを表示
    -f, --follow       リアルタイムでログを表示
    -n, --lines <N>    直近N行を表示（デフォルト: 100）
  cloudwatch [options]  CloudWatch Logsを表示
    -f, --follow       リアルタイムでログを表示
    --since <time>     指定時間以降のログ（例: 1h, 30m, 2d）
    --filter <pattern> フィルターパターン（例: ERROR, WARNING）
  restart            Botコンテナを再起動
  exec <command>     サーバー上でコマンドを実行

Options:
  -h, --help         このヘルプを表示

Environment Variables:
  LIGHTSAIL_IP       パブリックIPを直接指定（Terraform不要）
  SSH_KEY_PATH       SSH秘密鍵のパス（デフォルト: ~/.ssh/lightsail_key）

Examples:
  ./scripts/server.sh ssh
  ./scripts/server.sh status
  ./scripts/server.sh logs -f
  ./scripts/server.sh logs -n 50
  ./scripts/server.sh cloudwatch -f
  ./scripts/server.sh cloudwatch --since 1h --filter ERROR
  ./scripts/server.sh restart
  ./scripts/server.sh exec "docker compose ps"
USAGE
}

# --- コマンド実装 ---

cmd_ssh() {
  local ip
  ip=$(get_public_ip)
  info "サーバーに接続中... (${SSH_USER}@${ip})"
  ssh -i "${SSH_KEY}" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${SSH_USER}@${ip}"
}

cmd_status() {
  info "コンテナの状態を確認中..."
  ssh_cmd <<EOF
cd ${APP_DIR}
echo "=== コンテナ状態 ==="
docker compose ps
echo ""
echo "=== リソース使用状況 ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || true
echo ""
echo "=== ディスク使用状況 ==="
df -h / | tail -1
echo ""
echo "=== Uptime ==="
uptime
EOF
  success "完了"
}

cmd_logs() {
  local follow=""
  local lines="100"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -f|--follow)
        follow="-f"
        shift
        ;;
      -n|--lines)
        lines="$2"
        shift 2
        ;;
      *)
        error "不明なオプション: $1"
        exit 1
        ;;
    esac
  done

  info "Dockerログを表示中... (直近${lines}行)"
  ssh_cmd "cd ${APP_DIR} && docker compose logs --tail=${lines} ${follow}"
}

cmd_cloudwatch() {
  local follow=""
  local since=""
  local filter=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -f|--follow)
        follow="--follow"
        shift
        ;;
      --since)
        since="$2"
        shift 2
        ;;
      --filter)
        filter="$2"
        shift 2
        ;;
      *)
        error "不明なオプション: $1"
        exit 1
        ;;
    esac
  done

  if ! command -v aws &>/dev/null; then
    error "AWS CLIがインストールされていません"
    error "  brew install awscli"
    exit 1
  fi

  local args=(
    "logs"
  )

  if [ -n "$filter" ]; then
    args+=("filter-log-events"
      "--log-group-name" "$CLOUDWATCH_LOG_GROUP"
      "--filter-pattern" "$filter"
    )
    if [ -n "$since" ]; then
      local ms
      ms=$(parse_duration_to_ms "$since")
      local now_ms
      now_ms=$(date +%s)000
      args+=("--start-time" "$((now_ms - ms))")
    fi
    info "CloudWatch Logs を検索中... (フィルター: ${filter})"
    aws "${args[@]}" --region "$AWS_REGION" \
      --query 'events[].message' --output text
  else
    args+=("tail" "$CLOUDWATCH_LOG_GROUP")
    if [ -n "$since" ]; then
      args+=("--since" "$since")
    fi
    if [ -n "$follow" ]; then
      args+=("$follow")
    fi
    info "CloudWatch Logs を表示中..."
    aws "${args[@]}" --region "$AWS_REGION"
  fi
}

cmd_restart() {
  info "Botコンテナを再起動中..."
  ssh_cmd "cd ${APP_DIR} && docker compose restart"
  sleep 3
  info "再起動後の状態:"
  ssh_cmd "cd ${APP_DIR} && docker compose ps"
  success "再起動完了"
}

cmd_exec() {
  if [ -z "$1" ]; then
    error "実行するコマンドを指定してください"
    error "例: ./scripts/server.sh exec \"docker compose ps\""
    exit 1
  fi
  info "コマンドを実行中: $*"
  ssh_cmd "$@"
}

parse_duration_to_ms() {
  local input="$1"
  local num="${input%[a-z]*}"
  local unit="${input##*[0-9]}"

  case "$unit" in
    m) echo $((num * 60 * 1000)) ;;
    h) echo $((num * 3600 * 1000)) ;;
    d) echo $((num * 86400 * 1000)) ;;
    *) echo $((num * 1000)) ;;
  esac
}

# --- メイン ---

if [ $# -eq 0 ]; then
  show_usage
  exit 0
fi

command="$1"
shift

case "$command" in
  ssh)        cmd_ssh "$@" ;;
  status)     cmd_status "$@" ;;
  logs)       cmd_logs "$@" ;;
  cloudwatch) cmd_cloudwatch "$@" ;;
  restart)    cmd_restart "$@" ;;
  exec)       cmd_exec "$@" ;;
  -h|--help)  show_usage ;;
  *)
    error "不明なコマンド: ${command}"
    echo ""
    show_usage
    exit 1
    ;;
esac
