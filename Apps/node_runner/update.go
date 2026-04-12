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
)

// UpdateInfo holds the latest version info from async check or cache
var latestVersionInfo = struct {
	tagName string
	htmlURL string
	checked bool
}{}

// UpdatePrefs stores user update preferences
type UpdatePrefs struct {
	DismissedVersion string `json:"dismissed_version"` // Version user declined
	AutoUpdate      bool   `json:"auto_update"`       // Auto-update without asking
}

// UpdateCache stores cached update info
type UpdateCache struct {
	TagName string `json:"tag_name"`
	HTMLURL string `json:"html_url"`
}

// getUpdatePrefsPath returns the path to the update preferences file
func getUpdatePrefsPath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	zeuzDir := filepath.Join(home, ".zeuz")
	return filepath.Join(zeuzDir, "update_prefs.json"), nil
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

// loadUpdatePrefs loads user update preferences from disk
func loadUpdatePrefs() (*UpdatePrefs, error) {
	path, err := getUpdatePrefsPath()
	if err != nil {
		return nil, err
	}

	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return &UpdatePrefs{}, nil
		}
		return nil, err
	}

	var prefs UpdatePrefs
	if err := json.Unmarshal(data, &prefs); err != nil {
		return &UpdatePrefs{}, nil
	}
	return &prefs, nil
}

// saveUpdatePrefs saves user update preferences to disk
func saveUpdatePrefs(prefs *UpdatePrefs) error {
	path, err := getUpdatePrefsPath()
	if err != nil {
		return err
	}

	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	data, err := json.MarshalIndent(prefs, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(path, data, 0644)
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

// checkForUpdatesAsync fetches latest release info asynchronously and caches it
func checkForUpdatesAsync() {
	if version == "dev" || strings.HasPrefix(version, "dev-") {
		return
	}

	go func() {
		client := &http.Client{Timeout: 15 * time.Second}
		resp, err := client.Get("https://api.github.com/repos/AutomationSolutionz/Zeuz_Python_Node/releases/latest")
		if err != nil {
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			return
		}

		var release struct {
			TagName string `json:"tag_name"`
			HTMLURL string `json:"html_url"`
		}
		if err := json.NewDecoder(resp.Body).Decode(&release); err != nil {
			return
		}

		latestVersion := parseVersion(release.TagName)
		currentVersion := parseVersion(version)

		if compareVersions(latestVersion, currentVersion) {
			latestVersionInfo.tagName = release.TagName
			latestVersionInfo.htmlURL = release.HTMLURL
			latestVersionInfo.checked = true

			// Cache the update info for next startup
			saveUpdateCache(release.TagName, release.HTMLURL)
		}
	}()
}

// handleUpdatePromptWithInfo shows update prompt with provided version info
func handleUpdatePromptWithInfo(latestTag, htmlURL string) bool {
	prefs, err := loadUpdatePrefs()
	if err != nil {
		return true
	}

	// If auto-update is enabled, update without asking
	if prefs.AutoUpdate {
		fmt.Println("Auto-updating to latest version...")
		return performSelfUpdateWithInfo(latestTag, htmlURL)
	}

	// If user previously dismissed this exact version, don't ask again
	if prefs.DismissedVersion == latestTag {
		return true
	}

	fmt.Printf("\n")
	fmt.Printf("╔══════════════════════════════════════════════════════════════╗\n")
	fmt.Printf("║           ⚠️  Update Available: Zeuz Node %s → %s    ║\n",
		strings.TrimPrefix(version, "v"), strings.TrimPrefix(latestTag, "v"))
	fmt.Printf("╠══════════════════════════════════════════════════════════════╣\n")
	fmt.Printf("║  Release notes: %s                ║\n", htmlURL)
	fmt.Printf("╠══════════════════════════════════════════════════════════════╣\n")
	fmt.Printf("║  [Y] Yes, update now                                        ║\n")
	fmt.Printf("║  [N] No, ask me again next time                             ║\n")
	fmt.Printf("║  [D] Don't ask again for this version                        ║\n")
	fmt.Printf("║  [A] Always update without asking                            ║\n")
	fmt.Printf("╚══════════════════════════════════════════════════════════════╝\n")
	fmt.Printf("Choice (Y/N/D/A): ")

	var choice string
	fmt.Scanln(&choice)
	choice = strings.ToUpper(strings.TrimSpace(choice))

	switch choice {
	case "Y", "":
		fmt.Println("Updating...")
		return performSelfUpdateWithInfo(latestTag, htmlURL)
	case "N":
		fmt.Println("Update postponed.")
		return true
	case "D":
		prefs.DismissedVersion = latestTag
		if err := saveUpdatePrefs(prefs); err != nil {
			fmt.Printf("Warning: Failed to save preference: %v\n", err)
		}
		fmt.Println("Update dismissed for this version.")
		return true
	case "A":
		prefs.AutoUpdate = true
		prefs.DismissedVersion = ""
		if err := saveUpdatePrefs(prefs); err != nil {
			fmt.Printf("Warning: Failed to save preference: %v\n", err)
		}
		fmt.Println("Auto-update enabled. Updating...")
		return performSelfUpdateWithInfo(latestTag, htmlURL)
	default:
		fmt.Println("Invalid choice. Update postponed.")
		return true
	}
}

// performSelfUpdate downloads and replaces the current binary with the latest version
func performSelfUpdate() bool {
	if latestVersionInfo.tagName == "" {
		fmt.Println("No update information available.")
		return false
	}
	return performSelfUpdateWithInfo(latestVersionInfo.tagName, latestVersionInfo.htmlURL)
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

// HandleUpdateFlow checks for updates and handles user interaction.
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

	prefs, _ := loadUpdatePrefs()
	if prefs.AutoUpdate {
		fmt.Println("Auto-updating to latest version...")
		performSelfUpdateWithInfo(cachedUpdate.TagName, cachedUpdate.HTMLURL)
		return false
	}

	if prefs.DismissedVersion == cachedUpdate.TagName {
		// User dismissed this version
		checkForUpdatesAsync()
		return true
	}

	// Show update prompt
	checkForUpdatesAsync() // Refresh cache in background
	return handleUpdatePromptWithInfo(cachedUpdate.TagName, cachedUpdate.HTMLURL)
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
