# Node.js Installer Package

This package provides functionality to install Node.js locally and set up Appium with required drivers.

## Features

- Downloads and installs Node.js v20.18.0 locally in `~/.zeuz/nodejs`
- Cross-platform support (macOS, Linux, Windows)
- Installs Appium globally using the local Node.js installation
- Installs UiAutomator2 and XCUITest drivers for mobile automation

## Functions

### `InstallNodeJS() error`
Downloads and installs Node.js locally. Skips installation if Node.js is already present.

### `InstallAppium() error`
Installs Appium and the following drivers:
- `appium-uiautomator2-driver` (Android)
- `appium-xcuitest-driver` (iOS)

### `GetNodePath() (string, error)`
Returns the path to the local Node.js binary.

### `GetNpmPath() (string, error)`
Returns the path to the local npm binary.

## Usage

The installation is automatically triggered when running the main application. Node.js and Appium will be installed before the ZeuZ Node setup process.
