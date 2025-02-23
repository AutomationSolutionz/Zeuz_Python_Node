package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

// downloadFile downloads a file from URL to a local path
func downloadFile(url, destPath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to download file: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("bad status: %s", resp.Status)
	}

	out, err := os.CreateTemp("", "uv-install-*")
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

	// Make the file executable on Unix systems
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

// installUV installs the UV package manager if not already installed
func installUV() error {
	// Check if uv is already installed
	_, err := exec.LookPath("uv")
	if err == nil {
		fmt.Println("UV already installed")
		return nil
	}

	fmt.Println("Installing UV...")

	// Create temporary directory for installation files
	tempDir, err := os.MkdirTemp("", "uv-install")
	if err != nil {
		return fmt.Errorf("failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tempDir)

	var (
		scriptURL  string
		scriptPath string
		cmd        *exec.Cmd
	)

	if runtime.GOOS == "windows" {
		scriptURL = "https://astral.sh/uv/install.ps1"
		scriptPath = filepath.Join(tempDir, "install.ps1")

		if err := downloadFile(scriptURL, scriptPath); err != nil {
			return err
		}

		cmd = exec.Command("powershell", "-ExecutionPolicy", "ByPass", "-File", scriptPath)
	} else {
		scriptURL = "https://astral.sh/uv/install.sh"
		scriptPath = filepath.Join(tempDir, "install.sh")

		if err := downloadFile(scriptURL, scriptPath); err != nil {
			return err
		}

		cmd = exec.Command("sh", scriptPath)
	}

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

// getEnvPaths returns the appropriate paths for the virtual environment based on OS
func getEnvPaths() (string, string) {
	if runtime.GOOS == "windows" {
		return ".venv\\Scripts\\activate.bat", ".venv\\Scripts\\python.exe"
	}
	return ".venv/bin/activate", ".venv/bin/python"
}

// setupVirtualEnv creates and activates a Python virtual environment
func setupVirtualEnv() error {
	// Check if venv exists
	if _, err := os.Stat(".venv"); os.IsNotExist(err) {
		fmt.Println("Creating virtual environment...")
		cmd := exec.Command("python", "-m", "venv", ".venv")
		if runtime.GOOS != "windows" {
			cmd = exec.Command("python3", "-m", "venv", ".venv")
		}
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			return fmt.Errorf("failed to create virtual environment: %v", err)
		}
	}
	return nil
}

// updatePath adds UV binary location to PATH
func updatePath() error {
	home, err := os.UserHomeDir()
	if err != nil {
		return fmt.Errorf("failed to get home directory: %v", err)
	}

	var uvPath string
	if runtime.GOOS == "windows" {
		uvPath = filepath.Join(home, ".uv", "bin")
	} else {
		uvPath = filepath.Join(home, ".local", "bin")
	}

	currentPath := os.Getenv("PATH")
	if !strings.Contains(currentPath, uvPath) {
		newPath := fmt.Sprintf("%s%s%s", uvPath, string(os.PathListSeparator), currentPath)
		os.Setenv("PATH", newPath)
	}
	return nil
}

// runUVCommands executes UV sync and run commands
func runUVCommands() error {
	// Update PATH to ensure UV is available
	if err := updatePath(); err != nil {
		return err
	}

	// Run UV sync
	fmt.Println("Running uv sync...")
	syncCmd := exec.Command("uv", "sync")
	syncCmd.Stdout = os.Stdout
	syncCmd.Stderr = os.Stderr
	if err := syncCmd.Run(); err != nil {
		return fmt.Errorf("failed to run uv sync: %v", err)
	}

	// Run node_cli.py
	fmt.Println("Running node_cli.py...")
	runCmd := exec.Command("uv", "run", "node_cli.py")
	runCmd.Stdout = os.Stdout
	runCmd.Stderr = os.Stderr
	return runCmd.Run()
}

func main() {
	// Install UV if needed
	if err := installUV(); err != nil {
		fmt.Printf("Error installing UV: %v\n", err)
		os.Exit(1)
	}

	// Setup virtual environment
	// if err := setupVirtualEnv(); err != nil {
	// 	fmt.Printf("Error setting up virtual environment: %v\n", err)
	// 	os.Exit(1)
	// }

	// Run UV commands
	if err := runUVCommands(); err != nil {
		fmt.Printf("Error running UV commands: %v\n", err)
		os.Exit(1)
	}
}
