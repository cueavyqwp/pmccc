<div align = "center" >
    <h1>pmccc</h1>
    <a href = "https://pypi.org/project/pmccc" >
        <img alt = "PyPI version" src = "https://img.shields.io/pypi/v/pmccc?color=blue" >
    </a>
    <a href = "https://www.python.org" >
        <img alt = "Python version" src = "https://img.shields.io/badge/python-3.10+-blue" >
    </a>
    <a href = "https://opensource.org/license/mit" >
        <img alt = "license" src = "https://img.shields.io/badge/license-MIT-blue" >
    </a>
</div>

# 关于

这是一个基于`python`的`Minecraft`启动器库

# 示例

```python
import pmccc

# launcher启动器类
launcher = pmccc.client.launcher.launcher()
# 通过环境变量寻找Java
launcher.search_java()
# .minecraft版本文件夹
minecraft = pmccc.client.minecraft.minecraft_manager("你自己的游戏目录/.minecraft")
# 添加一个离线玩家
player = launcher.player.add_player("offline", "Test")
# 创建并启动进程
# 由于subprocess库,若不指定log4j2类,则默认不输出日志
popen = launcher.launch(minecraft, "版本名",
                        player, log4j2=pmccc.process.log4j2())
# 等待进程结束
popen.wait()
```
