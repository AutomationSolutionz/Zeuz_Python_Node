.PHONY: all clean windows mac linux checksums

# Output directory
BUILD_DIR=build

# Version info
VERSION?=dev
APPNAME=ZeuZ_Node
LDFLAGS=-X main.version=$(VERSION)

windows:
	x86_64-w64-mingw32-windres -o resource.syso resource.rc
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME).exe' main.go
	CGO_ENABLED=0 GOOS=windows GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_arm64.exe' main.go
	rm -f resource.syso

mac:
	CGO_ENABLED=0 GOOS=darwin GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_macos' main.go
	CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_macos_amd64' main.go

linux:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_linux' main.go
	CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_linux_arm64' main.go

checksums:
	cd $(BUILD_DIR) && sha256sum * > checksums.txt

all: windows linux mac checksums

clean:
	rm -rf $(BUILD_DIR)

init:
	mkdir -p $(BUILD_DIR)
