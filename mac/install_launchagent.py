#!/usr/bin/env python3
"""Explicit, optional local installation. Does not change system-wide settings."""
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

if sys.platform!='darwin':
    raise SystemExit('请在你的 Mac 上运行本脚本。')
root=Path(__file__).resolve().parents[1]
if any(x in str(root) for x in ['/Downloads/','/Desktop/','/Documents/']):
    raise SystemExit('请先将整个文件夹移到 ~/Applications/ForumRadar，再安装后台任务，以避免受保护目录权限问题。')
dest=Path.home()/'Library/LaunchAgents/com.lanyx.forum-radar.plist'
dest.parent.mkdir(parents=True,exist_ok=True)
logs=Path.home()/'Library/Logs/ForumRadar'; logs.mkdir(parents=True,exist_ok=True)
if dest.exists():
    raise SystemExit('已存在后台配置，未覆盖。需要升级时先按 README 卸载。')
payload={'Label':'com.lanyx.forum-radar','ProgramArguments':[str(Path(sys.executable).resolve()),str(root/'radar.py')],
 'WorkingDirectory':str(root),'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':30,
 'StandardOutPath':str(logs/'stdout.log'),'StandardErrorPath':str(logs/'stderr.log')}
with dest.open('wb') as f: plistlib.dump(payload,f)
os.chmod(dest,0o600)
try:
    subprocess.run(['launchctl','bootstrap',f'gui/{os.getuid()}',str(dest)],check=True)
except subprocess.CalledProcessError:
    raise SystemExit('配置已写入但加载失败。先停止前台实例，并按 README 检查；未报告安装成功。')
print('后台任务已加载。仅在你的用户登录会话中运行；请在 http://127.0.0.1:8765 检查。')
