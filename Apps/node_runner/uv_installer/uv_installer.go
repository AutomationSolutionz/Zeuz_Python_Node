package uv_installer

import (
	"archive/zip"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

type GitHubRelease struct {
	TagName string `json:"tag_name"`
	Assets  []struct {
		Name               string `json:"name"`
		BrowserDownloadURL string `json:"browser_download_url"`
	} `json:"assets"`
}

// getLatestUVRelease fetches the latest uv release info from GitHub
func getLatestUVRelease() (*GitHubRelease, error) {
	resp, err := http.Get("https://api.github.com/repos/astral-sh/uv/releases/latest")
	if err != nil {
		return nil, fmt.Errorf("failed to fetch release info: %v", err)
	}
	defer resp.Body.Close()

	var release GitHubRelease
	if err := json.NewDecoder(resp.Body).Decode(&release); err != nil {
		return nil, fmt.Errorf("failed to parse release info: %v", err)
	}

	return &release, nil
}

// getUVArchitecture returns the appropriate uv architecture string
func getUVArchitecture() string {
	switch runtime.GOARCH {
	case "amd64":
		return "x86_64-pc-windows-msvc"
	case "386":
		return "i686-pc-windows-msvc"
	case "arm64":
		return "aarch64-pc-windows-msvc"
	default:
		return "x86_64-pc-windows-msvc"
	}
}

// downloadUV downloads the uv binary for the current platform
func downloadUV(release *GitHubRelease) (string, error) {
	arch := getUVArchitecture()
	assetName := fmt.Sprintf("uv-%s.zip", arch)

	var downloadURL string
	for _, asset := range release.Assets {
		if asset.Name == assetName {
			downloadURL = asset.BrowserDownloadURL
			break
		}
	}

	if downloadURL == "" {
		return "", fmt.Errorf("could not find asset for architecture: %s", arch)
	}

	tempDir, err := os.MkdirTemp("", "uv-download")
	if err != nil {
		return "", fmt.Errorf("failed to create temp directory: %v", err)
	}

	zipPath := filepath.Join(tempDir, "uv.zip")
	resp, err := http.Get(downloadURL)
	if err != nil {
		return "", fmt.Errorf("failed to download uv: %v", err)
	}
	defer resp.Body.Close()

	out, err := os.Create(zipPath)
	if err != nil {
		return "", fmt.Errorf("failed to create zip file: %v", err)
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to write zip file: %v", err)
	}

	return zipPath, nil
}

// extractUV extracts uv binaries from the zip file
func extractUV(zipPath, destDir string) error {
	reader, err := zip.OpenReader(zipPath)
	if err != nil {
		return fmt.Errorf("failed to open zip file: %v", err)
	}
	defer reader.Close()

	if err := os.MkdirAll(destDir, 0755); err != nil {
		return fmt.Errorf("failed to create destination directory: %v", err)
	}

	for _, file := range reader.File {
		if file.FileInfo().IsDir() {
			continue
		}

		// Only extract .exe files
		if !strings.HasSuffix(file.Name, ".exe") {
			continue
		}

		fileName := filepath.Base(file.Name)
		destPath := filepath.Join(destDir, fileName)

		rc, err := file.Open()
		if err != nil {
			return fmt.Errorf("failed to open file in zip: %v", err)
		}

		outFile, err := os.Create(destPath)
		if err != nil {
			rc.Close()
			return fmt.Errorf("failed to create output file: %v", err)
		}

		_, err = io.Copy(outFile, rc)
		rc.Close()
		outFile.Close()
		if err != nil {
			return fmt.Errorf("failed to copy file: %v", err)
		}
	}

	return nil
}

// getUVInstallDir returns the installation directory for uv
func getUVInstallDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("failed to get home directory: %v", err)
	}

	return filepath.Join(home, ".local", "bin"), nil
}

// InstallUVFromSource downloads and installs the latest uv release
func InstallUVFromSource() error {
	fmt.Println("Fetching latest uv release...")
	release, err := getLatestUVRelease()
	if err != nil {
		return err
	}

	fmt.Printf("Downloading uv %s...\n", release.TagName)
	zipPath, err := downloadUV(release)
	if err != nil {
		return err
	}
	defer os.RemoveAll(filepath.Dir(zipPath))

	installDir, err := getUVInstallDir()
	if err != nil {
		return err
	}

	fmt.Printf("Installing to %s...\n", installDir)
	if err := extractUV(zipPath, installDir); err != nil {
		return err
	}

	fmt.Printf("Successfully installed uv %s\n", release.TagName)
	return nil
}
