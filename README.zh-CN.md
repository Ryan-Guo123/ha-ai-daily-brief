# Daily Brief for Home Assistant

一个由AI驱动的Home Assistant自定义集成，可以从RSS源生成个性化的每日新闻简报，并通过Home Assistant媒体播放器播放。

## ✨ 特性

- **AI智能选择**: 使用大语言模型(GPT-4o-mini, Claude等)智能选择最重要和最相关的新闻
- **自然语音生成**: 使用高级TTS服务(ElevenLabs、OpenAI TTS或免费的本地Piper)生成自然语音
- **个性化学习**: 根据您的反馈学习并改进新闻选择
- **多语言支持**: 支持中文、英文等多种语言
- **内容包**: 预配置的新闻源合集(科技、新闻、商业、科学等)
- **隐私优先**: 所有数据本地存储在Home Assistant中
- **灵活播放**: 支持定时自动播放、手动触发、语音命令或移动通知

## 📋 要求

- Home Assistant 2024.10.0或更高版本
- Python 3.11或更高版本
- OpenAI API密钥(或其他LLM/TTS提供商)
- FFmpeg(用于音频处理)

## 🚀 安装

### 通过HACS安装(推荐)

1. 在Home Assistant中打开HACS
2. 进入"集成"
3. 点击右上角三点菜单 → "自定义仓库"
4. 添加仓库URL: `https://github.com/yourusername/ha-daily-brief`
5. 类别选择: "Integration"
6. 点击"添加"
7. 搜索"Daily Brief"
8. 点击"下载"
9. 重启Home Assistant

### 手动安装

1. 下载最新发布版本
2. 解压到`config/custom_components/daily_brief/`
3. 重启Home Assistant

## ⚙️ 配置

1. 进入 设置 → 设备与服务
2. 点击"+ 添加集成"
3. 搜索"Daily Brief"
4. 按照设置向导操作:
   - 选择内容包(科技、新闻、商业等)
   - 设置您的兴趣和偏好
   - 配置AI提供商(OpenAI、Anthropic等)
   - 设置TTS提供商(OpenAI、ElevenLabs、Piper)
   - 配置定时和自动播放

## 📖 使用方法

### 自动每日简报

配置完成后，您的简报将在每天早上自动生成，并可以选择在指定时间自动播放。

### 手动生成

```yaml
# 按需生成简报
service: daily_brief.generate
data:
  briefing_type: on_demand
  article_count: 10
```

### 播放简报

```yaml
# 播放最新简报
service: daily_brief.play
data:
  media_player: media_player.bedroom_speaker
```

### 自动化示例

```yaml
automation:
  - alias: "早间新闻简报"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: daily_brief.generate
        data:
          briefing_type: morning
      - delay: '00:05:00'  # 等待生成完成
      - service: daily_brief.play
        data:
          media_player: media_player.kitchen_speaker
```

## 💰 费用估算

### 经济配置
- LLM: GPT-4o-mini (~¥0.14/简报)
- TTS: OpenAI TTS (~¥1.05/简报)
- **总计: ~¥1.19/简报** 或 **~¥35.70/月**(30个简报)

### 高级配置
- LLM: GPT-4o (~¥1.05/简报)
- TTS: ElevenLabs (~¥2.10/简报)
- **总计: ~¥3.15/简报** 或 **~¥94.50/月**(30个简报)

### 免费配置
- LLM: Ollama(本地，免费)
- TTS: Piper(本地，免费)
- **总计: ¥0**(仅需电费)

## 📊 可用服务

- `daily_brief.generate` - 生成新简报
- `daily_brief.play` - 播放简报
- `daily_brief.stop` - 停止播放
- `daily_brief.feedback` - 提供反馈(喜欢/不喜欢)
- `daily_brief.add_source` - 添加自定义RSS源
- `daily_brief.regenerate` - 重新生成脚本/音频

## 🎯 内容包

预配置的内容合集:

- **科技新闻(中文)**: 36氪、少数派、爱范儿、V2EX
- **科技新闻(英文)**: Hacker News、TechCrunch、The Verge、Ars Technica、Wired
- **中文新闻**: 知乎热榜、澎湃新闻
- **世界新闻**: BBC、路透社、半岛电视台、卫报
- **商业财经**: 华尔街日报、彭博社、金融时报
- **科学健康**: Nature、科学日报、新科学家
- **开发者新闻**: GitHub Trending、Dev.to、Lobsters

## 🛠️ 开发

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/yourusername/ha-daily-brief
cd ha-daily-brief

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows使用 venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements_dev.txt

# 设置pre-commit钩子
pre-commit install

# 运行测试
pytest tests/
```

### 项目结构

```
custom_components/daily_brief/
├── 核心模块(5个文件)
│   ├── __init__.py, const.py, coordinator.py
│   ├── config_flow.py, services.py
├── 存储层(4个文件)
│   ├── database.py, models.py, cache.py
├── 内容源(4个文件)
│   ├── parser.py, dedup.py, content_packs.py
├── 核心组件(5个文件)
│   ├── aggregator.py, selector.py, generator.py
│   ├── audio.py, player.py, orchestrator.py
├── AI层(6个文件)
│   ├── llm.py, tts.py, prompts.py
│   └── providers/openai.py
├── 实体(4个文件)
│   ├── sensor.py, binary_sensor.py, button.py, media_player.py
└── 翻译和配置(3个文件)
```

## 🤝 贡献

欢迎贡献！请阅读我们的[贡献指南](CONTRIBUTING.md)了解行为准则和提交PR的流程。

## 📝 许可证

本项目采用Apache License 2.0许可证 - 详见[LICENSE](LICENSE)文件。

## 🙏 致谢

- Home Assistant社区提供的优秀平台
- RSSHub提供RSS源聚合
- OpenAI、ElevenLabs提供AI服务
- 所有为本项目做出贡献的人

## 📞 支持

- **GitHub Issues**: https://github.com/yourusername/ha-daily-brief/issues
- **Home Assistant论坛**: [讨论主题]
- **Discord**: [服务器链接]

## 🗺️ 路线图

**v0.1.0(MVP)** - ✅ 核心功能
- RSS聚合、AI选择、基础TTS

**v0.2.0(Beta)** - 🚧 进行中
- 多TTS提供商、反馈系统、更多内容包

**v1.0.0(稳定版)** - 📅 计划中
- 本地LLM支持(Ollama)、移动应用集成、播客订阅

**未来版本**
- 社交媒体集成、语音克隆、对话模式、多用户配置文件

---

**用❤️为Home Assistant社区打造**
