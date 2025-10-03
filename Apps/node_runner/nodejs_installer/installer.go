package nodejs_installer

import (
	"archive/tar"
	"archive/zip"
	"compress/gzip"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

const (
	nodeVersion = "20.18.0"
)

// getNodeURL returns the download URL for Node.js based on the OS and architecture
func getNodeURL() string {
	var osName, arch, ext string
	
	switch runtime.GOOS {
	case "darwin":
		osName = "darwin"
		ext = "tar.gz"
	case "linux":
		osName = "linux"
		ext = "tar.xz"
	case "windows":
		osName = "win"
		ext = "zip"
	}
	
	switch runtime.GOARCH {
	case "amd64":
		arch = "x64"
	case "arm64":
		arch = "arm64"
	}
	
	return fmt.Sprintf("https://nodejs.org/dist/v%s/node-v%s-%s-%s.%s", 
		nodeVersion, nodeVersion, osName, arch, ext)
}

// getNodeDir returns the local directory where Node.js will be installed
func getNodeDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".zeuz", "nodejs"), nil
}

// downloadFile downloads a file from URL to destination
func downloadFile(url, dest string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	out, err := os.Create(dest)
	if err != nil {
		return err
	}
	defer out.Close()
	
	_, err = io.Copy(out, resp.Body)
	return err
}

// safeJoin securely joins and validates that the resulting path is within the intended directory.
func safeJoin(destDir, filePath string) (string, error) {
	cleanDest, err := filepath.Abs(destDir)
	if err != nil {
		return "", err
	}
	destPath := filepath.Join(cleanDest, filePath)
	cleanPath, err := filepath.Abs(destPath)
	if err != nil {
		return "", err
	}
	// Ensure the cleaned path starts with the cleaned destination root path + separator
	if !strings.HasPrefix(cleanPath, cleanDest+string(os.PathSeparator)) && cleanPath != cleanDest {
		return "", fmt.Errorf("illegal file path: %s", filePath)
	}
	return cleanPath, nil
}

// extractZip extracts a zip file
func extractZip(src, dest string) error {
	r, err := zip.OpenReader(src)
	if err != nil {
		return err
	}
	defer r.Close()
	
	for _, f := range r.File {
		// Remove the root directory from path
		parts := strings.Split(f.Name, "/")
		if len(parts) <= 1 {
			continue
		}
		outputPath, err := safeJoin(dest, filepath.Join(parts[1:]...))
		if err != nil {
			// Skip files with unsafe paths
			continue
		}
		
		if f.FileInfo().IsDir() {
			os.MkdirAll(outputPath, 0755)
			continue
		}
		
		os.MkdirAll(filepath.Dir(outputPath), 0755)
		rc, err := f.Open()
		if err != nil {
			return err
		}
		
		outFile, err := os.Create(outputPath)
		if err != nil {
			rc.Close()
			return err
		}
		
		io.Copy(outFile, rc)
		outFile.Close()
		rc.Close()
	}
	return nil
}

// extractTarGz extracts a tar.gz file
func extractTarGz(src, dest string) error {
	file, err := os.Open(src)
	if err != nil {
		return err
	}
	defer file.Close()
	
	gzr, err := gzip.NewReader(file)
	if err != nil {
		return err
	}
	defer gzr.Close()
	
	tr := tar.NewReader(gzr)
	
	for {
		header, err := tr.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}
		
		// Remove the root directory from path
		parts := strings.Split(header.Name, "/")
		if len(parts) <= 1 {
			continue
		}
		unsafePath := filepath.Join(parts[1:]...)
		cleanPath := filepath.Clean(unsafePath)

		// Prevent Zip Slip: Don't allow '..' anywhere, nor absolute extraction
		if strings.Contains(cleanPath, "..") || filepath.IsAbs(cleanPath) {
			// Skip entries with directory traversal or absolute paths
			continue
		}

		// Build absolute extraction path
		path := filepath.Join(dest, cleanPath)
		absDest, err := filepath.Abs(dest)
		if err != nil {
			return err
		}
		absPath, err := filepath.Abs(path)
		if err != nil {
			return err
		}

		if !strings.HasPrefix(absPath, absDest+string(os.PathSeparator)) && absPath != absDest {
			// Extraction path is outside of destination: skip entry
			continue
		}

		switch header.Typeflag {
		case tar.TypeDir:
			os.MkdirAll(absPath, 0755)
		case tar.TypeReg:
			os.MkdirAll(filepath.Dir(absPath), 0755)
			outFile, err := os.Create(absPath)
			if err != nil {
				return err
			}
			io.Copy(outFile, tr)
			outFile.Close()
			os.Chmod(absPath, os.FileMode(header.Mode))
		}
	}
	return nil
}

