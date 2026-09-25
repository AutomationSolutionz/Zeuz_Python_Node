package main

import (
	"archive/zip"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strings"

	"github.com/automationsolutionz/Zeuz_Python_Node/Apps/node_runner/uv_installer"
)

var (
	version    = "dev"
	branch     = flag.String("branch", "", "Branch to download (defaults to tagged version)")
	cleanFlag  = flag.Bool("clean", false, "Remove ZeuZ Node directory and $HOME/.zeuz and exit")
	upgradeFlag = flag.Bool("upgrade", false, "Check for updates and upgrade if available")
)

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

	_, err = io.Copy(out, resp.Body)
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

	// Move the temp file to the destination (on Windows, rename can't cross drives)
	if err := os.Rename(out.Name(), destPath); err != nil {
		if runtime.GOOS == "windows" {
			// Cross-device rename failed, use copy instead
			src, err := os.Open(out.Name())
			if err != nil {
				return fmt.Errorf("failed to open temp file: %v", err)
			}
			defer src.Close()

			dst, err := os.Create(destPath)
			if err != nil {
				return fmt.Errorf("failed to create destination: %v", err)
			}
			defer dst.Close()

			if _, err := io.Copy(dst, src); err != nil {
				return fmt.Errorf("failed to copy file: %v", err)
			}
			return nil
		}
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
	if version != "dev" && !strings.HasPrefix(version, "dev-") {
		return fmt.Sprintf("https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/tags/%s.zip", version)
	}
	return "https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/heads/dev.zip"
}

func getZeuZNodeDir() string {
	selectedVersion := ""
	if *branch != "" {
		selectedVersion = *branch
	}
	if version != "dev" && !strings.HasPrefix(version, "dev-") {
		selectedVersion = version
	}
	if selectedVersion == "" {
		selectedVersion = "dev"
	}

	return fmt.Sprintf("ZeuZ_Node-%s", selectedVersion)
}

func containsNodeCLI(dir string) bool {
	if info, err := os.Stat(filepath.Join(dir, "node_cli.py")); err == nil && !info.IsDir() {
		return true
	}
	return false
}

func findExistingZeuzNodeDir(expectedDir string) (string, error) {
	if info, err := os.Stat(expectedDir); err == nil && info.IsDir() && containsNodeCLI(expectedDir) {
		return expectedDir, nil
	}

	requestedSpecificRevision := *branch != "" || (version != "dev" && !strings.HasPrefix(version, "dev-"))
	if requestedSpecificRevision {
		return "", nil
	}

	entries, err := os.ReadDir(".")
	if err != nil {
		return "", fmt.Errorf("failed to read current directory: %v", err)
	}

	var candidates []string
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		name := entry.Name()
		if !strings.HasPrefix(name, "ZeuZ_Node-") {
			continue
		}
		if containsNodeCLI(name) {
			candidates = append(candidates, name)
		}
	}

	if len(candidates) == 0 {
		return "", nil
	}

	sort.Strings(candidates)
	return candidates[0], nil
}

func removeDirIfExists(path string) (bool, error) {
	if _, err := os.Stat(path); err != nil {
		if os.IsNotExist(err) {
			return false, nil
		}
		return false, err
	}

	if err := os.RemoveAll(path); err != nil {
		return false, err
	}

	return true, nil
}

func removeZeuzNodeDirs() (bool, error) {
	entries, err := os.ReadDir(".")
	if err != nil {
		return false, fmt.Errorf("failed to read current directory: %v", err)
	}

	removedAny := false
	for _, entry := range entries {
		if !entry.IsDir() || !strings.HasPrefix(entry.Name(), "ZeuZ_Node-") {
			continue
		}

		removed, err := removeDirIfExists(entry.Name())
		if err != nil {
			return removedAny, fmt.Errorf("failed to remove %s: %v", entry.Name(), err)
		}
		if removed {
			fmt.Printf("Removed %s\n", entry.Name())
			removedAny = true
		}
	}

	return removedAny, nil
}

