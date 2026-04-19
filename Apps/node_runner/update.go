package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
	"unicode/utf8"
)

const (
	colorYellow = "\033[33m"
	colorReset  = "\033[0m"
)

// UpdateCache stores cached update info
type UpdateCache struct {
	TagName string `json:"tag_name"`
	HTMLURL string `json:"html_url"`
}

// getUpdateCachePath returns the path to the update cache file
func getUpdateCachePath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	zeuzDir := filepath.Join(home, ".zeuz")
	return filepath.Join(zeuzDir, "update_cache.json"), nil
}

// saveUpdateCache saves cached update info to disk
func saveUpdateCache(tagName, htmlURL string) error {
	path, err := getUpdateCachePath()
	if err != nil {
		return err
	}

	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	cache := UpdateCache{TagName: tagName, HTMLURL: htmlURL}
	data, err := json.MarshalIndent(cache, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(path, data, 0644)
}

// loadUpdateCache loads cached update info from disk
func loadUpdateCache() *UpdateCache {
	path, err := getUpdateCachePath()
	if err != nil {
		return nil
	}

	data, err := os.ReadFile(path)
	if err != nil {
		return nil
	}

	var cache UpdateCache
	if err := json.Unmarshal(data, &cache); err != nil {
		return nil
	}
	return &cache
}

// fetchLatestRelease fetches the latest release info from GitHub API.
// Returns tag name, HTML URL, and error.
func fetchLatestRelease() (tagName, htmlURL string, err error) {
	if version == "dev" || strings.HasPrefix(version, "dev-") {
		return "", "", fmt.Errorf("dev version")
	}

	client := &http.Client{Timeout: 15 * time.Second}
	resp, err := client.Get("https://api.github.com/repos/AutomationSolutionz/Zeuz_Python_Node/releases/latest")
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", "", fmt.Errorf("bad status: %s", resp.Status)
	}

	var release struct {
		TagName string `json:"tag_name"`
		HTMLURL string `json:"html_url"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&release); err != nil {
		return "", "", err
	}

	return release.TagName, release.HTMLURL, nil
}

// checkForUpdatesAsync fetches latest release info asynchronously and caches it
func checkForUpdatesAsync() {
	go func() {
		tagName, _, err := fetchLatestRelease()
		if err != nil {
			return
		}
		saveUpdateCache(tagName, "")
	}()
}

// performSelfUpdateWithInfo downloads and replaces the current binary with the specified version
// Returns true on failure (caller should continue), false on success (caller should exit)
func performSelfUpdateWithInfo(tagName, htmlURL string) bool {
	execPath, err := os.Executable()
	if err != nil {
		fmt.Printf("Error: Could not determine current executable: %v\n", err)
		return true // Continue execution on failure
	}
	fmt.Printf("Current executable path: %s\n", execPath)

	// Determine binary name based on OS/arch (matches Makefile output)
	var binName string
	switch runtime.GOOS {
	case "windows":
		if runtime.GOARCH == "arm64" {
			binName = "ZeuZ_Node_arm64.exe"
		} else {
			binName = "ZeuZ_Node.exe"
		}
	case "darwin":
		if runtime.GOARCH == "arm64" {
			binName = "ZeuZ_Node_macos"
		} else {
			binName = "ZeuZ_Node_macos_amd64"
		}
	case "linux":
		if runtime.GOARCH == "arm64" {
			binName = "ZeuZ_Node_linux_arm64"
		} else {
			binName = "ZeuZ_Node_linux"
		}
	default:
		binName = "ZeuZ_Node"
	}

	// Download to same directory as executable (avoids cross-drive rename issues)
	execDir := filepath.Dir(execPath)
	newBinPath := filepath.Join(execDir, binName+".new")
	backupPath := filepath.Join(execDir, binName+".old")

	downloadURL := fmt.Sprintf("https://github.com/AutomationSolutionz/Zeuz_Python_Node/releases/download/%s/%s", tagName, binName)
	fmt.Printf("Downloading update from: %s\n", downloadURL)
	fmt.Printf("Downloading to: %s\n", newBinPath)

	if err := downloadFile(downloadURL, newBinPath); err != nil {
		fmt.Printf("Error: Failed to download update: %v\n", err)
		return true // Continue execution on failure
	}
	fmt.Printf("Download complete.\n")

	if runtime.GOOS != "windows" {
		if err := os.Chmod(newBinPath, 0755); err != nil {
			fmt.Printf("Error: Failed to make executable: %v\n", err)
			os.Remove(newBinPath)
			return true // Continue execution on failure
		}
	}

	// Replace old with .old, new with current
	fmt.Printf("Replacing old executable...\n")

	// Remove old backup if exists
	os.Remove(backupPath)

	// Rename current to .old
	fmt.Printf("Renaming current -> backup: %s -> %s\n", execPath, backupPath)
	if err := os.Rename(execPath, backupPath); err != nil {
		fmt.Printf("Error: Could not rename old executable (may be locked): %v\n", err)
		fmt.Printf("Please close Zeuz Node and run the update manually.\n")
		os.Remove(newBinPath)
		return true // Continue execution on failure
	}

	// Rename new to current
	fmt.Printf("Renaming new -> current: %s -> %s\n", newBinPath, execPath)
	if err := os.Rename(newBinPath, execPath); err != nil {
		fmt.Printf("Error: Failed to install new executable: %v\n", err)
		fmt.Printf("Restoring backup...\n")
		os.Rename(backupPath, execPath)
		os.Remove(newBinPath)
		return true // Continue execution on failure
	}

	// Remove backup
	fmt.Printf("Removing backup: %s\n", backupPath)
	os.Remove(backupPath)

	fmt.Printf("✅ Update complete! Please restart Zeuz Node.\n")

	// Wait 2 seconds so user can read the log
	time.Sleep(2 * time.Second)
	fmt.Printf("\nPress Enter to exit...")
	fmt.Scanln()
	os.Exit(0)
	return false // Never reached
}

// parseVersion parses a version string into a slice of integers for comparison
func parseVersion(versionString string) []int {
	versionString = strings.TrimPrefix(versionString, "v")
	versionString = strings.Split(versionString, "-")[0]

	var parsed []int
	for _, part := range strings.Split(versionString, ".") {
		if num, err := strconv.Atoi(part); err == nil {
			parsed = append(parsed, num)
		}
	}
	return parsed
}

// compareVersions compares two version slices, returns true if a > b
func compareVersions(a, b []int) bool {
	for i := 0; i < len(a) && i < len(b); i++ {
		if a[i] > b[i] {
			return true
		}
		if a[i] < b[i] {
			return false
		}
	}
	return len(a) > len(b)
}

// printUpgradeBanner prints a compact upgrade notification banner.
func printUpgradeBanner(current, latest string) {
	width := 52
	line1 := fmt.Sprintf("  Update available: %s → %s", current, latest)
	line2 := "  Run with --upgrade to upgrade"
	pad := func(s string) string {
		spaces := width - utf8.RuneCountInString(s)
		if spaces < 0 {
			spaces = 0
		}
		return s + strings.Repeat(" ", spaces) + "║"
	}
	border := "╔" + strings.Repeat("═", width) + "╗"
	bottom := "╚" + strings.Repeat("═", width) + "╝"
	fmt.Println(colorYellow + border)
	fmt.Println("║" + pad(line1))
	fmt.Println("║" + pad(line2))
	fmt.Println(bottom + colorReset)
}

// PerformUpgrade fetches latest version from GitHub and performs the upgrade.
// Returns true if upgrade was performed (binary will exit), false if not.
func PerformUpgrade() bool {
	currentVersionStr := getZeuZNodeVersion()

	fmt.Println("Checking for latest version...")
	tagName, htmlURL, err := fetchLatestRelease()
	if err != nil {
		fmt.Printf("Failed to fetch latest release: %v\n", err)
		return false
	}

	latestVersion := parseVersion(tagName)
	currentVersion := parseVersion(currentVersionStr)
	if !compareVersions(latestVersion, currentVersion) {
		fmt.Println("✅ You are running the latest version. No upgrade needed.")
		return false
	}

	fmt.Println()
	printUpgradeBanner(
		strings.TrimPrefix(currentVersionStr, "v"),
		strings.TrimPrefix(tagName, "v"),
	)
	fmt.Println("  Release notes:", htmlURL)
	fmt.Println()
	fmt.Println("Starting upgrade...")

	return !performSelfUpdateWithInfo(tagName, htmlURL)
}

// HandleUpdateFlow checks for updates in background and shows banner if available.
// Returns true if execution should continue, false if binary was updated and should exit.
func HandleUpdateFlow() bool {
	// Get current version from the Zeuz_Node folder name (if it exists)
	currentVersionStr := getZeuZNodeVersion()
	if currentVersionStr == "" {
		// Can't determine version from folder, skip update check
		checkForUpdatesAsync()
		return true
	}

	cachedUpdate := loadUpdateCache()
	if cachedUpdate == nil {
		// No cached update info, start async check for next time and continue
		checkForUpdatesAsync()
		return true
	}

	cachedVersion := parseVersion(cachedUpdate.TagName)
	currentVersion := parseVersion(currentVersionStr)
	if !compareVersions(cachedVersion, currentVersion) {
		// No update available
		checkForUpdatesAsync()
		return true
	}

	// Show yellow banner with update info (non-blocking)
	fmt.Println()
	printUpgradeBanner(
		strings.TrimPrefix(currentVersionStr, "v"),
		strings.TrimPrefix(cachedUpdate.TagName, "v"),
	)
	fmt.Println()

	// Refresh cache in background
	checkForUpdatesAsync()
	return true
}

// getZeuZNodeVersion extracts version from Zeuz_Node folder name
// Returns empty string if folder doesn't exist or can't determine version
func getZeuZNodeVersion() string {
	folderName := getZeuZNodeDir()
	// Check if folder exists
	if _, err := os.Stat(folderName); os.IsNotExist(err) {
		return "" // Folder doesn't exist, can't determine version
	}

	// Folder name format is "ZeuZ_Node-<version>"
	prefix := "ZeuZ_Node-"
	if strings.HasPrefix(folderName, prefix) {
		return strings.TrimPrefix(folderName, prefix)
	}
	return ""
}
