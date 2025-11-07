"""
配置类
"""

import typing
import json

from . import path as _path

__all__ = ["config_base"]


class config_base:
    """
    配置基类
    """

    def config_export(self) -> dict[str, typing.Any]:
        """
        导出为可被json序列化的字典

        **子类继承后最好覆写此方法**
        """
        ret: dict[str, typing.Any] = {}
        for name, obj in vars(self).items():
            # 以下划线开头/结尾的属性会被略过
            if not (name.startswith("_") or name.endswith("_")):
                # 尝试序列化
                try:
                    json.dumps([obj])
                except TypeError:
                    pass
                else:
                    ret[name] = obj
        return ret

    def config_loads(self, data: dict[str, typing.Any]) -> None:
        """
        从字典中加载配置
        """
        for name, value in data.items():
            setattr(self, name, value)

    def config_load(self, path: str) -> None:
        """
        从文件中加载配置
        """
        with open(path, "r", encoding="utf-8") as fp:
            self.config_loads(json.load(fp))

    def config_save(self, path: str) -> None:
        """
        保存配置文件
        """
        _path.check_dir(path, parent=True)
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(self.config_export(), fp, indent=4, ensure_ascii=False)
