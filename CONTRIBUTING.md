# 贡献指南

感谢您考虑为Daily Brief做出贡献！

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们作为贡献者和维护者承诺：无论年龄、体型、残疾、种族、性别特征、性别认同和表达、经验水平、教育程度、社会经济地位、国籍、外貌、种族、宗教或性认同和取向如何，参与我们的项目和社区的每个人都能获得无骚扰的体验。

### 我们的标准

有助于创建积极环境的行为包括：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 专注于对社区最有利的事情
- 对其他社区成员表现出同理心

## 如何贡献

### 报告Bug

在创建bug报告之前，请检查现有的issues以避免重复。创建bug报告时，请包含：

- 使用清晰描述性的标题
- 详细的重现步骤
- 预期行为和实际行为
- 屏幕截图（如果适用）
- Home Assistant版本、Python版本
- 相关的日志输出

**Bug报告模板**:

```markdown
**描述**
简要描述bug

**重现步骤**
1. 进入 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**预期行为**
应该发生什么

**实际行为**
实际发生了什么

**环境**
- Home Assistant版本: [例如 2024.10.0]
- Python版本: [例如 3.11]
- Daily Brief版本: [例如 0.1.0]

**日志**
```
粘贴相关日志
```

**截图**
如果适用，添加截图
```

### 功能请求

功能请求应该包含：

- 清晰的功能描述
- 为什么需要这个功能
- 可能的实现方式（可选）
- 相关的截图或模拟图（可选）

### 提交代码

#### 开发流程

1. **Fork仓库**
   ```bash
   git clone https://github.com/yourusername/ha-daily-brief
   cd ha-daily-brief
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/amazing-feature
   # 或
   git checkout -b fix/bug-description
   ```

3. **设置开发环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements_dev.txt
   pre-commit install
   ```

4. **编写代码**
   - 遵循现有代码风格
   - 添加类型提示
   - 编写文档字符串
   - 更新相关文档

5. **运行测试**
   ```bash
   # 运行所有测试
   pytest tests/

   # 运行代码质量检查
   black custom_components/daily_brief/
   isort custom_components/daily_brief/
   pylint custom_components/daily_brief/
   mypy custom_components/daily_brief/
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加了令人惊叹的功能"
   ```

   **提交消息规范**:
   - `feat:` 新功能
   - `fix:` Bug修复
   - `docs:` 文档更新
   - `style:` 代码格式（不影响代码运行）
   - `refactor:` 重构
   - `test:` 测试相关
   - `chore:` 构建过程或辅助工具的变动

7. **推送并创建PR**
   ```bash
   git push origin feature/amazing-feature
   ```
   然后在GitHub上创建Pull Request

#### Pull Request指南

- 填写PR模板
- 链接相关的issues
- 确保所有测试通过
- 更新文档（如果需要）
- 添加更新日志条目
- 等待代码审查

**PR检查清单**:

- [ ] 代码遵循项目风格指南
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 添加了changelog条目
- [ ] Commit消息清晰描述性强

## 代码风格

### Python代码规范

- 使用 **Black** 格式化代码
- 使用 **isort** 排序导入
- 使用 **pylint** 进行代码检查
- 使用 **mypy** 进行类型检查
- 遵循 **PEP 8** 标准
- 最大行长度: 100字符

### 文档规范

- 所有公共函数/类必须有文档字符串
- 使用Google风格的文档字符串
- 代码注释使用中文或英文（保持一致）
- README和文档使用Markdown格式

### 示例

```python
"""模块的文档字符串."""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class ExampleClass:
    """示例类的文档字符串.

    详细描述这个类的用途。

    Attributes:
        name: 名称属性
        value: 数值属性

    """

    def __init__(self, name: str, value: int) -> None:
        """初始化示例类.

        Args:
            name: 名称
            value: 数值

        """
        self.name = name
        self.value = value

    async def example_method(self, param: str) -> dict[str, Any]:
        """示例异步方法.

        Args:
            param: 参数说明

        Returns:
            返回值说明

        Raises:
            ValueError: 何时会抛出这个异常

        """
        if not param:
            raise ValueError("param不能为空")

        return {"result": param}
```

## 添加新功能

### 添加新的AI提供商

1. 在 `ai/providers/` 创建新文件（如 `anthropic.py`）
2. 继承 `LLMProvider` 或 `TTSProvider` 基类
3. 实现所有抽象方法
4. 添加到 `__init__.py`
5. 更新配置流程
6. 编写测试
7. 更新文档

### 添加新的内容包

1. 编辑 `feeds/content_packs.py`
2. 添加新的内容包定义
3. 测试RSS源是否有效
4. 更新README

## 测试

### 编写测试

- 所有新功能必须有测试
- 测试文件命名: `test_<module_name>.py`
- 使用pytest fixtures
- Mock外部API调用

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_aggregator.py

# 运行特定测试
pytest tests/test_aggregator.py::test_fetch_feed

# 带覆盖率报告
pytest --cov=custom_components/daily_brief tests/
```

## 发布流程

只有维护者可以发布新版本：

1. 更新版本号
   - `manifest.json`
   - `const.py`

2. 更新 `CHANGELOG.md`

3. 创建Git tag
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

4. GitHub Actions会自动创建release

## 获取帮助

如果您需要帮助：

- 查看 [文档](README.zh-CN.md)
- 搜索 [现有issues](https://github.com/yourusername/ha-daily-brief/issues)
- 创建新issue询问
- 加入讨论

## 致谢

感谢所有贡献者！

## 许可证

通过贡献，您同意您的贡献将在 Apache License 2.0 下授权。
