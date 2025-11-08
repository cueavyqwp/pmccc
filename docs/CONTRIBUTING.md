# 为pmccc做出贡献

## 常见贡献

- 功能建议: 你可以在这里参与[讨论](https://github.com/cueavyqwp/pmccc/discussions)
- BUG反馈: 你可以在[议题](https://github.com/cueavyqwp/pmccc/issues)反馈BUG
- 文档: 你可以通过创建[拉取请求](https://github.com/cueavyqwp/pmccc/pulls)来提交或更新文档
- 代码: 你可以通过创建[拉取请求](https://github.com/cueavyqwp/pmccc/pulls)来提交代码

### BUG反馈

在开启新议题前请先确认没有重复的议题

附带上

- 基本的系统信息

- python/pmccc版本

- 详细报错日志

### 代码

- 使用`black`来代码格式化

- 开启`pylance`语法检查器的`strict`模式

- 标明类型注释

- 尽可能少的使用`# pyright: ignore`

- 代码保持低耦合性

- 仅在必要时写注释

- 每个文件开头写文档字符串,简单说明其作用

- 使用`__all__`指定要导出的内容

#### `import`顺序

1. `python`自带库
2. 本地模块
3. 第三方库

#### 命名原则

- 使用蛇形命名法
- 常量使用全大写

# Contributing to pmccc

## Common Ways to Contribute

- **Feature Suggestions**: You can participate in [Discussions](https://github.com/cueavyqwp/pmccc/discussions)
- **Bug Reports**: You can report bugs in [Issues](https://github.com/cueavyqwp/pmccc/issues)
- **Documentation**: You can submit or update documentation via [Pull Requests](https://github.com/cueavyqwp/pmccc/pulls)
- **Code**: You can submit code via [Pull Requests](https://github.com/cueavyqwp/pmccc/pulls)

### Bug Reports

Before opening a new issue, please make sure no duplicate issue exists.

Please include:

- Basic system information
- Python / pmccc version
- Detailed error logs

### Code

- Use `black` to format code
- Enable `strict` mode in the `pylance` language server
- Include type annotations
- Minimize usage of `# pyright: ignore`
- Keep code loosely coupled
- Add comments only when necessary
- Include a docstring at the top of each file to briefly describe its purpose
- Use `__all__` to specify exported content

#### Import Order

1. Python standard libraries
2. Local modules
3. Third-party libraries

#### Naming Conventions

- Use **snake_case** for variables and functions
- Use **ALL_CAPS** for constants
