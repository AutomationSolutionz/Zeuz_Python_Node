package main

import (
	"archive/zip"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/automationsolutionz/Zeuz_Python_Node/Apps/node_runner/uv_installer"
)

var (
	version       = "dev"
	targetVersion string // runtime override; empty = use build-time version
	branch        = flag.String("branch", "", "Branch to download (defaults to tagged version)")
	cleanFlag     = flag.Bool("clean", false, "Remove ZeuZ Node directory and $HOME/.zeuz and exit")
	updateFlag    = flag.Bool("update", false, "Download and install the latest ZeuZ Node version")
)

const (
	colorReset  = "\033[0m"
	colorGreen  = "\033[32m"
	colorYellow = "\033[33m"
	colorBold   = "\033[1m"
)

type zeuzRelease struct {
	TagName string `json:"tag_name"`
}

// versionCache persists the last GitHub version check result to disk so the
// network call is skipped on subsequent startups within the cache window.
type versionCache struct {
	CheckedAt time.Time `json:"checked_at"`
	Latest    string    `json:"latest"`
}

const versionCheckInterval = 24 * time.Hour

var errRateLimited = errors.New("GitHub API rate limited — try again later")

// versionCachePath returns the path to the version cache file.
func versionCachePath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}
	return filepath.Join(home, ".zeuz", "version_check_cache.json")
}

// loadVersionCache reads the cache file. Returns nil if missing, unreadable,
// or older than versionCheckInterval.
func loadVersionCache() *versionCache {
	path := versionCachePath()
	if path == "" {
		return nil
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return nil
	}
	var cache versionCache
	if err := json.Unmarshal(data, &cache); err != nil {
		return nil
	}
	if time.Since(cache.CheckedAt) > versionCheckInterval {
		return nil // expired
	}
	return &cache
}

// saveVersionCache writes the latest version and current timestamp to disk.
func saveVersionCache(latest string) {
	path := versionCachePath()
	if path == "" {
		return
	}
	os.MkdirAll(filepath.Dir(path), 0755)
	data, err := json.Marshal(versionCache{CheckedAt: time.Now(), Latest: latest})
	if err != nil {
		return
	}
	os.WriteFile(path, data, 0644)
}

func effectiveVersion() string {
	if targetVersion != "" {
		return targetVersion
	}
	return version
}

