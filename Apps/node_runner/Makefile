.PHONY: all clean windows mac linux checksums

# Output directory
BUILD_DIR=build

# Version info
VERSION?=dev
APPNAME=ZeuZ_Node
LDFLAGS=-X main.version=$(VERSION)

windows:
	x86_64-w64-mingw32-windres -o resource.syso resource.rc
	GOOS=windows GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME).exe' main.go
	GOOS=windows GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_arm64.exe' main.go
	rm -f resource.syso

mac:
	GOOS=darwin GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_macos' main.go
	GOOS=darwin GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_macos_amd64' main.go

linux:
	GOOS=linux GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_linux' main.go
	GOOS=linux GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_linux_arm64' main.go

checksums:
	cd $(BUILD_DIR) && sha256sum * > checksums.txt

all: windows linux mac checksums

clean:
	rm -rf $(BUILD_DIR)

init:
	mkdir -p $(BUILD_DIR)
