#!/bin/bash
#
# astralix Userbot installer for Debian/Ubuntu (root, no sudo)
#
# Usage:  bash install.sh
#
set -euo pipefail

# ── Config ─────────────────────────────────────────────────────────────────
INSTALL_DIR="/root/astralix"
REPO_URL="https://github.com/radiocycle/astralix.git"
BRANCH="dev"
SERVICE_NAME="astralix.service"
PYTHON_MIN="3.10"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }
step()  { echo -e "\n${CYAN}${BOLD}▶ $*${NC}"; }

# ── Pre-flight checks ────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root"
    exit 1
fi

if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    info "Detected OS: $PRETTY_NAME"
else
    error "Cannot detect OS (/etc/os-release not found). This script supports Debian/Ubuntu only."
    exit 1
fi

# Check Python version
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0")
if [[ $(echo -e "$PY_VERSION\n$PYTHON_MIN" | sort -V | head -1) != "$PYTHON_MIN" ]]; then
    error "Python >= $PYTHON_MIN required (found $PY_VERSION)"
    exit 1
fi
info "Python $PY_VERSION found"

# ── Step 1: Install system packages ──────────────────────────────────────
step "Step 1/5: Installing system packages"

export DEBIAN_FRONTEND=noninteractive

if command -v apt-get &>/dev/null; then
    apt-get update -qq
    apt-get install -y -qq \
        python3 python3-pip python3-venv python3-dev \
        build-essential git curl wget \
        libssl-dev libffi-dev libsqlite3-dev \
        zlib1g-dev libjpeg-dev libxml2-dev libxslt1-dev \
        > /dev/null 2>&1
    info "System packages installed"
else
    warn "apt-get not found, skipping system package installation"
fi

# ── Step 2: Install uv (fast Python package manager) ─────────────────────
step "Step 2/5: Installing uv"

if command -v uv &>/dev/null; then
    info "uv already installed: $(uv --version 2>/dev/null || echo 'unknown')"
else
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    info "uv installed: $(uv --version)"
fi

# ── Step 3: Clone / update repository ─────────────────────────────────────
step "Step 3/5: Cloning repository"

if [[ -d "$INSTALL_DIR/.git" ]]; then
    warn "$INSTALL_DIR already exists, pulling latest changes..."
    git -C "$INSTALL_DIR" fetch origin "$BRANCH"
    git -C "$INSTALL_DIR" checkout "$BRANCH"
    git -C "$INSTALL_DIR" reset --hard "origin/$BRANCH"
    info "Repository updated"
else
    git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    info "Repository cloned to $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ── Step 4: Create virtualenv and install dependencies ───────────────────
step "Step 4/5: Setting up virtualenv and dependencies"

# Create venv with uv
if [[ ! -d ".venv" ]]; then
    uv venv .venv
    info "Virtualenv created"
else
    info "Virtualenv already exists"
fi

# Install dependencies
info "Installing dependencies (this may take a while)..."
uv pip install -r requirements.txt 2>&1 | tail -5
info "Dependencies installed"

# ── Step 5: Create systemd service ────────────────────────────────────────
step "Step 5/5: Creating systemd service"

# Ensure start.sh exists and is executable
if [[ ! -f "start.sh" ]]; then
    cat > start.sh << 'STARTEOF'
#!/bin/bash
cd /root/astralix
exec uv run python -m astralix --root
STARTEOF
    info "start.sh created"
fi
chmod +x start.sh

# Write systemd unit
cat > "/etc/systemd/system/$SERVICE_NAME" << EOF
[Unit]
Description=astralix service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=bash $INSTALL_DIR/start.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
info "systemd unit created: $SERVICE_NAME"

# ── First run: Authentication ─────────────────────────────────────────────
step "Authentication"
echo -e "${BOLD}Starting astralix for first-time login.${NC}"
echo -e "You will need your Telegram API ID and Hash."
echo -e "Get them from: ${CYAN}https://my.telegram.org${NC}"
echo ""
read -rp "Press Enter to start login, or Ctrl+C to cancel..."

# Start once in foreground for interactive login
echo -e "\n${CYAN}── astralix first run ──${NC}"
bash start.sh

# ── Enable & start service (interactive) ──────────────────────────────────
step "Service management"
echo -e "astralix is now set up. You can enable it as a system service."
echo ""

read -rp "Enable and start astralix.service on boot? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        systemctl enable --now "$SERVICE_NAME"
        info "Service enabled and started"
        ;;
    *)
        info "Service not enabled. You can start it later with:"
        echo "  systemctl start $SERVICE_NAME"
        ;;
esac

echo ""
echo -e "${GREEN}${BOLD}✓ Installation complete!${NC}"
echo -e "  Directory:   $INSTALL_DIR"
echo -e "  Service:     systemctl {start|stop|restart|status} $SERVICE_NAME"
echo -e "  Logs:        journalctl -u $SERVICE_NAME -f"
echo ""