// fetchLatestVersion fetches the latest ZeuZ Node release tag from GitHub
func fetchLatestVersion() (string, error) {
	client := &http.Client{Timeout: 5 * time.Second}
	req, err := http.NewRequest("GET",
		"https://api.github.com/repos/AutomationSolutionz/Zeuz_Python_Node/releases/latest",
		nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("User-Agent", "zeuz-node-runner/"+version)
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode == 403 {
		return "", errRateLimited
	}
	if resp.StatusCode != 200 {
		return "", fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var r zeuzRelease
	json.NewDecoder(resp.Body).Decode(&r)
	return r.TagName, nil
}

// printUpdateBanner prints a styled update available notice
func printUpdateBanner(current, latest string) {
	width := 52
	line1 := fmt.Sprintf("  Update available: %s → %s", current, latest)
	line2 := "  Run with --update to upgrade"
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

// runUpdate fetches the latest release and replaces the current ZeuZ Node directory
func runUpdate() error {
	if *branch != "" {
		return fmt.Errorf("--update is not compatible with --branch")
	}
	if version == "dev" || strings.HasPrefix(version, "dev-") {
		fmt.Println("  Dev build — skipping update check")
		return nil
	}

	fmt.Println("  Checking for updates...")
	latest, err := fetchLatestVersion()
	if err != nil {
		return fmt.Errorf("could not check for updates: %w", err)
	}

	if effectiveVersion() == latest {
		fmt.Printf(colorGreen+"  Already up to date (%s)"+colorReset+"\n", latest)
		return nil
	}

	fmt.Printf("  Updating %s → %s\n", effectiveVersion(), latest)
	oldDir := getZeuZNodeDir()
	os.RemoveAll(oldDir)

	targetVersion = latest
	if err := setupZeuzNode(); err != nil {
		return fmt.Errorf("update failed: %w", err)
	}

	// Refresh the cache so the next startup doesn't re-check immediately.
	saveVersionCache(latest)

	fmt.Printf(colorGreen+"  Update complete (%s)"+colorReset+"\n", latest)
	return nil
}

// progressReader wraps an io.Reader and prints download progress
type progressReader struct {
	reader io.Reader
	total  int64
	read   int64
}

func (p *progressReader) Read(buf []byte) (int, error) {
	n, err := p.reader.Read(buf)
	p.read += int64(n)
	if p.total > 0 {
		pct := (p.read * 100) / p.total
		fmt.Printf("\r  Downloading... %d%%  ", pct)
	} else {
		fmt.Printf("\r  Downloading... %.1f MB", float64(p.read)/1e6)
	}
	if err == io.EOF {
		fmt.Println()
	}
	return n, err
}

func downloadFile(url, destPath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to download file: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("bad status: %s", resp.Status)
	}

	out, err := os.CreateTemp("", "download-*")
	if err != nil {
		return fmt.Errorf("failed to create temp file: %v", err)
	}
	defer os.Remove(out.Name())

	pr := &progressReader{reader: resp.Body, total: resp.ContentLength}
	_, err = io.Copy(out, pr)
	if err != nil {
		out.Close()
		return fmt.Errorf("failed to write file: %v", err)
	}
	out.Close()

	// Make the file executable on Unix systems if it's a script
	if runtime.GOOS != "windows" {
		if err := os.Chmod(out.Name(), 0755); err != nil {
			return fmt.Errorf("failed to make file executable: %v", err)
		}
	}

	// Move the temp file to the destination
	if err := os.Rename(out.Name(), destPath); err != nil {
		return fmt.Errorf("failed to move file to destination: %v", err)
	}

	return nil
}

// unzip extracts a zip file to the specified destination
func unzip(zipFile, dest string) error {
	reader, err := zip.OpenReader(zipFile)
	if err != nil {
		return fmt.Errorf("failed to open zip file: %v", err)
	}
	defer reader.Close()

	// Create destination directory if it doesn't exist
	if err := os.MkdirAll(dest, 0755); err != nil {
		return fmt.Errorf("failed to create destination directory: %v", err)
	}

	// Get the root directory name from the first entry
	var rootDir string
	if len(reader.File) > 0 {
		rootDir = strings.Split(reader.File[0].Name, "/")[0]
	}

	for _, file := range reader.File {
		// Remove the root directory from the path
		relPath := strings.TrimPrefix(file.Name, rootDir+"/")
		if relPath == "" {
			continue
		}

		path := filepath.Join(dest, relPath)

		if file.FileInfo().IsDir() {
			os.MkdirAll(path, 0755)
			continue
		}

		// Ensure parent directory exists
		if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
			return fmt.Errorf("failed to create directory: %v", err)
		}

		outFile, err := os.Create(path)
		if err != nil {
			return fmt.Errorf("failed to create output file: %v", err)
		}

		rc, err := file.Open()
		if err != nil {
			outFile.Close()
			return fmt.Errorf("failed to open zip file entry: %v", err)
		}

		_, err = io.Copy(outFile, rc)
		rc.Close()
		outFile.Close()
		if err != nil {
			return fmt.Errorf("failed to copy file content: %v", err)
		}
	}

	return nil
}

// getZeuZNodeURL returns the appropriate download URL based on version and branch
func getZeuZNodeURL() string {
	if *branch != "" {
		return fmt.Sprintf("https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/heads/%s.zip", *branch)
	}
	ev := effectiveVersion()
	if ev != "dev" && !strings.HasPrefix(ev, "dev-") {
		return fmt.Sprintf("https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/tags/%s.zip", ev)
	}
	return "https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/heads/dev.zip"
}

func getZeuZNodeDir() string {
	selectedVersion := ""
	if *branch != "" {
		selectedVersion = *branch
	} else {
		ev := effectiveVersion()
		if ev != "dev" && !strings.HasPrefix(ev, "dev-") {
			selectedVersion = ev
		}
	}

	return fmt.Sprintf("ZeuZ_Node-%s", selectedVersion)
}

// setupZeuzNode downloads and extracts the ZeuZ Node repository if not already present
func setupZeuzNode() error {
	zeuzDir := getZeuZNodeDir()
	// Check if ZeuZ Node directory already exists and contains files
	if info, err := os.Stat(zeuzDir); err == nil && info.IsDir() {
		// Check if directory is not empty
		f, err := os.Open(zeuzDir)
		if err == nil {
			defer f.Close()
			_, err = f.Readdirnames(1) // Try to read at least one file
			if err == nil {            // Directory is not empty
				return nil
			}
		}
	}

	fmt.Println("  Setting up ZeuZ Node...")

	// Create temporary directory for zip file
	tempDir, err := os.MkdirTemp("", "zeuz-download")
	if err != nil {
		return fmt.Errorf("failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tempDir)

	// Download zip file
	zipPath := filepath.Join(tempDir, "zeuz.zip")
	zeuzURL := getZeuZNodeURL()
	fmt.Printf("  Fetching from: %s\n", zeuzURL)
	if err := downloadFile(zeuzURL, zipPath); err != nil {
		return err
	}

	// Remove existing ZeuZ Node directory if it exists
	if err := os.RemoveAll(zeuzDir); err != nil {
		return fmt.Errorf("failed to remove existing directory: %v", err)
	}

	// Extract zip file
	fmt.Println("  Extracting...")
	if err := unzip(zipPath, zeuzDir); err != nil {
		return err
	}

	return nil
}

// installUV installs the UV package manager if not already installed
func installUV() error {
	// Check if uv is already installed
	_, err := exec.LookPath("uv")
	if err == nil {
		return nil
	}

	fmt.Println("Installing UV...")

	if runtime.GOOS == "windows" {
		return uv_installer.InstallUVFromSource()
	} else {
		// For non-Windows systems, use the shell script
	tempDir, err := os.MkdirTemp("", "uv-install")
	if err != nil {
		return fmt.Errorf("failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tempDir)

		scriptURL := "https://astral.sh/uv/install.sh"
	scriptPath := filepath.Join(tempDir, "install.sh")

		if err := downloadFile(scriptURL, scriptPath); err != nil {
		return err
	}

	cmd := exec.Command("sh", scriptPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	return cmd.Run()
	}
}

// updatePath adds UV binary location to PATH
func updatePath() error {
	home, err := os.UserHomeDir()
	if err != nil {
		return fmt.Errorf("failed to get home directory: %v", err)
	}

	var uvPath string = filepath.Join(home, ".local", "bin")
	// Create .local/bin directory if it doesn't exist
	if err := os.MkdirAll(uvPath, 0755); err != nil {
		return fmt.Errorf("failed to create UV path directory: %v", err)
	}

	currentPath := os.Getenv("PATH")
	if !strings.Contains(currentPath, uvPath) {
		newPath := fmt.Sprintf("%s%s%s", uvPath, string(os.PathListSeparator), currentPath)
		os.Setenv("PATH", newPath)
	}
	return nil
}

// runUVCommands executes UV sync and run commands
func runUVCommands(args []string) error {
	// Run UV sync
	syncCmd := exec.Command("uv", "sync", "--link-mode=symlink")
	syncCmd.Stdout = os.Stdout
	syncCmd.Stderr = os.Stderr
	syncCmd.Stdin = os.Stdin
	if err := syncCmd.Run(); err != nil {
		return fmt.Errorf("failed to run uv sync: %v", err)
	}

	// Create the command slice starting with "uv" and "run"
	cmdArgs := []string{"run", "node_cli.py"}
	// Append any additional arguments
	cmdArgs = append(cmdArgs, args...)

	runCmd := exec.Command("uv", cmdArgs...)
	runCmd.Stdout = os.Stdout
	runCmd.Stderr = os.Stderr
	runCmd.Stdin = os.Stdin
	return runCmd.Run()
}

// showUpdateBannerIfNeeded reads the version cache and prints the update
// banner if the cached latest version differs from the running version.
// This is called at startup and again after node_cli.py exits so the user
// always sees a reminder. No network call — purely a cache file read.
func showUpdateBannerIfNeeded() {
	cache := loadVersionCache()
	if cache == nil {
		return
	}
	if cache.Latest != "" && cache.Latest != effectiveVersion() {
		printUpdateBanner(effectiveVersion(), cache.Latest)
	}
}

func main() {
	flag.Parse()

	fmt.Printf(colorGreen+colorBold+"  ZeuZ Node %s"+colorReset+"\n", version)

	// Refresh the version cache in the background (once per 24h).
	// Just writes to the cache file — showUpdateBannerIfNeeded() reads it.
	go func() {
		if loadVersionCache() != nil {
			return // cache still fresh, nothing to do
		}
		latest, err := fetchLatestVersion()
		if err != nil {
			return
		}
		saveVersionCache(latest)
	}()

	// Show update banner at startup using whatever is in the cache.
	// On first ever run the cache is empty so nothing shows yet.
	showUpdateBannerIfNeeded()

	zeuzDir := getZeuZNodeDir()

	if *cleanFlag {
		var removedAny bool
		if err := os.RemoveAll(zeuzDir); err == nil {
			fmt.Printf(colorYellow+"  Removed %s"+colorReset+"\n", zeuzDir)
			removedAny = true
		} else if !os.IsNotExist(err) {
			fmt.Printf("  Failed to remove %s: %v\n", zeuzDir, err)
		}

		home, err := os.UserHomeDir()
		if err == nil {
			zeuzHome := filepath.Join(home, ".zeuz")
			if err := os.RemoveAll(zeuzHome); err == nil {
				fmt.Printf(colorYellow+"  Removed %s"+colorReset+"\n", zeuzHome)
				removedAny = true
			} else if !os.IsNotExist(err) {
				fmt.Printf("  Failed to remove %s: %v\n", zeuzHome, err)
			}
		} else {
			fmt.Printf("  Could not determine user home dir: %v\n", err)
		}

		if !removedAny {
			fmt.Println("  Nothing removed. No matching directories found.")
		} else {
			fmt.Println(colorGreen + "  Cleanup complete — downloading fresh copy." + colorReset)
		}
	}

	if *updateFlag {
		if err := runUpdate(); err != nil {
			fmt.Printf(colorYellow+"  Warning: %v"+colorReset+"\n", err)
			os.Exit(1)
		}
	}

	// Setup ZeuZ Node directory and change into it
	if err := setupZeuzNode(); err != nil {
		fmt.Printf("  Error setting up ZeuZ Node: %v\n", err)
		os.Exit(1)
	}

	// Re-evaluate after potential targetVersion change by runUpdate.
	zeuzDir = getZeuZNodeDir()
	if err := os.Chdir(zeuzDir); err != nil {
		fmt.Printf("  Error changing to ZeuZ Node directory: %v\n", err)
		os.Exit(1)
	}

	if err := updatePath(); err != nil {
		fmt.Printf("  Error updating path: %v\n", err)
	}

	// Install UV if needed
	if err := installUV(); err != nil {
		fmt.Printf("  Error installing UV: %v\n", err)
		os.Exit(1)
	}

	// Update PATH to ensure UV is available after installation
	if err := updatePath(); err != nil {
		fmt.Printf("  Error updating path: %v\n", err)
	}

	// Get remaining command line arguments after flag parsing
	args := flag.Args()
	runErr := runUVCommands(args)

	// Show update banner again after node_cli.py exits.
	showUpdateBannerIfNeeded()

	if runErr != nil {
		fmt.Printf("  Error running UV commands: %v\n", runErr)
		os.Exit(1)
	}
}
