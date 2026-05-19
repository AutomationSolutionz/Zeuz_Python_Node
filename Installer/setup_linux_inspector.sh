#!/usr/bin/env bash

set -e

# List of required packages for each package manager
APT_PACKAGES=(
  build-essential
  cmake
  pkg-config
  libgirepository1.0-dev
  libcairo2-dev
  xdotool
  x11-apps            # provides xwd
  imagemagick         # provides convert, import
  wmctrl
)

DNF_PACKAGES=(
  cmake
  pkgconf-pkg-config
  gobject-introspection-devel
  cairo-devel
  xdotool
  xorg-x11-utils      # provides xwd on some distros
  ImageMagick
  wmctrl
  python3-devel
  cairo-gobject-devel
)

PACMAN_PACKAGES=(
  gcc
  meson
  cmake
  pkgconf
  cairo
  xdotool
  gobject-introspection
  imagemagick
  wmctrl
)

# Function to join array into space-separated string
join_packages() {
  local IFS=" "
  echo "$*"
}

# Detect and install using the available package manager
if command -v apt >/dev/null 2>&1; then
  echo "Using APT (Debian/Ubuntu-based)"
  sudo apt update
  sudo apt install -y $(join_packages "${APT_PACKAGES[@]}")

elif command -v dnf >/dev/null 2>&1; then
  echo "Using DNF (Fedora-based)"

  # Alma Linux 9 (and RHEL 9 derivatives) need extra repos and a specific install order
  if grep -qiE "AlmaLinux.*9|Red Hat.*9|Rocky.*9" /etc/os-release 2>/dev/null; then
    echo "Detected Alma/RHEL 9 — using extended setup sequence"
    sudo dnf groupinstall "Development Tools" -y
    sudo dnf install -y cairo-devel pkg-config
    sudo dnf config-manager --set-enabled crb
    sudo dnf install -y gobject-introspection-devel at-spi2-core-devel cairo-gobject-devel
    sudo dnf install -y epel-release
    sudo dnf install -y xwd xdotool ImageMagick wmctrl python3-devel
  else
    sudo dnf install -y $(join_packages "${DNF_PACKAGES[@]}")
  fi

elif command -v pacman >/dev/null 2>&1; then
  echo "Using Pacman (Arch-based)"
  sudo pacman -Sy --noconfirm $(join_packages "${PACMAN_PACKAGES[@]}")

else
  echo "❌ No supported package manager found (apt, dnf, pacman, brew)"
  exit 1
fi

echo "✅ Installation complete."

# --- Accessibility environment variables ---
ACCESSIBILITY_VARS=(
  'export NO_AT_BRIDGE=0'
  'export GTK_MODULES=gail:atk-bridge'
  'export ACCESSIBILITY_ENABLED=1'
)

add_env_vars() {
  local rc_file="$1"
  local marker="# zeuz-accessibility"
  if grep -q "$marker" "$rc_file" 2>/dev/null; then
    echo "Accessibility vars already present in $rc_file — skipping"
    return
  fi
  {
    echo ""
    echo "$marker"
    for line in "${ACCESSIBILITY_VARS[@]}"; do echo "$line"; done
  } >> "$rc_file"
  echo "Added accessibility vars to $rc_file"
}

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [ -f "$rc" ] && add_env_vars "$rc"
done

# Apply to the current session as well
for line in "${ACCESSIBILITY_VARS[@]}"; do eval "$line"; done

# --- GNOME accessibility setting ---
if command -v gsettings >/dev/null 2>&1; then
  gsettings set org.gnome.desktop.interface toolkit-accessibility true
  echo "GNOME toolkit-accessibility enabled"
else
  echo "gsettings not found — skipping GNOME accessibility setting"
fi

# Post-install sanity checks for screenshot/capture utilities
echo "\nChecking availability of key utilities:" 
REQUIRED_TOOLS=(xdotool xwd convert import wmctrl)
for t in "${REQUIRED_TOOLS[@]}"; do
  if command -v "$t" >/dev/null 2>&1; then
    echo " - $t: available"
  else
    echo " - $t: NOT FOUND"
  fi
done

echo "If any of the above are missing, please install them for full Linux inspector functionality."
