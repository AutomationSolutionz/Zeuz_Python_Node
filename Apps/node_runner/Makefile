.PHONY: all clean windows mac linux checksums init

# Output directory
BUILD_DIR?=build

# Version info
VERSION?=dev
APPNAME=ZeuZ_Node
LDFLAGS=-X main.version=$(VERSION)
# Windows resource compiler; override when using a different toolchain.
WINDRES?=x86_64-w64-mingw32-windres

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

windows: | $(BUILD_DIR)
	@if command -v $(WINDRES) >/dev/null 2>&1; then \
		$(WINDRES) -o resource.syso resource.rc; \
	else \
		echo "warning: $(WINDRES) not found; building without custom resources" >&2; \
	fi
	GOOS=windows GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME).exe' main.go
	GOOS=windows GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_arm64.exe' main.go
	@if [ -f resource.syso ]; then rm -f resource.syso; fi

mac: | $(BUILD_DIR)
	GOOS=darwin GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_macos' main.go
	GOOS=darwin GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_macos_amd64' main.go

linux: | $(BUILD_DIR)
	GOOS=linux GOARCH=amd64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_linux' main.go
	GOOS=linux GOARCH=arm64 go build -ldflags "$(LDFLAGS)" -o '$(BUILD_DIR)/$(APPNAME)_linux_arm64' main.go

checksums: | $(BUILD_DIR)
	cd $(BUILD_DIR) && sha256sum * > checksums.txt

all: windows linux mac checksums

clean:
	rm -rf $(BUILD_DIR)

init: $(BUILD_DIR)
