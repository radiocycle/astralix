<div align="center">
  <img src="https://github.com/hikariatama/assets/raw/master/1326-command-window-line-flat.webp" height="80">
  <h1>astralix Userbot</h1>
  <p>Advanced Telegram userbot powered by <a href="https://codeberg.org/Lonami/Telethon">Telethon</a></p>
  
  <p>
    <a href="https://github.com/radiocycle/astralix/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/radiocycle/astralix/main.yml?branch=dev" alt="Build">
    </a>
    <a href="#">
      <img src="https://img.shields.io/github/languages/code-size/radiocycle/astralix" alt="Code Size">
    </a>
    <a href="#">
      <img src="https://img.shields.io/github/issues-raw/radiocycle/astralix" alt="Open Issues">
    </a>
    <a href="#">
      <img src="https://img.shields.io/github/license/radiocycle/astralix" alt="License">
    </a>
    <a href="#">
      <img src="https://img.shields.io/github/commit-activity/m/radiocycle/astralix" alt="Commit Activity">
    </a>
    <br>
    <a href="#">
      <img src="https://img.shields.io/github/forks/radiocycle/astralix?style=flat" alt="Forks">
    </a>
    <a href="#">
      <img src="https://img.shields.io/github/stars/radiocycle/astralix" alt="Stars">
    </a>
    <a href="https://github.com/psf/black">
      <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
    </a>
  </p>
</div>

---

## 🚀 Quick Install (Debian/Ubuntu, root)

One-liner — installs everything (packages, venv, systemd service) and launches interactive Telegram login:

```bash
curl -fsSL https://raw.githubusercontent.com/radiocycle/astralix/dev/install.sh | bash
```

> **What it does:** installs system deps → sets up [`uv`](https://github.com/astral-sh/uv) → clones repo → creates `.venv` → installs Python dependencies → creates `astralix.service` (systemd) → runs first-time login → asks `y/N` to enable autostart.

### Manual one-liner (no install.sh)

```bash
apt update && apt install -y git python3 python3-venv && \
git clone -b dev https://github.com/radiocycle/astralix.git && \
cd astralix && \
python3 -m venv .venv && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
python3 -m astralix --root
```

---

## ⚠️ Security Notice

> **Important Security Advisory**
> While astralix implements extended security measures, installing modules from untrusted developers may still cause damage to your server/account.
>
> **Recommendations:**
> - ✅ Download modules exclusively from official repositories or trusted developers
> - ❌ Do NOT install modules if unsure about their safety
> - ⚠️ Exercise caution with unknown commands (`.terminal`, `.eval`, `.ecpp`, etc.)

---

## 📦 Installation (other platforms)

<details>
<summary><b>Fedora</b></summary>

```bash
dnf install -y git python3 python3-devel && \
git clone -b dev https://github.com/radiocycle/astralix.git && \
cd astralix && \
python3 -m venv .venv && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
python3 -m astralix --root
```
</details>

<details>
<summary><b>Arch Linux</b></summary>

```bash
pacman -Syu --noconfirm --needed git python && \
git clone -b dev https://github.com/radiocycle/astralix.git && \
cd astralix && \
python3 -m venv .venv && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
python3 -m astralix --root
```
</details>

<details>
<summary><b>WSL (Windows)</b></summary>

> **⚠️ Can be unstable!**

1. Install WSL (PowerShell as admin):
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```
2. Restart, open Ubuntu terminal, then:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/radiocycle/astralix/dev/install.sh | bash
   ```
</details>

---

## 🔧 Service Management

After installation with `install.sh`, the bot runs as a systemd service:

```bash
systemctl start astralix       # start
systemctl stop astralix        # stop
systemctl restart astralix     # restart
systemctl status astralix      # status
journalctl -u astralix -f      # live logs
```

---

## ✨ Key Features & Improvements

| Feature | Description |
|---------|-------------|
| 🆕 **Latest Telegram Layer** | Layer 228 — forums, communities, newest Telegram features |
| 🔄 **Telethon Powered** | Migrated from astralix-TL to upstream [Telethon](https://codeberg.org/Lonami/Telethon) |
| 🔒 **Enhanced Security** | Native entity caching and targeted security rules |
| 🎨 **Configurable Banners** | `banner_url`, `quote_media`, `invert_media` on `.astralix` and `.info` |
| ⏱ **Rapid Bug Fixes** | Faster resolution than FTG/GeekTG |
| 🔄 **Backward Compatibility** | Import hook redirects `hikkatl` → `telethon` for loaded modules |
| ▶️ **Inline Elements** | Forms, galleries and lists support |

---

## 📋 Requirements

- **Python 3.10+**
- **Root access** (for systemd service)
- **API Credentials** from [my.telegram.org](https://my.telegram.org/apps)

---

## 💬 Support

[![Telegram](https://img.shields.io/badge/Telegram-Support_Group-2594cb?logo=telegram)](https://t.me/astralix_talks)

---

## ⚠️ Usage Disclaimer

> This project is provided as-is. The developer takes **NO responsibility** for:
> - Account bans or restrictions
> - Message deletions by Telegram
> - Security issues from scam modules
> - Session leaks from malicious modules
>
> **Security Recommendations:**
> - Enable `.api_fw_protection`
> - Avoid installing many modules at once
> - Review [Telegram's Terms](https://core.telegram.org/api/terms)

---

## 🙏 Acknowledgements

- [**Hikari**](https://gitlab.com/hikariatama) for Hikka (project foundation)
- [**Codrago**](https://github.com/coddrago) for astralix (fork base)
- [**Lonami**](https://codeberg.org/Lonami) for Telethon (MTProto backbone)
