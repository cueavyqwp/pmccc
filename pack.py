"""
测试并构建
"""

import subprocess
import shutil
import json
import sys
import os

import toml

# 优先找src文件夹下的模块
sys.path.insert(0, "src")

# 更新 pyproject.toml
with open("pyproject.json", "r", encoding="utf-8") as file:
    data = json.load(file)
data["project"]["version"] = __import__(data["project"]["name"]).__version__
with open("pyproject.toml", "w", encoding="utf-8") as file:
    toml.dump(data, file)

if os.path.exists("dist"):
    shutil.rmtree("dist")
subprocess.check_call((sys.executable, "-m", "build", "-w"))
