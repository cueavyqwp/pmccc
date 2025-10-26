<div align = "center" >
    <h1>pmccc</h1>
</div>

# 关于

这是一个基于`python`的`Minecraft`启动器核心

# 示例

## 启动器信息

```python
import pmccc

launcher_info = pmccc.launcher_info("启动器名称", "启动器版本")
```

## 玩家信息

```python
import pmccc

# 离线登录(可自定义UUID)
player = pmccc.player.player_base()
player.name = "名称"
player.uuid = "UUID"

print(player)

# 离线登录
player = pmccc.player.player_offline("名称")

print(player)

# 微软登录
player = pmccc.player_online()

url = input(f"请访问地址: {player.login_url()}\n把跳转后的链接粘贴过来\n>")
# microsoft_refresh_token 若90天不使用就会过期,一定不能泄露
microsoft_refresh_token = player.login_auto_init(url)

print(player)

# 以后改用 login_auto 登录即可
player.login_auto(microsoft_refresh_token)

# 可使用 get_profile 获取玩家档案
print(player.get_profile(player.access_token))
```

# 获取Java

```python
import pmccc

java_manager = pmccc.java_manager()
# 会通过环境变量寻找可用Java
java_manager.search()

print(java_manager)

```

# 版本文件

```python
import pmccc
import json

with open("xxx.json", encoding="utf-8") as fp:
    version = pmccc.version(json.load(fp))

# 游戏jvm与游戏参数
jvm, game = version.get_args()

# 获取库(注意这里返回的是相对路径,绝对路径需要你自行拼接)
library = version.get_library()
native = version.get_native()

# 获取classpath
class_path = version.merge_cp(library, "游戏jar文件路径")

# 获取启动参数
args = version.replace_args(
    launcher_info,
    java_manager,  # 这里会自动选择合适Java版本
    version.merge_args(jvm, game),
    class_path,
    player,
    "游戏目录(版本文件夹)",
    "asset目录",
    "natives目录"
)
```

# 解压native

```python
import pmccc

# 清理目录
pmccc.native.clear("natives目录")

# 注意刚刚说的,这里native默认是相对路径,记得自行拼接
pmccc.native.unzip_all(native)
```

# 启动游戏

```python
import subprocess

subprocess.run(args, cwd="游戏目录")
```
