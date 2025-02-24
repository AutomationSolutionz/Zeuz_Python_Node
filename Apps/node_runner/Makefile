.PHONY: all clean windows mac linux

# Output directory
BUILD_DIR=build

# Version info
VERSION=1.0.0
APPNAME=ZeuZ_Node

windows:
	GOOS=windows GOARCH=amd64 go build -o '$(BUILD_DIR)/$(APPNAME).exe' main.go
	GOOS=windows GOARCH=arm64 go build -o '$(BUILD_DIR)/$(APPNAME)_arm64.exe' main.go

mac:
	GOOS=darwin GOARCH=arm64 go build -o '$(BUILD_DIR)/$(APPNAME)_macos' main.go
	GOOS=darwin GOARCH=amd64 go build -o '$(BUILD_DIR)/$(APPNAME)_macos_amd64' main.go

linux:
	GOOS=linux GOARCH=amd64 go build -o '$(BUILD_DIR)/$(APPNAME)_linux' main.go
	GOOS=linux GOARCH=arm64 go build -o '$(BUILD_DIR)/$(APPNAME)_linux_arm64' main.go

all: windows linux mac

clean:
	rm -rf $(BUILD_DIR)

init:
	mkdir -p $(BUILD_DIR)
