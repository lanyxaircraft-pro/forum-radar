#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null; then
  echo "需要 Python 3.10 或以上版本。请从 python.org 安装后再启动。"
  read -r -p "按回车关闭" _radar_pause
  exit 1
fi
python3 -c 'import sys; assert sys.version_info >= (3,10), "需要 Python 3.10+"'
open "http://127.0.0.1:8765"
exec python3 radar.py
