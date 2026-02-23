#!/bin/sh
set -e

REPO="AutomationSolutionz/Zeuz_Python_Node"
API_URL="https://api.github.com/repos/$REPO/releases/latest"
DIRECT_DOWNLOAD_BASE="https://github.com/$REPO/releases/latest/download"

# ---------------------------
# Downloader helper
# ---------------------------
download() {
  local_url="$1"
  local_output="$2"

  if command -v curl >/dev/null 2>&1; then
    if [ -n "$GITHUB_TOKEN" ]; then
      curl -fL --retry 3 --retry-delay 1 --http1.1 \
        -H "User-Agent: ZeuZ-Installer" \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        "$local_url" -o "$local_output"
    else
      curl -fL --retry 3 --retry-delay 1 --http1.1 \
        -H "User-Agent: ZeuZ-Installer" \
        "$local_url" -o "$local_output"
    fi
  elif command -v wget >/dev/null 2>&1; then
    if [ -n "$GITHUB_TOKEN" ]; then
      wget -q \
        --header="User-Agent: ZeuZ-Installer" \
        --header="Authorization: Bearer $GITHUB_TOKEN" \
        -O "$local_output" "$local_url"
    else
      wget -q \
        --header="User-Agent: ZeuZ-Installer" \
        -O "$local_output" "$local_url"
    fi
  else
    echo "❌ Neither curl nor wget is available"
    exit 1
  fi
}

fetch() {
  local_url="$1"

  if command -v curl >/dev/null 2>&1; then
    if [ -n "$GITHUB_TOKEN" ]; then
      curl -fL --retry 3 --retry-delay 1 --http1.1 \
        -H "Accept: application/vnd.github+json" \
        -H "User-Agent: ZeuZ-Installer" \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        "$local_url"
    else
      curl -fL --retry 3 --retry-delay 1 --http1.1 \
        -H "Accept: application/vnd.github+json" \
        -H "User-Agent: ZeuZ-Installer" \
        "$local_url"
    fi
  elif command -v wget >/dev/null 2>&1; then
    if [ -n "$GITHUB_TOKEN" ]; then
      wget -qO- \
        --header="Accept: application/vnd.github+json" \
        --header="User-Agent: ZeuZ-Installer" \
        --header="Authorization: Bearer $GITHUB_TOKEN" \
        "$local_url"
    else
      wget -qO- \
        --header="Accept: application/vnd.github+json" \
        --header="User-Agent: ZeuZ-Installer" \
        "$local_url"
    fi
  else
    echo "❌ Neither curl nor wget is available"
    exit 1
  fi
}

# ---------------------------
# Detect platform
# ---------------------------
OS=$(uname -s)
ARCH=$(uname -m)
BINARY=""

case "$OS" in
  Linux)
    if [ "$ARCH" = "x86_64" ]; then
      BINARY="ZeuZ_Node_linux"
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
      BINARY="ZeuZ_Node_linux_arm64"
    else
      echo "❌ Unsupported Linux architecture: $ARCH"
      exit 1
    fi
    ;;
  Darwin)
    if [ "$ARCH" = "arm64" ]; then
      BINARY="ZeuZ_Node_macos"
    elif [ "$ARCH" = "x86_64" ]; then
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
# Download + run
# ---------------------------
echo "⬇️  Downloading latest release..."
DIRECT_URL="$DIRECT_DOWNLOAD_BASE/$BINARY"

if ! download "$DIRECT_URL" "$BINARY"; then
  echo "⚠️  Direct download failed. Trying GitHub Releases API..."

  if ! RELEASE_JSON=$(fetch "$API_URL"); then
    echo "❌ Failed to query GitHub latest release (API access denied or rate limited)."
    echo "   If this is a private repo or you hit the GitHub API limit, set GITHUB_TOKEN and retry."
    exit 1
  fi

  # Using grep and cut for compatibility across different environments
  DOWNLOAD_URL=$(
    printf '%s\n' "$RELEASE_JSON" |
    grep "browser_download_url" |
    grep "/$BINARY\"" |
    cut -d '"' -f 4
  )

  if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Could not find binary '$BINARY' in latest release assets"
    exit 1
  fi

  download "$DOWNLOAD_URL" "$BINARY"
fi

chmod +x "$BINARY"

echo "🚀 Running ZeuZ Node..."
./"$BINARY"