// setupZeuzNode downloads and extracts the ZeuZ Node repository if not already present
func setupZeuzNode() (string, error) {
	zeuzDir := getZeuZNodeDir()

	existingDir, err := findExistingZeuzNodeDir(zeuzDir)
	if err != nil {
		return "", err
	}
	if existingDir != "" {
		if existingDir != zeuzDir {
			fmt.Printf("Using existing ZeuZ Node directory: %s\n", existingDir)
		}
		return existingDir, nil
	}

	fmt.Println("Setting up ZeuZ Node...")

	// Create temporary directory for zip file
	tempDir, err := os.MkdirTemp("", "zeuz-download")
	if err != nil {
		return "", fmt.Errorf("failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tempDir)

	// Download zip file
	zipPath := filepath.Join(tempDir, "zeuz.zip")
	zeuzURL := getZeuZNodeURL()
	fmt.Printf("Downloading ZeuZ Node repository from: %s\n", zeuzURL)
	if err := downloadFile(zeuzURL, zipPath); err != nil {
		return "", err
	}

	// Remove existing ZeuZ Node directory if it exists
	if err := os.RemoveAll(zeuzDir); err != nil {
		return "", fmt.Errorf("failed to remove existing directory: %v", err)
	}

	// Extract zip file
	fmt.Println("Extracting ZeuZ Node repository...")
	if err := unzip(zipPath, zeuzDir); err != nil {
		return "", err
	}

	return zeuzDir, nil
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

func main() {
	flag.Parse()

	fmt.Printf("✅ ZeuZ Node %s\n", version)

	// Handle upgrade flag - performs upgrade if available
	if *upgradeFlag {
		PerformUpgrade()
		return // Only reached if upgrade failed or not needed
	}

	// Check for updates (non-blocking, uses cached info from last run)
	if !HandleUpdateFlow() {
		return
	}

	zeuzDir := getZeuZNodeDir()

	if *cleanFlag {
		removedAny, err := removeZeuzNodeDirs()
		if err != nil {
			fmt.Printf("Failed during ZeuZ Node cleanup: %v\n", err)
		}

		home, err := os.UserHomeDir()
		if err == nil {
			zeuzHome := filepath.Join(home, ".zeuz")
			removed, removeErr := removeDirIfExists(zeuzHome)
			if removeErr != nil {
				fmt.Printf("Failed to remove %s: %v\n", zeuzHome, removeErr)
			} else if removed {
				fmt.Printf("Removed %s\n", zeuzHome)
				removedAny = true
			}
		} else {
			fmt.Printf("Could not determine user home dir: %v\n", err)
		}

		if !removedAny {
			fmt.Println("Nothing removed. No matching directories found.")
		} else {
			fmt.Println("Cleanup complete — proceeding to download & install a fresh copy.")
		}
	}

	// Setup ZeuZ Node directory and change into it
	resolvedZeuzDir, err := setupZeuzNode()
	if err != nil {
		fmt.Printf("Error setting up ZeuZ Node: %v\n", err)
		os.Exit(1)
	}
	zeuzDir = resolvedZeuzDir

	// Change directory to ZeuZ Node
	if err := os.Chdir(zeuzDir); err != nil {
		fmt.Printf("Error changing to ZeuZ Node directory: %v\n", err)
		os.Exit(1)
	}

	// Update PATH before checking if UV is installed
	if err := updatePath(); err != nil {
		fmt.Printf("Error updating path: %v\n", err)
	}

	// Install UV if needed
	if err := installUV(); err != nil {
		fmt.Printf("Error installing UV: %v\n", err)
		os.Exit(1)
	}

	// Update PATH to ensure UV is available after installation
	if err := updatePath(); err != nil {
		fmt.Printf("Error updating path: %v\n", err)
	}

	// Get remaining command line arguments after flag parsing
	args := flag.Args()

	// Run UV commands with arguments
	if err := runUVCommands(args); err != nil {
		fmt.Printf("Error running UV commands: %v\n", err)
		os.Exit(1)
	}
}