// InstallNodeJS downloads and installs Node.js locally
func InstallNodeJS() error {
	nodeDir, err := getNodeDir()
	if err != nil {
		return err
	}
	
	// Check if Node.js is already installed
	nodeBin := filepath.Join(nodeDir, "bin", "node")
	if runtime.GOOS == "windows" {
		nodeBin = filepath.Join(nodeDir, "node.exe")
	}
	
	if _, err := os.Stat(nodeBin); err == nil {
		fmt.Println("Node.js already installed")
		return nil
	}
	
	fmt.Printf("Installing Node.js v%s...\n", nodeVersion)
	
	// Create installation directory
	if err := os.MkdirAll(nodeDir, 0755); err != nil {
		return err
	}
	
	// Download Node.js
	url := getNodeURL()
	var tempFile string
	if runtime.GOOS == "windows" {
		tempFile = filepath.Join(os.TempDir(), "nodejs.zip")
	} else {
		tempFile = filepath.Join(os.TempDir(), "nodejs.tar.gz")
	}
	
	fmt.Println("Downloading Node.js...")
	if err := downloadFile(url, tempFile); err != nil {
		return err
	}
	defer os.Remove(tempFile)
	
	// Extract Node.js
	fmt.Println("Extracting Node.js...")
	if runtime.GOOS == "windows" {
		if err := extractZip(tempFile, nodeDir); err != nil {
			return err
		}
	} else {
		if err := extractTarGz(tempFile, nodeDir); err != nil {
			return err
		}
	}
	
	fmt.Println("Node.js installation completed")
	return nil
}

// GetNodePath returns the path to the Node.js binary
func GetNodePath() (string, error) {
	nodeDir, err := getNodeDir()
	if err != nil {
		return "", err
	}
	
	nodeBin := filepath.Join(nodeDir, "bin", "node")
	if runtime.GOOS == "windows" {
		nodeBin = filepath.Join(nodeDir, "node.exe")
	}
	
	return nodeBin, nil
}

// GetNpmPath returns the path to the npm binary
func GetNpmPath() (string, error) {
	nodeDir, err := getNodeDir()
	if err != nil {
		return "", err
	}
	
	npmBin := filepath.Join(nodeDir, "bin", "npm")
	if runtime.GOOS == "windows" {
		npmBin = filepath.Join(nodeDir, "npm.cmd")
	}
	
	return npmBin, nil
}

// InstallAppium installs Appium and required drivers using the local Node.js
func InstallAppium() error {
	npmPath, err := GetNpmPath()
	if err != nil {
		return err
	}
	
	fmt.Println("Installing Appium...")
	cmd := exec.Command(npmPath, "install", "-g", "appium")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to install Appium: %v", err)
	}
	
	fmt.Println("Installing Appium drivers...")
	
	// Install UiAutomator2 driver
	cmd = exec.Command(npmPath, "install", "-g", "appium-uiautomator2-driver")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to install UiAutomator2 driver: %v", err)
	}
	
	// Install XCUITest driver
	cmd = exec.Command(npmPath, "install", "-g", "appium-xcuitest-driver")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to install XCUITest driver: %v", err)
	}
	
	fmt.Println("Appium installation completed")
	return nil
}
