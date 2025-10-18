"""
test and build
"""

import subprocess
import shutil
import json
import sys
import os

import toml

# update pyproject.toml
with open("pyproject.json", "r", encoding="utf-8") as file:
    data = json.load(file)
data["project"]["version"] = __import__(data["project"]["name"]).__version__
with open("pyproject.toml", "w", encoding="utf-8") as file:
    toml.dump(data, file)

if os.path.exists("dist"):
    shutil.rmtree("dist")
subprocess.check_call((sys.executable, "-m", "build", "-w"))
