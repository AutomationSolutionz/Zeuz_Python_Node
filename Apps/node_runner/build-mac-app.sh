#!/bin/sh

ASSETS_DIR='./macos/assets'
make mac
mkdir $ASSETS_DIR
cp ./macos/run.command $ASSETS_DIR
cp ./build/ZeuZ_Node_macos $ASSETS_DIR
cp ./zeuz-logo.png $ASSETS_DIR
cd macos
go run macapp.go -assets ./assets -bin run.command -icon ./assets/zeuz-logo.png -identifier ai.zeuz.node -name "ZeuZ Node" -o ../build
cd ../
rm -rf $ASSETS_DIR
