# 更新日志

所有重要的更改都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [未发布]

## [0.1.0] - 2025-10-17

### 新增
- 🎉 首次发布！
- ✅ RSS/Atom订阅源聚合
- ✅ AI驱动的文章选择(多因素评分 + LLM)
- ✅ 自然语音脚本生成
- ✅ TTS音频生成和处理
- ✅ 媒体播放器集成
- ✅ 7个预配置内容包
  - 科技新闻(中文)
  - 科技新闻(英文)
  - 中文新闻
  - 世界新闻
  - 商业财经
  - 科学健康
  - 开发者新闻
- ✅ 7个Home Assistant服务
  - generate - 生成简报
  - play - 播放简报
  - stop - 停止播放
  - skip_story - 跳过故事
  - feedback - 提供反馈
  - add_source - 添加RSS源
  - regenerate - 重新生成
- ✅ 多语言支持(中文、英文)
- ✅ OpenAI集成(LLM + TTS)
- ✅ 配置流程UI(4步向导)
- ✅ SQLite本地存储
- ✅ 实时进度跟踪
- ✅ 音频后处理(音量标准化、暂停插入、音乐混合)
- ✅ 反馈系统

### 技术亮点
- 完整的流程编排器协调所有组件
- 提供商抽象层，易于扩展其他AI服务
- 异步架构，性能优良
- 完善的错误处理和日志
- 清晰的代码结构和文档

### 已知限制
- 首次生成可能需要3-5分钟
- 需要OpenAI API密钥(或其他LLM/TTS提供商)
- 需要系统安装FFmpeg用于音频处理

### 文档
- 完整的中英文README
- 开发者文档
- API文档
- 使用示例

[未发布]: https://github.com/Ryan-Guo123/ha-daily-brief/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ryan-Guo123/ha-daily-brief/releases/tag/v0.1.0
