# Daily Brief for Home Assistant

一个由AI驱动的Home Assistant自定义集成，可以从RSS源生成个性化的每日新闻简报。

## 特性

- 🤖 **AI智能选择** - 使用GPT-4o-mini等大语言模型智能筛选重要新闻
- 🎙️ **自然语音** - 使用OpenAI TTS、ElevenLabs等高质量语音合成
- 📚 **丰富内容源** - 7个预配置内容包，支持中英文新闻
- 🎯 **个性化** - 根据您的兴趣和反馈持续优化
- 🔒 **隐私优先** - 所有数据本地存储
- 🌍 **多语言** - 支持中文、英文等多种语言

## 安装后配置

1. 进入 **设置** → **设备与服务** → **添加集成**
2. 搜索 "Daily Brief"
3. 按照4步向导完成配置:
   - **步骤1**: 配置LLM提供商(OpenAI/Anthropic/Google/Ollama)
   - **步骤2**: 配置TTS提供商(OpenAI/ElevenLabs/Piper)
   - **步骤3**: 选择内容包(科技/新闻/商业等)
   - **步骤4**: 设置兴趣和偏好

## 快速开始

### 手动生成简报

```yaml
service: daily_brief.generate
data:
  briefing_type: morning
  article_count: 10
```

### 播放简报

```yaml
service: daily_brief.play
data:
  media_player: media_player.bedroom_speaker
```

### 自动化示例

```yaml
automation:
  - alias: "每日新闻简报"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: daily_brief.generate
      - wait_template: "{{ states('sensor.daily_brief_status') == 'ready' }}"
        timeout: '00:05:00'
      - service: daily_brief.play
        data:
          media_player: media_player.kitchen_speaker
```

## 费用估算

### 经济配置
- GPT-4o-mini + OpenAI TTS
- 约 ¥1.19/简报 或 ¥35.70/月

### 高级配置
- GPT-4o + ElevenLabs
- 约 ¥3.15/简报 或 ¥94.50/月

### 免费配置
- Ollama(本地) + Piper(本地)
- 完全免费！

## 需要帮助？

- 📖 [完整文档](https://github.com/Ryan-Guo123/ha-daily-brief)
- 💬 [问题反馈](https://github.com/Ryan-Guo123/ha-daily-brief/issues)
- 🌟 [给项目加星](https://github.com/Ryan-Guo123/ha-daily-brief)

## 截图

_即将添加..._
