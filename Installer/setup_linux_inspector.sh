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

BREW_PACKAGES=(
  cmake
  pkg-config
  cairo
  xdotool
  gobject-introspection
  imagemagick
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
  sudo dnf install -y $(join_packages "${DNF_PACKAGES[@]}")

elif command -v pacman >/dev/null 2>&1; then
  echo "Using Pacman (Arch-based)"
  sudo pacman -Sy --noconfirm $(join_packages "${PACMAN_PACKAGES[@]}")

elif command -v brew >/dev/null 2>&1; then
  echo "Using Homebrew (macOS)"
  brew install $(join_packages "${BREW_PACKAGES[@]}")

else
  echo "❌ No supported package manager found (apt, dnf, pacman, brew)"
  exit 1
fi

echo "✅ Installation complete."

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
