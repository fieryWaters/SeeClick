#!/bin/bash

DATA_DIR=${1:-./data}
mkdir -p "$DATA_DIR/mobile" "$DATA_DIR/web"

# Download datasets (smallest first)
echo "Downloading Widget Captioning..."
wget https://box.nju.edu.cn/f/4019422e045b480f8945/?dl=1 -O "$DATA_DIR/mobile/widget_captioning.zip"

echo "Downloading RICOSCA..."
wget https://box.nju.edu.cn/f/1b54f3b4bf864775b78c/?dl=1 -O "$DATA_DIR/mobile/ricosca.zip"

echo "Downloading Screen Summarization..."
wget https://box.nju.edu.cn/f/6bcf4c17ec1b49d2806b/?dl=1 -O "$DATA_DIR/mobile/screen_summarization.zip"

echo "Downloading Web Annotations..."
wget https://box.nju.edu.cn/f/3b0f6ccb8bed476c8e39/?dl=1 -O "$DATA_DIR/web/annotations.zip"

echo "Downloading RICO Mobile Images..."
wget https://box.nju.edu.cn/f/7ae5e9bd4bf840d4add3/?dl=1 -O "$DATA_DIR/mobile/rico.zip"

echo "Downloading Web Screenshots (130GB)..."
wget https://box.nju.edu.cn/f/6a804cf190dd490a808f/?dl=1 -O "$DATA_DIR/web/screenshots.zip"

# Extract all
cd "$DATA_DIR/mobile" && unzip -q "*.zip" && cd - > /dev/null
cd "$DATA_DIR/web" && unzip -q "*.zip" && cd - > /dev/null