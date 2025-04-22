#!/bin/bash

# 仓库信息
OWNER="TC999"
REPO="CHJSL-archive"
TAG=$1  # 传入的 tag 参数

# 获取发行版信息
API_URL="https://api.github.com/repos/$OWNER/$REPO/releases/tags/$TAG"
ASSETS=$(curl -s $API_URL | grep "browser_download_url" | grep "\.mp4" | cut -d '"' -f 4)

# 下载 .mp4 文件
for URL in $ASSETS; do
  FILENAME=$(basename "$URL")
  echo "正在下载 $FILENAME..."
  curl -L "$URL" -o 1.mp4
done

echo "完成！"