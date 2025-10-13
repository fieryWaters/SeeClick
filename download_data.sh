#!/bin/bash

# Data directory - defaults to Perlmutter CFS if available, otherwise ./data
if [ -d /global/cfs/cdirs/m3930 ]; then
    DATA_DIR=${1:-/global/cfs/cdirs/m3930/$USER/SeeClick/data}
else
    DATA_DIR=${1:-./data}
fi
mkdir -p "$DATA_DIR/mobile" "$DATA_DIR/web"

# Download datasets (smallest first)
echo "Downloading Widget Captioning..."
wget --content-disposition https://box.nju.edu.cn/f/4019422e045b480f8945/?dl=1 -P "$DATA_DIR/mobile"

echo "Downloading RICOSCA..."
wget --content-disposition https://box.nju.edu.cn/f/1b54f3b4bf864775b78c/?dl=1 -P "$DATA_DIR/mobile"

echo "Downloading Screen Summarization..."
wget --content-disposition https://box.nju.edu.cn/f/6bcf4c17ec1b49d2806b/?dl=1 -P "$DATA_DIR/mobile"

echo "Downloading Web Annotations..."
wget --content-disposition https://box.nju.edu.cn/f/3b0f6ccb8bed476c8e39/?dl=1 -P "$DATA_DIR/web"

echo "Downloading RICO Mobile Images..."
wget --content-disposition https://box.nju.edu.cn/f/7ae5e9bd4bf840d4add3/?dl=1 -P "$DATA_DIR/mobile"

echo "Downloading Web Screenshots (130GB)..."
wget --content-disposition https://box.nju.edu.cn/f/6a804cf190dd490a808f/?dl=1 -P "$DATA_DIR/web"

# Extract zip files only
cd "$DATA_DIR/mobile" && for f in *.zip; do [ -f "$f" ] && unzip -q "$f"; done && cd - > /dev/null
cd "$DATA_DIR/web" && for f in *.zip; do [ -f "$f" ] && unzip -q "$f"; done && cd - > /dev/null