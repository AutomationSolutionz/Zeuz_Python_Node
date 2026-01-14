#!/usr/bin/env bash
set -e

REPO="AutomationSolutionz/Zeuz_Python_Node"
API_URL="https://api.github.com/repos/$REPO/releases/latest"

# ---------------------------
# Downloader helper
# ---------------------------
download() {
  local url="$1"
  local output="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$output"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$output" "$url"
  else
    echo "❌ Neither curl nor wget is available"
    exit 1
  fi
}

fetch() {
  local url="$1"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$url"
  else
    echo "❌ Neither curl nor wget is available"
    exit 1
  fi
}

# ---------------------------
# Detect platform
# ---------------------------
OS="$(uname -s)"
ARCH="$(uname -m)"
BINARY=""

case "$OS" in
  Linux)
    if [[ "$ARCH" == "x86_64" ]]; then
      BINARY="ZeuZ_Node_linux"
    elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
      BINARY="ZeuZ_Node_linux_arm64"
    else
      echo "❌ Unsupported Linux architecture: $ARCH"
      exit 1
    fi
    ;;
  Darwin)
    if [[ "$ARCH" == "x86_64" ]]; then
      BINARY="ZeuZ_Node_macos"
    elif [[ "$ARCH" == "arm64" ]]; then
      BINARY="ZeuZ_Node_macos_amd64"
    else
      echo "❌ Unsupported macOS architecture: $ARCH"
      exit 1
    fi
    ;;
  *)
    echo "❌ Unsupported OS: $OS"
    exit 1
    ;;
esac

echo "✅ OS: $OS"
echo "✅ Arch: $ARCH"
echo "➡️  Binary: $BINARY"

# ---------------------------
# Resolve latest release URL
# ---------------------------
DOWNLOAD_URL=$(
  fetch "$API_URL" |
  grep browser_download_url |
  grep "$BINARY\"" |
  cut -d '"' -f 4
)

if [[ -z "$DOWNLOAD_URL" ]]; then
  echo "❌ Could not find binary in latest release"
  exit 1
fi

# ---------------------------
# Download + run
# ---------------------------
echo "⬇️  Downloading latest release..."
download "$DOWNLOAD_URL" "$BINARY"

chmod +x "$BINARY"

echo "🚀 Running ZeuZ Node..."
./"$BINARY"
