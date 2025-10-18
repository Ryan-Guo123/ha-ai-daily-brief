# Home Assistant 每日简报 - 产品需求文档 (PRD)

**版本:** 1.0  
**日期:** 2025年10月13日  
**许可证:** Apache-2.0  
**状态:** 草案 - 待开发

---

## 📋 文档概述

**产品名称:** Home Assistant 每日简报  
**标语:** "您的 AI 个人新闻助理"  
**愿景:** 每天清晨，您的智能家居只告诉您最重要的事。

---

## 1. 执行摘要

### 1.1 我们在构建什么

一个能自动执行以下操作的 Home Assistant 自定义集成：

1.  聚合来自 RSS 订阅、新闻 API 和社交媒体的内容
2.  使用 AI 筛选并挑选 5-15 条最重要的新闻
3.  生成一段自然流畅的音频简报（5-30分钟）
4.  通过智能音箱、手机或任何媒体播放器进行播放
5.  通过用户反馈不断学习和改进

### 1.2 为何重要

**问题:**

-   信息过载：每天 100 多篇文章，95% 是噪音
-   现有解决方案不够智能：Alexa/Google 要么全读，要么不读
-   缺乏个性化：千篇一律的新闻简报
-   耗费精力：用户浪费 2 小时在无尽的滚动浏览上

**解决方案:**

-   AI 从噪音中筛选出信号
-   每日自动生成
-   根据用户兴趣进行个性化
-   零手动操作
-   与现有智能家居无缝集成

### 1.3 成功指标 (6个月)

-   **采用率:** 通过 HACS 安装量超过 1,000 次
-   **参与度:** 用户收听所生成简报的 80% 以上
-   **满意度:** NPS > 50，GitHub 星标 > 4.5
-   **社区:** 超过 10 位社区贡献者
-   **成本:** 每用户每月的 API 成本低于 0.50 美元

---

## 2. 用户画像

### 主要用户画像: "精通技术的专业人士"

-   **姓名:** Alex Chen
-   **年龄:** 28-45
-   **职业:** 产品经理 / 软件工程师 / 创业者
-   **HA 经验:** 中级 (拥有 10+ 集成，理解基本自动化)
-   **场景:** 每天通勤 30 分钟，希望在不进行“末日滚动”的情况下了解最新信息
-   **痛点:**
    -   订阅过多 (新闻通讯、播客、RSS)
    -   担心错过重要新闻 (FOMO)
    -   讨厌阅读“标题党”文章
-   **目标:**
    -   在 15 分钟内了解最新动态
    -   专注于深度工作，不受干扰
    -   只从高质量来源获取信息

### 次要用户画像: "智能家居爱好者"

-   **姓名:** Maria Rodriguez
-   **年龄:** 35-55
-   **职业:** 以技术为爱好的专业人士
-   **HA 经验:** 高级 (自托管，会编写 YAML)
-   **场景:** 晨间例行自动化 (起床 → 新闻 → 天气 → 咖啡)
-   **痛点:**
    -   现有的 HA 新闻集成功能非常基础
    -   希望拥有高度定制化和控制权
    -   不喜欢依赖云服务
-   **目标:**
    -   集成到现有的自动化流程中
    -   完全控制内容来源
    -   隐私优先

---

## 3. 核心功能 (MVP)

### 3.1 内容聚合

#### 3.1.1 支持的来源

**第一梯队: RSS/Atom 订阅** (主要)

-   RSSHub 集成 (5000+ 路由)
-   直接的 RSS URL (用户提供)
-   内置订阅源发现功能

**第二梯队: 新闻 API** (可选)

-   NewsAPI.org
-   美联社 API
-   自定义 API 端点

**第三梯队: 社交媒体** (未来规划)

-   Twitter/X 热门话题
-   Reddit 热门帖子
-   Hacker News 首页

#### 3.1.2 预配置内容包

用户可以一键启用：

**科技 (英文)**

-   Hacker News
-   TechCrunch
-   The Verge
-   Ars Technica
-   MIT Technology Review

**科技 (中文)**

-   36氪
-   少数派
-   爱范儿
-   InfoQ中文
-   CSDN热榜

**世界新闻 (英文)**

-   BBC World
-   Reuters
-   Al Jazeera
-   The Guardian
-   Associated Press

**中文新闻**

-   知乎热榜
-   澎湃新闻
-   财新网
-   FT中文网

**商业与金融**

-   Wall Street Journal
-   Bloomberg
-   Financial Times
-   The Economist
-   彭博中文

**科学与健康**

-   Nature News
-   Science Daily
-   New Scientist
-   果壳网

**开发者新闻**

-   GitHub Trending
-   Dev.to
-   Lobsters
-   Reddit r/programming

**自定义**

-   用户添加自己的 RSS URL
-   导入 OPML 文件
-   与社区共享订阅列表

#### 3.1.3 内容处理管道

```
1. 获取 (每 30-60 分钟)
   ├─ 并行获取 (10个并发)
   ├─ 遵守速率限制
   ├─ 缓存 1 小时
   └─ 存储原始 HTML/JSON

2. 解析与提取
   ├─ 文章标题、摘要、内容
   ├─ 发布日期、来源
   ├─ 作者、标签、分类
   └─ 移除广告、样板代码

3. 去重
   ├─ 标题相似度 (>80%)
   ├─ 内容哈希匹配
   └─ 合并多来源报道

4. 语言检测
   ├─ 自动检测 (langdetect)
   ├─ 按语言分离
   └─ 支持多语言简报
```

---

### 3.2 AI 驱动的内容筛选

#### 3.2.1 评分算法

每篇文章根据以下标准获得一个分数 (0-100)：

**重要性 (40分)**

-   突发新闻检测 (+20)
-   来源权威性 (+10)
-   社交媒体热度 (+10)
-   通过 AI 预测影响力 (+0 到 +40)

**相关性 (30分)**

-   用户兴趣匹配 (+15)
-   关键词对齐 (+10)
-   主题分类契合度 (+5)

**新鲜度 (20分)**

-   发布于 <2 小时前 (+20)
-   发布于 <12 小时前 (+15)
-   发布于 <24 小时前 (+10)
-   更早 → 分数衰减

**质量 (10分)**

-   内容长度 (理想为 500-3000 词)
-   可读性分数
-   无“标题党”模式
-   原创报道加分

#### 3.2.2 AI 筛选流程

**第 1 步: 初步过滤**

```
- 移除重复项
- 按分数 >50 筛选
- 保留前 50 名候选文章
```

**第 2 步: AI 排序** (使用 LLM)

```
Prompt:
"你是一名新闻编辑。从这 50 篇文章中，
为一位对以下领域感兴趣的专业人士挑选 10 篇最重要的文章：
{user_interests}。

请考虑：
- 对用户领域的影响
- 新闻价值
- 信息的独特性
- 可操作性

以 JSON 格式返回文章 ID 和理由。"
```

**第 3 步: 平衡与多样性**

```
- 确保主题多样性 (每个分类最多 3 篇)
- 平衡语言 (如果为多语言)
- 避免全是负面新闻 (添加 1-2 篇正面新闻)
- 文章总数: 5-15 (用户可配置)
```

#### 3.2.3 用户兴趣建模

**初次设置** (引导)

-   用户选择 3-5 个兴趣类别
-   可选: 关键词列表
-   可选: "减少看到" 的主题

**隐式学习** (通过反馈)

```
完整收听 → +10 分
跳过 → -5 分
标记为感兴趣 → +20 分
标记为不感兴趣 → -30 分

每日更新用户画像
旧偏好在 30 天内衰减
```

---

### 3.3 AI 生成的音频简报

#### 3.3.1 简报脚本生成

**结构:**

```
1. 开场 (30秒)
   "早上好！今天是10月13日，星期一。
   以下是今天最重要的 10 条新闻。"

2. 主要内容 (5-25分钟)
   对于每篇文章:
   - 重写标题 (移除标题党)
   - 3句话摘要 或
   - 完整的 1-2 分钟阐述
   - 在新闻之间自然过渡
   
   示例:
   "在科技新闻方面，OpenAI 刚刚发布了 GPT-5。
   新模型在推理能力上显示出显著提升，并且现在能够...
   
   转向商业新闻，特斯拉在宣布...后股价飙升。"

3. 结尾 (15秒)
   "今天的简报就到这里。您可以让我重复任何一条新闻，
   或深入了解您感兴趣的话题。祝您有美好的一天！"
```

**LLM Prompt 模板:**

```python
SYSTEM_PROMPT = """
你是一名专业的电台新闻主播。
请生成一个自然、对话式的音频脚本。

风格要求:
- 清晰、简洁、引人入胜
- 避免使用“这篇文章说...”或“根据...”
- 使用主动语态
- 过渡平滑
- 带有适当的情感 (兴奋、关切、中立)

目标时长: {target_duration} 分钟
阅读速度: 每分钟 150 词
"""

USER_PROMPT = """
请根据以下文章创建一份音频新闻简报：

{articles_json}

用户偏好:
- 兴趣: {user_interests}
- 详细程度: {detail_level}  # 摘要 / 均衡 / 详细
- 语言: {language}
- 语调: {tone}  # 专业 / 休闲 / 热情

请生成一个完整的脚本，包含：
1. 引人入胜的开场
2. 每条新闻 (使用 <pause> 标签以实现自然停顿)
3. 平滑的过渡
4. 恰当的结尾

格式为针对 TTS 优化的纯文本。
"""
```

#### 3.3.2 文本转语音 (TTS)

**支持的 TTS 引擎** (优先级顺序)

**选项 1: ElevenLabs** (默认 - 最佳质量)

-   声音: "Rachel" 或用户自选
-   模型: Eleven Multilingual v2
-   成本: ~$0.30 / 简报 (3万字符)
-   语言: 29 种
-   延迟: 10分钟音频需 2-5 秒

**选项 2: OpenAI TTS**

-   声音: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
-   模型: tts-1 或 tts-1-hd
-   成本: ~$0.15-0.30 / 简报
-   语言: 60+ 种
-   延迟: 3-8 秒

**选项 3: Google Cloud TTS**

-   声音: WaveNet/Neural2
-   成本: ~$0.20 / 简报
-   语言: 40+ 种
-   质量好，成本较低

**选项 4: Azure TTS**

-   声音: Neural voices
-   成本: ~$0.15 / 简报
-   语言: 75+ 种
-   适合多语言场景

**选项 5: Piper** (本地/免费)

-   开源，本地运行
-   质量: 良好 (不如云端自然)
-   成本: $0 (仅 CPU)
-   语言: 50+
-   延迟: 在树莓派4上需 10-30 秒

**选项 6: Home Assistant TTS**

-   Google Translate TTS (免费，质量较低)
-   备用选项

**配置:**

```yaml
daily_brief:
  tts:
    provider: "elevenlabs"  # 或 openai, google, azure, piper, ha
    
    # ElevenLabs
    elevenlabs_api_key: !secret elevenlabs_key
    elevenlabs_voice_id: "21m00Tcm4TlvDq8ikWAM"  # Rachel
    elevenlabs_model: "eleven_multilingual_v2"
    
    # OpenAI
    openai_api_key: !secret openai_key
    openai_voice: "alloy"
    openai_model: "tts-1-hd"
    
    # Piper (本地)
    piper_model: "en_US-amy-medium"
    
    # 声音设置
    speed: 1.0  # 0.8-1.2
    pitch: 0  # -20 到 +20 (取决于提供商)
    
    # 音频格式
    format: "mp3"  # mp3, wav, ogg
    sample_rate: 22050  # 22050, 44100
```

#### 3.3.3 音频处理

**TTS 后处理:**

1.  **音量标准化** (loudnorm 滤波器)
2.  **添加片头/片尾音乐** (可选，用户提供)
3.  **插入停顿** (在新闻之间)
4.  **速度调整** (0.8x - 1.5x, 用户偏好)
5.  **保存为 MP3** 并附带元数据:
    -   标题: "每日简报 - 2025年10月13日"
    -   艺术家: "每日简报"
    -   专辑: "2025-10"
    -   封面: 用户可配置的图片

**存储:**

```
/config/www/daily_brief/
  ├── 2025-10-13_morning.mp3
  ├── 2025-10-13_morning.txt (脚本)
  ├── 2025-10-13_morning.json (元数据)
  ├── 2025-10-12_morning.mp3
  └── ...

保留期限: 用户可配置 (1-30天)
URL: http://homeassistant.local:8123/local/daily_brief/
```

---

### 3.4 分发与播放

#### 3.4.1 触发方式

**1. 定时自动化** (推荐)

```yaml
automation:
  - alias: "每日简报 - 早晨"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: daily_brief.generate_and_play
        data:
          media_player: media_player.bedroom_speaker
          briefing_type: "morning"
```

**2. 手动按钮** (仪表盘)

```yaml
type: button
name: "生成每日简报"
icon: mdi:newspaper-variant
tap_action:
  action: call-service
  service: daily_brief.generate
  data:
    briefing_type: "on_demand"
```

**3. 语音命令**

-   "Hey Google, ask Daily Brief for today's news"
-   "Alexa, trigger daily briefing" (通过 Alexa 例程)

**4. 物理按钮**

-   Zigbee 按钮点击 → 自动化 → 播放简报

**5. 例程集成**

```yaml
# 作为晨间例程的一部分
script:
  morning_routine:
    sequence:
      - service: light.turn_on
      - service: climate.set_temperature
      - service: daily_brief.generate_and_play  # ←
      - delay: '00:15:00'
      - service: notify.mobile_app
```

#### 3.4.2 播放选项

**直接播放**

```python
# 在指定媒体播放器上播放
service: daily_brief.play
data:
  media_player: media_player.kitchen_speaker
  briefing_date: "2025-10-13"  # 可选，默认为今天
```

**媒体源**

```python
# 作为 HA 媒体源可用
media_content_type: "music"
media_content_id: "media-source://daily_brief/2025-10-13_morning"

# 用户可以在 HA 媒体浏览器中浏览和选择
```

**移动应用**

```python
# 发送到 HA 移动应用
service: notify.mobile_app_iphone
data:
  title: "您的每日简报已准备就绪"
  message: "15 分钟, 10 条新闻"
  data:
    audio:
      url: "http://ha.local/local/daily_brief/2025-10-13.mp3"
    actions:
      - action: "PLAY_BRIEF"
        title: "立即播放"
      - action: "OPEN_APP"
        title: "打开应用"
```

**播客订阅** (未来规划)

```xml
<!-- 生成私有 RSS 订阅源 -->
<rss>
  <channel>
    <title>我的每日简报</title>
    <item>
      <title>每日简报 - 2025年10月13日</title>
      <enclosure url="..." type="audio/mpeg"/>
    </item>
  </channel>
</rss>

<!-- 用户可以在任何播客应用中订阅 -->
```

---

### 3.5 用户界面

#### 3.5.1 配置流程 (设置)

**第 1 步: 欢迎**

```
┌─────────────────────────────────┐
│  欢迎使用每日简报! 📰           │
│                                 │
│  获取由 AI 驱动的新闻摘要，      │
│  并分发到您的智能家居。         │
│                                 │
│  [开始使用]                     │
└─────────────────────────────────┘
```

**第 2 步: 内容源**

```
┌─────────────────────────────────┐
│  选择您的内容                   │
│                                 │
│  ☑ 科技 (英文)                  │
│  ☑ 科技 (中文)                  │
│  ☐ 世界新闻                     │
│  ☑ 商业与金融                   │
│  ☐ 科学与健康                   │
│  ☐ 开发者新闻                   │
│                                 │
│  + 添加自定义 RSS 订阅          │
│                                 │
│  [下一步]                       │
└─────────────────────────────────┘
```

**第 3 步: 偏好设置**

```
┌─────────────────────────────────┐
│  告诉我们您的兴趣               │
│                                 │
│  哪些主题对您最重要？           │
│  (选择 3-5 个)                  │
│                                 │
│  ☑ 人工智能                     │
│  ☑ 产品管理                     │
│  ☐ 加密货币                     │
│  ☑ 气候变化                     │
│  ☐ 太空探索                     │
│  ...                            │
│                                 │
│  简报长度:                      │
│  ○ 快速 (5-10 分钟, 5 条新闻)   │
│  ◉ 均衡 (10-20 分钟, 10 条)     │
│  ○ 深度 (20-30 分钟, 15 条)     │
│                                 │
│  [下一步]                       │
└─────────────────────────────────┘
```

**第 4 步: AI 配置**

```
┌─────────────────────────────────┐
│  AI 提供商设置                  │
│                                 │
│  内容筛选与摘要:                │
│  ◉ OpenAI (GPT-4)               │
│  ○ Anthropic (Claude)           │
│  ○ Google (Gemini)              │
│  ○ 本地 (Ollama)                │
│                                 │
│  API 密钥: [________________]   │
│                                 │
│  文本转语音:                    │
│  ◉ ElevenLabs (最佳质量)        │
│  ○ OpenAI TTS                   │
│  ○ Piper (免费, 本地)           │
│                                 │
│  ElevenLabs 密钥: [__________]  │
│  声音: [Rachel ▼]               │
│                                 │
│  [测试声音]  [下一步]           │
└─────────────────────────────────┘
```

**第 5 步: 时间安排**

```
┌─────────────────────────────────┐
│  何时生成？                     │
│                                 │
│  每日生成时间:                  │
│  [06:30] (后台运行)             │
│                                 │
│  自动播放:                      │
│  ☐ 是, 在 [07:00] 于            │
│    [media_player.bedroom ▼]     │
│                                 │
│  日期:                          │
│  ☑ 周一 ☑ 周二 ☑ 周三 ☑ 周四 ☑ 周五 │
│  ☐ 周六 ☐ 周日                    │
│                                 │
│  [完成设置]                     │
└─────────────────────────────────┘
```

#### 3.5.2 仪表盘卡片

**主控制卡片**

```yaml
type: custom:daily-brief-card
entity: sensor.daily_brief_status
show_header: true
show_progress: true
show_controls: true
```

视觉模型:

```
┌────────────────────────────────────┐
│  📰 每日简报                       │
│                                    │
│  状态: 可随时播放                  │
│  生成于: 今天 06:30 AM             │
│  时长: 15 分 23 秒                 │
│  新闻条数: 10                      │
│                                    │
│  🎧 立即收听                       │
│  🔄 重新生成   📝 查看脚本         │
│                                    │
│  最近的简报:                       │
│  • 10月13日 - 15:23 (10 条)        │
│  • 10月12日 - 14:18 (12 条)        │
│  • 10月11日 - 16:45 (9 条)         │
│                                    │
│  ⚙️ 设置                           │
└────────────────────────────────────┘
```

**新闻列表卡片**

```
┌────────────────────────────────────┐
│  今日新闻                          │
│                                    │
│  1. 🔥 OpenAI 发布 GPT-5           │
│     AI • TechCrunch • 2小时前      │
│     👍 👎                           │
│                                    │
│  2. 📈 特斯拉股价飙升 15%          │
│     商业 • Bloomberg • 4小时前     │
│     👍 👎                           │
│                                    │
│  3. 🌍 联合国气候峰会开幕          │
│     世界 • BBC • 1小时前           │
│     👍 👎                           │
│                                    │
│  ... 还有 7 条                     │
│                                    │
│  [查看全部]                        │
└────────────────────────────────────┘
```

**快捷操作**

```
┌────────────────────────────────────┐
│  每日简报                          │
│                                    │
│  [▶ 播放]  [⏸ 暂停]  [⏭ 跳过]    │
│                                    │
│  音量: ━━━━━●━━━━ 70%              │
│  进度: ━━━━●━━━━━━ 5:32/15:23      │
│                                    │
│  正在播放:                         │
│  "特斯拉股价在...后飙升"            │
│                                    │
│  [❤️ 喜欢] [👎 不喜欢] [⏭ 下一条] │
└────────────────────────────────────┘
```

#### 3.5.3 设置面板

**通用设置**

-   简报名称 (例如, "早间简报", "通勤快讯")
-   默认媒体播放器
-   生成时间安排
-   自动播放设置
-   通知偏好

**内容设置**

-   启用的内容包
-   自定义 RSS 订阅 (增/删/改)
-   排除的来源
-   排除的关键词
-   语言偏好
-   文章数量 (5-15)

**AI 设置**

-   LLM 提供商 & API 密钥
-   模型选择 (gpt-4, claude-3-5, 等)
-   TTS 提供商 & API 密钥
-   声音选择
-   语速 (0.8x - 1.5x)
-   语调 (专业/休闲)
-   详细程度 (摘要/均衡/详细)

**高级设置**

-   内容保留期限 (1-30天)
-   缓存时长
-   API 超时
-   并行获取数量
-   最低文章分数
-   去重阈值
-   调试日志

---

### 3.6 反馈与学习

#### 3.6.1 反馈机制

**播放期间:**

```python
# 语音命令 (通过 HA Assist)
"将这条新闻标记为感兴趣"
"跳过这条新闻"
"多来点像这样的内容"
"减少这个主题"

# 物理交互
- 双击按钮 → 喜欢当前新闻
- 长按按钮 → 不喜欢并跳过
```

**播放后:**

```python
# 仪表盘
- 对每条新闻点赞/踩
- 对整个简报进行星级评分
- 文字反馈 (可选)

# 通知
"为今天的简报评分: ⭐⭐⭐⭐⭐"
```

#### 3.6.2 学习系统

**收集的数据 (仅本地)**

```json
{
  "article_id": "abc123",
  "feedback": "like",  // like, dislike, skip, complete
  "timestamp": "2025-10-13T07:15:00Z",
  "listen_duration": 120,  // 秒
  "total_duration": 180,
  "topics": ["AI", "Technology"],
  "source": "techcrunch"
}
```

**用户画像更新**

```python
# 每周计算
topics_scores = {
  "AI": +50,  # 喜欢了 5 条新闻
  "Cryptocurrency": -20,  # 跳过了 2 条新闻
  "Climate": +30
}

sources_scores = {
  "techcrunch": +10,
  "theverge": -5
}

# 应用于下一次简报生成
```

**隐私:**

-   所有数据本地存储在 HA 中
-   绝不上传到云端
-   用户可以随时导出/删除
-   可选: 匿名反馈以改进默认设置

---

## 4. 技术架构

### 4.1 系统组件

```
┌─────────────────────────────────────────────────┐
│           Home Assistant                        │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  每日简报集成 (Daily Brief Integration)    │  │
│  │                                          │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  内容聚合器 (Content Aggregator)    │ │  │
│  │  │  - RSSHub 连接器                  │ │  │
│  │  │  - RSS 解析器                     │ │  │
│  │  │  - 去重器                         │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                ↓                         │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  AI 筛选器 (AI Selector)          │ │  │
│  │  │  - 评分引擎                       │ │  │
│  │  │  - LLM 排序器 (API)               │ │  │
│  │  │  - 用户偏好匹配器                 │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                ↓                         │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  脚本生成器 (Script Generator)    │ │  │
│  │  │  - LLM Prompter (API)             │ │  │
│  │  │  - 模板引擎                       │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                ↓                         │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  音频生成器 (Audio Generator)     │ │  │
│  │  │  - TTS 引擎 (API/本地)            │ │  │
│  │  │  - 音频处理器 (FFmpeg)            │ │  │
│  │  │  - 文件管理器                     │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                ↓                         │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  播放控制器 (Playback Controller) │ │  │
│  │  │  - 媒体播放器集成                 │ │  │
│  │  │  - 反馈收集器                     │ │  │
│  │  └────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  存储 (Storage)                          │  │
│  │  - SQLite (元数据, 反馈)                 │  │
│  │  - 文件系统 (音频文件)                   │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘

外部服务:
  ├─ RSSHub (内容源)
  ├─ OpenAI API (LLM + TTS)
  ├─ ElevenLabs API (TTS)
  └─ Ollama (可选, 本地 LLM)
```

### 4.2 技术栈

**语言:** Python 3.11+

**关键依赖:**

```python
# 核心 HA
homeassistant>=2024.10.0

# HTTP & 异步
aiohttp>=3.9.0
asyncio

# RSS 解析
feedparser>=6.0.10
beautifulsoup4>=4.12.0
lxml>=4.9.0

# AI/ML
openai>=1.0.0  # LLM + TTS
anthropic>=0.5.0  # Claude (可选)
google-generativeai>=0.3.0  # Gemini (可选)
elevenlabs>=0.2.0  # TTS

# 音频处理
pydub>=0.25.0
mutagen>=1.47.0  # 音频元数据

# NLP
langdetect>=1.0.9
nltk>=3.8

# 数据
python-dateutil>=2.8.0
pytz

# 可选
ollama  # 本地 LLM
transformers  # 本地嵌入
```

**外部工具:**

-   FFmpeg (音频处理)
-   RSSHub (自托管或公共实例)

### 4.3 文件结构

```
custom_components/daily_brief/
├── __init__.py              # 集成入口点
├── manifest.json            # 集成元数据
├── config_flow.py           # UI 配置流程
├── const.py                 # 常量
├── coordinator.py           # 数据更新协调器
│
├── components/
│   ├── aggregator.py        # 内容获取
│   ├── selector.py          # AI 内容筛选
│   ├── generator.py         # 脚本生成
│   ├── audio.py             # TTS & 音频处理
│   └── player.py            # 播放控制
│
├── services.py              # HA 服务
├── sensor.py                # 状态传感器
├── media_player.py          # 媒体播放器实体
├── button.py                # 操作按钮
│
├── ai/
│   ├── llm.py               # LLM 抽象层
│   ├── tts.py               # TTS 抽象层
│   ├── prompts.py           # Prompt 模板
│   └── providers/
│       ├── openai.py
│       ├── anthropic.py
│       ├── google.py
│       └── ollama.py
│
├── feeds/
│   ├── parser.py            # RSS 解析
│   ├── dedup.py             # 去重
│   ├── content_packs.py     # 预配置的订阅源
│   └── rsshub.py            # RSSHub 集成
│
├── storage/
│   ├── database.py          # SQLite 操作
│   ├── models.py            # 数据模型
│   └── cache.py             # 缓存层
│
├── utils/
│   ├── logger.py            # 日志工具
│   ├── helpers.py           # 辅助函数
│   └── validators.py        # 输入验证
│
├── frontend/
│   ├── daily_brief_card.js  # Lovelace 卡片
│   └── styles.css           # 卡片样式
│
├── translations/
│   ├── en.json              # 英文
│   ├── zh-Hans.json         # 简体中文
│   └── zh-Hant.json         # 繁体中文
│
└── tests/
    ├── test_aggregator.py
    ├── test_selector.py
    ├── test_generator.py
    └── ...
```

### 4.4 数据库结构

**SQLite 表:**

```sql
-- 用户配置
CREATE TABLE config (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    briefing_length TEXT DEFAULT 'balanced',
    interests TEXT,  -- JSON 数组
    excluded_topics TEXT,  -- JSON 数组
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 内容源
CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    type TEXT,  -- rss, api, social
    category TEXT,
    language TEXT,
    enabled BOOLEAN DEFAULT 1,
    last_fetched TIMESTAMP,
    error_count INTEGER DEFAULT 0
);

-- 文章缓存
CREATE TABLE articles (
    id TEXT PRIMARY KEY,  -- URL 的哈希值
    source_id INTEGER,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP,
    language TEXT,
    topics TEXT,  -- JSON 数组
    score REAL,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- 生成的简报
CREATE TABLE briefings (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    type TEXT,  -- morning, evening, on_demand
    article_ids TEXT,  -- JSON 数组
    script TEXT,
    audio_path TEXT,
    duration INTEGER,  -- 秒
    status TEXT,  -- generating, ready, played, error
    generated_at TIMESTAMP,
    played_at TIMESTAMP,
    play_count INTEGER DEFAULT 0
);

-- 用户反馈
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    briefing_id INTEGER,
    article_id TEXT,
    feedback_type TEXT,  -- like, dislike, skip, complete
    listen_duration INTEGER,  -- 秒
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (briefing_id) REFERENCES briefings(id)
);

-- 用户画像 (学习到的偏好)
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL UNIQUE,
    score REAL DEFAULT 0,
    source TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_score ON articles(score DESC);
CREATE INDEX idx_briefings_date ON briefings(date DESC);
CREATE INDEX idx_feedback_timestamp ON feedback(timestamp DESC);
```

### 4.5 API 端点 (HA 服务)

**服务: `daily_brief.generate`**

```yaml
service: daily_brief.generate
data:
  briefing_type: "morning"  # morning, evening, on_demand
  force_refresh: false  # 跳过缓存
  article_count: 10  # 覆盖默认值
  target_duration: 15  # 分钟
  language: "en"  # 覆盖默认值
```

**服务: `daily_brief.play`**

```yaml
service: daily_brief.play
data:
  media_player: media_player.living_room
  briefing_date: "2025-10-13"  # 可选，默认为今天
  shuffle: false
```

**服务: `daily_brief.stop`**

```yaml
service: daily_brief.stop
data:
  media_player: media_player.living_room
```

**服务: `daily_brief.skip_story`**

```yaml
service: daily_brief.skip_story
data:
  feedback: "dislike"  # 可选: like, dislike, neutral
```

**服务: `daily_brief.feedback`**

```yaml
service: daily_brief.feedback
data:
  article_id: "abc123"
  feedback_type: "like"  # like, dislike, skip
```

**服务: `daily_brief.add_source`**

```yaml
service: daily_brief.add_source
data:
  name: "我的博客"
  url: "https://example.com/feed.xml"
  category: "Technology"
```

**服务: `daily_brief.regenerate`**

```yaml
service: daily_brief.regenerate
data:
  keep_articles: true  # 使用相同文章，重新生成脚本/音频
```

### 4.6 状态实体

**传感器 (Sensors):**

```yaml
# 主状态传感器
sensor.daily_brief_status:
  state: "ready"  # idle, fetching, selecting, generating, ready, playing, error
  attributes:
    last_generated: "2025-10-13 06:30:00"
    article_count: 10
    duration: "15:23"
    audio_url: "http://..."
    briefing_type: "morning"
    stories:
      - title: "OpenAI 发布 GPT-5"
        source: "TechCrunch"
        duration: 92
      - ...

# 生成进度
sensor.daily_brief_progress:
  state: 65  # 百分比
  attributes:
    current_step: "正在生成音频"
    total_steps: 5
    eta_seconds: 30

# 今日文章
sensor.daily_brief_articles:
  state: 10  # 数量
  attributes:
    articles:
      - id: "abc123"
        title: "..."
        source: "..."
        score: 85
        selected: true
      - ...

# 用户统计
sensor.daily_brief_stats:
  state: "active"
  attributes:
    total_briefings: 45
    total_listened: 38
    avg_listen_rate: 0.84
    top_topics: ["AI", "Business", "Science"]
    top_sources: ["TechCrunch", "BBC", "Bloomberg"]
```

**二进制传感器 (Binary Sensors):**

```yaml
# 简报是否就绪?
binary_sensor.daily_brief_ready:
  state: "on"  # on = 就绪, off = 未就绪

# 简报是否正在播放?
binary_sensor.daily_brief_playing:
  state: "off"

# 是否有新内容?
binary_sensor.daily_brief_new_content:
  state: "on"
```

**按钮 (Buttons):**

```yaml
# 快捷操作按钮
button.daily_brief_generate:
  press: "生成新简报"

button.daily_brief_play:
  press: "播放最新简报"

button.daily_brief_regenerate:
  press: "用新脚本重新生成"
```

**媒体播放器 (Media Player):**

```yaml
# 用于简报控制的虚拟媒体播放器
media_player.daily_brief:
  state: "playing"
  attributes:
    media_content_type: "music"
    media_title: "每日简报 - 2025年10月13日"
    media_duration: 923  # 秒
    media_position: 245
    volume_level: 0.7
    is_volume_muted: false
    media_playlist:
      - "新闻 1: OpenAI 发布 GPT-5"
      - "新闻 2: 特斯拉股价飙升"
      - ...
```

---

## 5. 用户体验流程

### 5.1 首次设置 (引导)

```
用户通过 HACS 安装
      ↓
重启 Home Assistant
      ↓
通知: "每日简报已安装！点击以配置"
      ↓
配置流程 (5步)
  1. 欢迎 & 概述
  2. 选择内容包
  3. 设置偏好 (兴趣, 长度)
  4. 配置 AI (API 密钥)
  5. 设置时间安排
      ↓
"设置完成！您的第一份简报将在早上 7:00 准备就绪"
      ↓
仪表盘卡片自动添加
      ↓
第二天早上: 简报自动生成并播放
```

### 5.2 日常使用流程

**场景 A: 自动晨间简报**

```
06:30 - 后台开始生成
  ├─ 获取新文章 (2 分钟)
  ├─ AI 筛选 (1 分钟)
  ├─ 生成脚本 (2 分钟)
  ├─ 生成音频 (3 分钟)
  └─ 保存并通知用户

06:38 - 通知: "您的每日简报已准备就绪 (15 分钟, 10 条新闻)"

07:00 - 在卧室音箱上自动播放
  ├─ 用户醒来
  ├─ 在洗漱时收听
  ├─ 轻点物理按钮以喜欢/跳过新闻
  └─ 简报在 07:15 结束

07:30 - 用户出门上班
  ├─ 未完成的简报同步到手机
  └─ 在通勤途中继续收听
```

**场景 B: 按需生成**

```
用户: 在仪表盘上点击 "生成简报" 按钮

系统:
  ├─ 显示进度: "正在获取文章... 10%"
  ├─ "正在筛选头条新闻... 40%"
  ├─ "正在生成脚本... 70%"
  ├─ "正在创建音频... 90%"
  └─ "已就绪!" (总共 3-5 分钟)

用户: 点击 "立即播放"
  └─ 在选定的媒体播放器上播放
```

**场景 C: 语音命令**

```
用户: "Hey Google, 让每日简报播放今天的新闻"

Google Assistant:
  └─ 触发 HA 自动化

系统:
  ├─ 检查今天的简报是否存在
  ├─ 如果存在: 立即播放
  └─ 如果不存在: 先生成 (可能需要 3-5 分钟)

用户: 在做晚饭时收听
```

### 5.3 反馈循环

```
播放期间:
  用户双击 Zigbee 按钮
    ↓
  系统记录: "用户喜欢了第 3 条新闻"
    ↓
  更新 user_profile 表
    ↓
  显示提示: "我们会为您展示更多类似内容"

每周:
  系统分析反馈
    ↓
  调整主题分数
    ↓
  下一次的简报反映了新的偏好
    ↓
  用户注意到: "这周的简报更对我的胃口了！"
```

---

## 6. 内容包规范

### 6.1 内置内容包

**科技 (英文)**

```yaml
id: tech_en
name: "Technology News (English)"
language: en
feeds:
  - name: "Hacker News"
    url: "https://rsshub.app/hackernews/best"
    weight: 1.2
  - name: "TechCrunch"
    url: "https://techcrunch.com/feed/"
    weight: 1.0
  - name: "The Verge"
    url: "https://www.theverge.com/rss/index.xml"
    weight: 1.0
  - name: "Ars Technica"
    url: "https://feeds.arstechnica.com/arstechnica/index"
    weight: 0.9
  - name: "MIT Tech Review"
    url: "https://www.technologyreview.com/feed/"
    weight: 1.1
  - name: "Wired"
    url: "https://www.wired.com/feed/rss"
    weight: 0.9
topics:
  - "Artificial Intelligence"
  - "Startups"
  - "Consumer Tech"
  - "Software"
  - "Hardware"
```

**科技 (中文)**

```yaml
id: tech_zh
name: "科技新闻（中文）"
language: zh
feeds:
  - name: "36氪"
    url: "https://rsshub.app/36kr/newsflashes"
    weight: 1.1
  - name: "少数派"
    url: "https://rsshub.app/sspai/index"
    weight: 1.0
  - name: "爱范儿"
    url: "https://rsshub.app/ifanr/app"
    weight: 1.0
  - name: "InfoQ中文"
    url: "https://www.infoq.cn/feed"
    weight: 0.9
  - name: "CSDN热榜"
    url: "https://rsshub.app/csdn/blog/hot"
    weight: 0.8
  - name: "V2EX"
    url: "https://rsshub.app/v2ex/topics/hot"
    weight: 0.9
topics:
  - "人工智能"
  - "创业公司"
  - "消费电子"
  - "软件开发"
  - "互联网"
```

**世界新闻 (英文)**

```yaml
id: world_news_en
name: "World News"
language: en
feeds:
  - name: "BBC World"
    url: "http://feeds.bbci.co.uk/news/world/rss.xml"
    weight: 1.2
  - name: "Reuters"
    url: "https://rsshub.app/reuters/world"
    weight: 1.2
  - name: "Al Jazeera"
    url: "https://www.aljazeera.com/xml/rss/all.xml"
    weight: 1.0
  - name: "The Guardian"
    url: "https://www.theguardian.com/world/rss"
    weight: 1.0
  - name: "AP News"
    url: "https://rsshub.app/apnews/topics/ap-top-news"
    weight: 1.1
```

**中文新闻**

```yaml
id: news_zh
name: "中文新闻"
language: zh
feeds:
  - name: "知乎热榜"
    url: "https://rsshub.app/zhihu/hotlist"
    weight: 1.0
  - name: "澎湃新闻"
    url: "https://rsshub.app/thepaper/featured"
    weight: 1.1
  - name: "财新网"
    url: "https://rsshub.app/caixin/latest"
    weight: 1.2
  - name: "FT中文网"
    url: "https://rsshub.app/ft/chinese"
    weight: 1.1
  - name: "微博热搜"
    url: "https://rsshub.app/weibo/search/hot"
    weight: 0.8  # 权重较低 (可能很嘈杂)
```

**商业与金融**

```yaml
id: business
name: "Business & Finance"
language: en
feeds:
  - name: "Wall Street Journal"
    url: "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
    weight: 1.2
  - name: "Bloomberg"
    url: "https://www.bloomberg.com/feed/podcast/etf-report.xml"
    weight: 1.2
  - name: "Financial Times"
    url: "https://www.ft.com/?format=rss"
    weight: 1.1
  - name: "The Economist"
    url: "https://www.economist.com/finance-and-economics/rss.xml"
    weight: 1.1
  - name: "彭博中文"
    url: "https://rsshub.app/bloomberg/chinese"
    weight: 1.0
```

**科学与健康**

```yaml
id: science
name: "Science & Health"
language: en
feeds:
  - name: "Nature News"
    url: "https://www.nature.com/nature.rss"
    weight: 1.2
  - name: "Science Daily"
    url: "https://www.sciencedaily.com/rss/all.xml"
    weight: 1.0
  - name: "New Scientist"
    url: "https://www.newscientist.com/feed/home"
    weight: 1.0
  - name: "果壳网"
    url: "https://rsshub.app/guokr/scientific"
    weight: 0.9
  - name: "科学松鼠会"
    url: "https://rsshub.app/songshuhui"
    weight: 0.9
```

**开发者新闻**

```yaml
id: dev
name: "Developer News"
language: en
feeds:
  - name: "GitHub Trending"
    url: "https://rsshub.app/github/trending/daily"
    weight: 1.1
  - name: "Dev.to"
    url: "https://dev.to/feed"
    weight: 0.9
  - name: "Lobsters"
    url: "https://lobste.rs/rss"
    weight: 1.0
  - name: "Reddit r/programming"
    url: "https://rsshub.app/reddit/hot/programming"
    weight: 0.8
  - name: "Hacker News Show"
    url: "https://rsshub.app/hackernews/show"
    weight: 0.9
```

### 6.2 内容包格式

**YAML 结构:**

```yaml
# content_packs/my_pack.yaml
id: "unique_id"
name: "显示名称"
description: "简短描述"
language: "en"  # 或 zh, es, fr, 等.
category: "technology"  # technology, news, business, science, 等.
icon: "mdi:newspaper"  # Material Design 图标
author: "Ryan-Guo123"
version: "1.0.0"
enabled: true

feeds:
  - name: "订阅源名称"
    url: "https://example.com/feed.xml"
    type: "rss"  # rss, atom, json
    weight: 1.0  # 0.5-2.0, 影响文章评分
    language: "en"
    refresh_interval: 3600  # 秒
    max_articles: 50

  - name: "另一个订阅源"
    url: "https://rsshub.app/example"
    weight: 1.2
    tags: ["breaking", "verified"]  # 可选标签

topics:
  - "主题 1"
  - "主题 2"
  - "主题 3"

keywords:
  include:
    - "AI"
    - "Machine Learning"
  exclude:
    - "Celebrity"
    - "Sports"

settings:
  min_article_score: 50
  dedupe_threshold: 0.8
  prefer_original: true  # 偏好原创报道而非聚合器
```

### 6.3 社区内容包

**仓库结构:**

```
daily-brief-content-packs/  (独立的 GitHub 仓库)
├── README.md
├── official/
│   ├── tech_en.yaml
│   ├── tech_zh.yaml
│   ├── news_en.yaml
│   └── ...
├── community/
│   ├── crypto.yaml
│   ├── gaming.yaml
│   ├── climate.yaml
│   └── ...
└── schema.json  # 验证用的 schema
```

**安装:**

```python
# 在 HA UI 中
设置 → 每日简报 → 内容包 → 浏览社区

# 或通过服务调用
service: daily_brief.install_pack
data:
  url: "https://raw.githubusercontent.com/.../crypto.yaml"
```

---

## 7. AI 集成细节

### 7.1 LLM 提供商抽象层

**基础接口:**

```python
# ai/llm.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    async def select_articles(
        self,
        articles: List[Dict],
        user_interests: List[str],
        count: int
    ) -> List[Dict]:
        """从候选文章中选择前 N 篇。"""
        pass
    
    @abstractmethod
    async def generate_script(
        self,
        articles: List[Dict],
        style: str,
        duration: int,
        language: str
    ) -> str:
        """生成简报脚本。"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试 API 连接和凭据。"""
        pass
```

**OpenAI 实现:**

```python
# ai/providers/openai.py
from openai import AsyncOpenAI
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def select_articles(self, articles, user_interests, count):
        prompt = self._build_selection_prompt(articles, user_interests, count)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SELECTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def generate_script(self, articles, style, duration, language):
        prompt = self._build_script_prompt(articles, style, duration, language)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
```

**配置:**

```yaml
# configuration.yaml
daily_brief:
  llm:
    provider: openai
    api_key: !secret openai_api_key
    model: gpt-4o-mini  # 或 gpt-4o, gpt-4-turbo
    
    # 提供商特定设置
    temperature: 0.7
    max_tokens: 4000
    timeout: 60
    
    # 备用
    fallback_provider: ollama
    fallback_model: llama3
```

### 7.2 Prompt 工程

**文章选择 Prompt:**

```python
SELECTION_SYSTEM_PROMPT = """
你是一名专业的每日简报新闻编辑。
你的目标是：选择最重要和最相关的文章。

标准:
1. 影响力: 这对用户重要吗？
2. 时效性: 这是突发/最近的新闻吗？
3. 独特性: 它是否提供了新信息？
4. 可操作性: 用户能据此采取行动吗？
5. 相关性: 是否匹配用户兴趣？

返回 JSON:
{
  "selected": [
    {
      "id": "article_id",
      "reason": "一句话的理由",
      "priority": 1-10
    }
  ],
  "rejected": ["id1", "id2"],
  "summary": "对所选文章的简要说明"
}
"""

SELECTION_USER_PROMPT_TEMPLATE = """
用户画像:
- 兴趣: {interests}
- 之前喜欢的主题: {liked_topics}
- 之前不喜欢的主题: {disliked_topics}

候选文章 ({count}篇):
{articles_json}

任务: 精确选择 {target_count} 篇文章。
平衡性: 混合突发新闻、深度分析和用户兴趣。
多样性: 多个主题，避免重复。
"""
```

**脚本生成 Prompt:**

```python
SCRIPT_SYSTEM_PROMPT = """
你是一名专业的播客主持人，正在制作一份音频新闻简报。

风格指南:
- 对话式但权威
- 发音清晰 (避免使用未解释的术语)
- 使用 <pause> 标签实现自然停顿
- 在新闻之间进行引人入胜的过渡
- 根据新闻内容使用适当的情感语调

结构:
1. 开场: 热情的问候，日期，简要预告
2. 新闻: 每条都包含背景、关键事实、影响
3. 过渡: 在主题之间平滑连接
4. 结尾: 总结，如果相关则提供行动号召

时长: 目标 {duration} 分钟
语速: 约 150 词/分钟
格式: 纯文本 (将转换为音频)
"""

SCRIPT_USER_PROMPT_TEMPLATE = """
请根据这些文章生成一份 {duration} 分钟的音频简报：

{articles_with_summaries}

用户偏好:
- 详细程度: {detail_level}  # 摘要, 均衡, 详细
- 语调: {tone}  # 专业, 休闲, 热情
- 语言: {language}
- 特别兴趣: {interests}

说明:
- 从最重要/突发的新闻开始
- 使用清晰、简洁的语言
- 添加 <pause> 标签以实现自然停顿
- 为技术术语提供上下文解释
- 以积极或前瞻性的基调结束

现在请生成完整的脚本：
"""
```

### 7.3 TTS 提供商抽象层

**基础接口:**

```python
# ai/tts.py
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class TTSProvider(ABC):
    @abstractmethod
    async def generate_audio(
        self,
        text: str,
        voice: str,
        language: str,
        speed: float = 1.0
    ) -> bytes:
        """将文本转换为音频。"""
        pass
    
    @abstractmethod
    async def list_voices(self, language: Optional[str] = None) -> List[Dict]:
        """获取可用声音列表。"""
        pass
    
    @abstractmethod
    async def estimate_cost(self, text: str) -> float:
        """估算成本 (美元)。"""
        pass
```

**ElevenLabs 实现:**

```python
# ai/providers/elevenlabs.py
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import VoiceSettings

class ElevenLabsProvider(TTSProvider):
    def __init__(self, api_key: str):
        self.client = AsyncElevenLabs(api_key=api_key)
    
    async def generate_audio(self, text, voice, language, speed):
        audio = await self.client.generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
                speaking_rate=speed
            )
        )
        
        # 返回音频字节
        return b"".join(audio)
    
    async def list_voices(self, language=None):
        voices = await self.client.voices.get_all()
        return [
            {
                "id": v.voice_id,
                "name": v.name,
                "language": v.labels.get("language", "en"),
                "gender": v.labels.get("gender"),
                "preview_url": v.preview_url
            }
            for v in voices.voices
            if not language or v.labels.get("language") == language
        ]
    
    async def estimate_cost(self, text):
        # ElevenLabs: 每 1000 字符 $0.30
        return len(text) / 1000 * 0.30
```

**配置:**

```yaml
daily_brief:
  tts:
    provider: elevenlabs
    api_key: !secret elevenlabs_key
    
    # 声音选择
    voice_id: "21m00Tcm4TlvDq8ikWAM"  # Rachel
    # 或 voice_name: "Rachel"
    
    # 语音设置
    speed: 1.0  # 0.25 - 4.0
    stability: 0.5  # 0.0 - 1.0
    similarity_boost: 0.75  # 0.0 - 1.0
    
    # 音频格式
    output_format: mp3
    sample_rate: 22050
    
    # 成本控制
    max_cost_per_briefing: 0.50  # 美元
    fallback_on_limit: true
    fallback_provider: piper
```

---

## 8. 开发路线图

### 8.1 MVP (v0.1.0) - 第 1-4 周

**目标:** 可用的基础集成

**功能:**

-   [x] RSS 订阅源聚合 (5个内置内容包)
-   [x] 基础 AI 筛选 (仅 OpenAI)
-   [x] 脚本生成
-   [x] TTS 集成 (OpenAI TTS)
-   [x] 手动触发 (按钮)
-   [x] 仪表盘卡片
-   [x] 配置流程
-   [x] 存储 (SQLite)

**交付物:**

-   可用的 HACS 集成
-   基础文档
-   安装指南
-   1-2 个演示视频

**成功标准:**

-   可以通过 HACS 安装
-   可以生成和播放简报
-   每次简报成本 < $0.50
-   10 个 Beta 测试者成功使用

---

### 8.2 Beta (v0.2.0) - 第 5-8 周

**目标:** 打磨和社区反馈

**功能:**

-   [x] 定时自动化
-   [x] 多个 TTS 提供商 (ElevenLabs, Piper)
-   [x] 反馈系统 (喜欢/不喜欢)
-   [x] 10+ 内容包
-   [x] 多语言支持 (中/英)
-   [x] 历史记录与重播
-   [x] 改进的 UI/UX

**交付物:**

-   公开 Beta 版本
-   完整文档
-   社区 Discord/论坛
-   教程视频

**成功标准:**

-   100+ 安装量
-   < 5 个严重 bug
-   来自 Beta 测试者的积极反馈
-   NPS > 40

---

### 8.3 v1.0.0 (稳定版) - 第 9-12 周

**目标:** 生产就绪的发布版

**功能:**

-   [x] 所有 MVP + Beta 功能
-   [x] 本地 LLM 支持 (Ollama)
-   [x] 高级个性化
-   [x] 移动应用集成
-   [x] 播客源生成
-   [x] 导入/导出设置
-   [x] 全面的测试

**交付物:**

-   稳定的 1.0 版本
-   完整的文档
-   视频教程
-   博客文章/公告

**成功标准:**

-   500+ 安装量
-   < 2 个严重 bug
-   4.5+ 星级评分
-   被 HA 社区博客报道

---

### 8.4 v1.1+ (未来增强)

**计划功能:**

**v1.1 - 高级内容**

-   社交媒体集成 (Twitter, Reddit, HN)
-   图片/视频内容描述
-   突发新闻警报
-   紧急简报

**v1.2 - 协作**

-   多用户画像
-   家庭友好模式
-   共享反馈
-   向家庭成员推荐内容

**v1.3 - 平台扩展**

-   Telegram 机器人
-   Discord 机器人
-   Chrome 扩展
-   iOS/Android 应用

**v1.4 - 高级 AI**

-   声音克隆 (使用您自己的声音)
-   对话模式 (提出追问)
-   事实核查高亮
-   偏见检测和多角度观点

**v2.0 - 企业功能**

-   团队简报
-   自定义内容工作流
-   用于外部集成的 API
-   高级分析

---

## 9. 测试策略

### 9.1 单元测试

**覆盖率目标:** >80%

```python
# tests/test_aggregator.py
async def test_fetch_rss_feed():
    """测试 RSS 订阅源获取。"""
    aggregator = ContentAggregator()
    articles = await aggregator.fetch_feed("https://example.com/feed.xml")
    assert len(articles) > 0
    assert "title" in articles[0]
    assert "url" in articles[0]

async def test_deduplicate_articles():
    """测试文章去重。"""
    articles = [
        {"title": "OpenAI 发布 GPT-5", "url": "https://a.com"},
        {"title": "OpenAI 发布 GPT-5", "url": "https://b.com"},
        {"title": "另一篇文章", "url": "https://c.com"}
    ]
    deduped = deduplicate(articles)
    assert len(deduped) == 2

# tests/test_selector.py
async def test_article_scoring():
    """测试文章重要性评分。"""
    article = {
        "title": "突发：重大技术突破",
        "published": "2025-10-13T08:00:00Z",
        "source": "TechCrunch"
    }
    score = calculate_score(article, user_interests=["Technology"])
    assert score > 50

# tests/test_generator.py
async def test_script_generation():
    """测试脚本生成。"""
    articles = load_test_articles()
    script = await generate_script(articles, duration=15)
    assert len(script) > 1000
    assert "good morning" in script.lower()
    assert "<pause>" in script

# tests/test_audio.py
async def test_tts_generation():
    """测试 TTS 音频生成。"""
    text = "这是一个测试简报。"
    audio = await generate_audio(text, provider="mock")
    assert len(audio) > 0
    assert audio.startswith(b"ID3")  # MP3 标头
```

### 9.2 集成测试

```python
# tests/test_integration.py
async def test_full_briefing_generation():
    """测试完整的简报生成流程。"""
    # 设置
    config = load_test_config()
    
    # 获取
    articles = await fetch_all_sources(config)
    assert len(articles) > 50
    
    # 筛选
    selected = await select_articles(articles, count=10)
    assert len(selected) == 10
    
    # 生成脚本
    script = await generate_script(selected)
    assert len(script) > 1000
    
    # 生成音频
    audio_path = await generate_audio(script)
    assert os.path.exists(audio_path)
    assert os.path.getsize(audio_path) > 100000  # >100KB
    
    # 验证元数据
    briefing = load_briefing_metadata()
    assert briefing["status"] == "ready"
    assert briefing["article_count"] == 10

async def test_scheduled_automation():
    """测试定时简报生成。"""
    # 触发自动化
    await trigger_automation("daily_brief_morning")
    
    # 等待完成
    await asyncio.sleep(300)  # 5 分钟
    
    # 验证简报已创建
    briefing = get_latest_briefing()
    assert briefing is not None
    assert briefing["status"] == "ready"
```

### 9.3 用户验收测试

**测试场景:**

1.  **首次设置**
    
    -   用户通过 HACS 安装
    -   完成配置流程
    -   第二天早上收到第一份简报
    -   ✅ 通过条件: 简报成功播放
2.  **日常使用**
    
    -   用户收听 10 天的自动简报
    -   提供反馈 (5+ 喜欢, 2+ 不喜欢)
    -   ✅ 通过条件: 内容根据反馈得到改善
3.  **手动生成**
    
    -   用户点击 "生成" 按钮
    -   等待完成
    -   立即播放
    -   ✅ 通过条件: 生成在 <5 分钟内完成
4.  **语音命令**
    
    -   用户通过 Google/Alexa 触发
    -   简报在正确的设备上播放
    -   ✅ 通过条件: 90% 以上的时间能正常工作
5.  **错误处理**
    
    -   模拟 API 失败
    -   模拟网络问题
    -   ✅ 通过条件: 清晰的错误消息，优雅降级

### 9.4 性能测试

**基准:**

```python
# tests/test_performance.py
async def test_generation_time():
    """简报生成应在 <5 分钟内完成。"""
    start = time.time()
    await generate_briefing()
    duration = time.time() - start
    assert duration < 300  # 5 分钟

async def test_api_cost():
    """API 成本应 <$0.50 / 简报。"""
    cost = await estimate_generation_cost()
    assert cost < 0.50

async def test_memory_usage():
    """内存使用应 <500MB。"""
    import psutil
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024
    
    await generate_briefing()
    
    mem_after = process.memory_info().rss / 1024 / 1024
    mem_increase = mem_after - mem_before
    assert mem_increase < 500  # MB

async def test_concurrent_generations():
    """应能处理多个并发生成请求。"""
    tasks = [generate_briefing() for _ in range(3)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(r is not None for r in results)
```

---

## 10. 文档计划

### 10.1 用户文档

**README.md**

-   项目概述
-   主要功能
-   快速入门指南
-   截图/演示视频
-   安装说明
-   基本配置
-   常见问题
-   支持链接

**安装指南**

```markdown
# 安装

## 通过 HACS (推荐)

1. 在 Home Assistant 中打开 HACS
2. 进入 集成
3. 点击右上角的三个点 → 自定义存储库
4. 添加: `https://github.com/Ryan-Guo123/ha-ai-daily-brief`
5. 类别: 集成
6. 点击 "添加"
7. 搜索 "Daily Brief"
8. 点击 "下载"
9. 重启 Home Assistant

## 手动安装

1. 从 GitHub 下载最新版本
2. 解压到 `config/custom_components/daily_brief/`
3. 重启 Home Assistant
```

**配置指南**

-   分步设置向导
-   API 密钥获取指南
-   内容包选择
-   自动化示例
-   故障排除

**用户指南**

-   日常使用工作流
-   仪表盘定制
-   添加自定义订阅源
-   反馈系统
-   语音命令设置
-   移动应用集成

### 10.2 开发者文档

**架构概述**

-   系统图
-   组件描述
-   数据流
-   API 端点

**开发设置**

````markdown
# 开发设置

## 先决条件
- Python 3.11+
- Home Assistant Core 2024.10+
- Git

## 设置

```bash
# 克隆仓库
git clone https://github.com/Ryan-Guo123/ha-ai-daily-brief
cd ha-ai-daily-brief

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements_dev.txt

# 设置 pre-commit 钩子
pre-commit install

# 运行测试
pytest tests/
```

## 本地运行

```bash
# 复制到 HA 配置目录
ln -s $(pwd)/custom_components/daily_brief ~/.homeassistant/custom_components/

# 重启 HA
ha core restart
```

````

**API 文档**
-   服务定义
-   实体结构
-   事件类型
-   配置选项

**贡献指南**
-   代码风格 (Black, isort, pylint)
-   Git 工作流
-   PR 指南
-   测试要求

### 10.3 社区资源

**Discord/论坛**
-   设置帮助频道
-   反馈与建议
-   Bug 报告
-   “作品展示” (用户配置)

**视频教程**
-   安装演练
-   配置指南
-   高级定制
-   常见问题故障排除

**博客文章**
-   发布公告
-   用例示例
-   集成指南
-   幕后故事

---

## 11. 发布策略

### 11.1 预发布 (第 1-2 周)

**目标:**
-   建立期待
-   收集反馈
-   招募 Beta 测试者

**活动:**
1.  **创建落地页**
    -   问题陈述
    -   功能概述
    -   演示视频
    -   用于早期访问的邮件注册
2.  **社交媒体预热**
    -   在 Reddit r/homeassistant 发帖
    -   在个人推特账户发推
    -   在 HA Discord 中分享
3.  **联系影响者**
    -   HA YouTubers (Smart Home Junkie, Everything Smart Home)
    -   科技博主
    -   提供早期访问权限
4.  **Beta 注册**
    -   招募 20-50 名 Beta 测试者
    -   创建私有 Discord 频道
    -   提供测试指南

### 11.2 Beta 发布 (第 3-6 周)

**目标:**
-   验证 MVP
-   修复严重 bug
-   收集用户评价

**活动:**
1.  **向 Beta 测试者发布**
    -   私有 HACS 仓库
    -   设置支持频道
    -   每日签到
2.  **根据反馈迭代**
    -   Bug 修复 (优先)
    -   UX 改进
    -   功能请求 (评估)
3.  **创建内容**
    -   用户评价 (视频)
    -   案例研究
    -   常见问题解答
4.  **准备发布材料**
    -   新闻稿
    -   社交媒体帖子
    -   博客文章草稿
    -   演示视频

### 11.3 公开发布 (第 7 周)

**目标:**
-   第一周 500+ 安装量
-   登上 r/homeassistant 首页
-   被 HA 社区博客报道

**发布日活动:**

**上午 (00:00 UTC)**
1.  发布到公共 HACS
2.  提交到 HA 社区集成列表
3.  在 Home Assistant 论坛发帖
4.  创建 GitHub discussion 帖子

**下午 (12:00 UTC)**
1.  发布到 r/homeassistant
    -   标题: "我为 Home Assistant 构建了一个 AI 驱动的新闻简报"
    -   包括: 演示视频, 主要功能, 链接
    -   与评论互动
2.  发布到 r/selfhosted
3.  在 LinkedIn, Twitter/X 上分享
4.  邮件通知 Beta 测试者 (请他们分享)

**晚上 (18:00 UTC)**
1.  监控反馈和问题
2.  回答问题
3.  立即修复任何严重 bug

**第一周活动:**
1.  在论坛/Reddit 上每日互动
2.  收集并回应问题
3.  发布 bug 修复更新
4.  分享用户成功故事
5.  联系科技博客 (投稿)

### 11.4 发布后 (第 8 周+)

**增长策略:**

1.  **内容营销**
    -   每周博客文章
    -   教程视频
    -   用户聚焦
    -   集成指南
2.  **社区建设**
    -   活跃的 Discord 社区
    -   每月社区会议
    -   功能投票
    -   社区内容包
3.  **集成合作**
    -   与内容提供商合作
    -   与其他 HA 工具集成
    -   交叉推广
4.  **公关与媒体**
    -   提交到 Product Hunt
    -   联系科技出版物
    -   播客访谈
    -   会议演讲

---

## 12. 指标与分析

### 12.1 关键绩效指标 (KPIs)

**采用指标:**
-   总安装量 (通过 HACS 统计)
-   活跃用户 (选择加入的遥测)
-   日/月活跃用户 (DAU/MAU)
-   留存率 (D1, D7, D30)

**参与指标:**
-   每日生成的简报数
-   完成率 (简报被收听的百分比)
-   反馈率 (提供反馈的用户百分比)
-   平均收听时长

**质量指标:**
-   用户满意度 (NPS 调查)
-   Bug 报告率
-   功能请求率
-   GitHub 星标 & forks

**技术指标:**
-   平均生成时间
-   每次简报的 API 成本
-   错误率
-   系统资源使用情况

### 12.2 遥测 (隐私优先)

**选择加入的匿名遥测:**

```yaml
# 仅在用户明确启用时收集
daily_brief:
  telemetry:
    enabled: false  # 默认: 禁用
    anonymous_id: "random-uuid"  # 无个人数据
```

**收集的数据 (如果启用):**

-   安装 ID (随机 UUID)
-   HA 版本
-   集成版本
-   匿名使用统计:
    -   生成的简报数 (计数)
    -   平均时长
    -   使用的内容包 (计数, 非名称)
    -   使用的 TTS 提供商
    -   语言
-   匿名错误日志 (无个人数据)

**不收集的数据:**

-   用户身份
-   HA IP 地址
-   具体内容来源
-   实际文章标题/内容
-   音频文件
-   任何个人信息

**隐私承诺:**

-   所有遥测都是选择加入的
-   用户可以随时禁用
-   数据是匿名的
-   不向第三方出售或共享数据
-   每月透明度报告

### 12.3 成功标准 (6个月)

**最低成功:**

-   500+ 活跃安装
-   GitHub 3.5+ 星级评分
-   < 10 个未解决的严重 bug
-   活跃的社区 (50+ Discord 成员)

**目标成功:**

-   1,000+ 活跃安装
-   4.5+ 星级评分
-   < 5 个未解决的 bug
-   繁荣的社区 (200+ Discord 成员)
-   10+ 社区内容包
-   被 HA 社区博客报道
-   3+ 第三方集成

**挑战目标:**

-   5,000+ 安装
-   4.8+ 星级评分
-   成为官方 HA 集成 (提交到核心)
-   会议演讲被接受
-   媒体报道 (科技博客)

---

## 13. 风险管理

### 13.1 技术风险

**风险: API 成本螺旋上升**

-   **影响:** 高
-   **概率:** 中
-   **缓解措施:**
    -   实现每个用户的成本跟踪
    -   设置硬性限制 (每次简报最高 $0.50)
    -   自动回退到更便宜的提供商
    -   在接近限制时提醒用户
    -   积极缓存

**风险: API 提供商变更/停止服务**

-   **影响:** 高
-   **概率:** 低
-   **缓解措施:**
    -   从第一天起就支持多个提供商
    -   抽象所有 API 调用 (无供应商锁定)
    -   维持到本地选项的回退 (Piper, Ollama)
    -   定期监控提供商状态

**风险: 低端硬件上的性能问题**

-   **影响:** 中
-   **概率:** 中
-   **缓解措施:**
    -   优化代码效率
    -   提供 "精简模式" 设置
    -   在文档中明确硬件要求
    -   全程使用异步操作
    -   可选的云生成服务

**风险: 存储空间耗尽**

-   **影响:** 低
-   **概率:** 中
-   **缓解措施:**
    -   自动清理旧简报
    -   可配置的保留期
    -   压缩音频文件
    -   在磁盘使用率达到 80% 时警告用户

### 13.2 法律/合规风险

**风险: 内容的版权问题**

-   **影响:** 高
-   **概率:** 低-中
-   **缓解措施:**
    -   仅使用公共 RSS 订阅源
    -   遵守 robots.txt
    -   链接到原始来源
    -   生成摘要 (合理使用)
    -   明确署名
    -   建立 DMCA 删除流程

**风险: 隐私/GDPR 合规**

-   **影响:** 高
-   **概率:** 低
-   **缓解措施:**
    -   默认所有数据本地存储
    -   未经同意不收集数据
    -   简单的导出/删除功能
    -   清晰的隐私政策
    -   符合 GDPR 的设计

**风险: 违反服务条款 (API)**

-   **影响:** 中
-   **概率:** 低
-   **缓解措施:**
    -   审查所有 API 的服务条款
    -   保持在速率限制内
    -   不转售 API 服务
    -   监控服务条款的变更
    -   准备好备用提供商

### 13.3 社区/社会风险

**风险: 负面的社区反响**

-   **影响:** 中
-   **概率:** 低
-   **缓解措施:**
    -   发布前有高质量的 MVP
    -   积极响应反馈
    -   清晰的沟通
    -   设定合理的期望
    -   广泛进行 Beta 测试

**风险: 维护者燃尽**

-   **影响:** 高
-   **概率:** 中
-   **缓解措施:**
    -   清晰的贡献指南
    -   招募共同维护者
    -   尽可能自动化 (CI/CD)
    -   设定界限 (响应时间期望)
    -   需要时休息

**风险: 安全漏洞**

-   **影响:** 高
-   **概率:** 中
-   **缓解措施:**
    -   1.0 版本前进行安全审计
    -   依赖项扫描 (Dependabot)
    -   处处进行输入验证
    -   密钥管理的最佳实践
    -   负责任的披露政策
    -   Bug 赏金 (如果有资金)

---

## 14. 成本分析

### 14.1 开发成本

**时间投入:**

-   MVP 开发: 160 小时 (4 周 × 40小时)
-   Beta 测试: 80 小时 (2 周)
-   文档: 40 小时
-   社区支持: 每月 20 小时 (持续)

**机会成本:**

-   如果按 $50/小时 估值 = MVP 需 $14,000
-   持续: $1,000/月 用于支持

**基础设施成本:**

-   GitHub 仓库: 免费
-   域名 (可选): $12/年
-   云托管 (可选): $0-50/月

### 14.2 用户成本 (每次简报)

**最低配置:**

```
OpenAI GPT-4o-mini: $0.01 (文章筛选)
OpenAI GPT-4o-mini: $0.02 (脚本生成)
OpenAI TTS: $0.15 (音频生成)
总计: ~$0.18 / 简报
每月: ~$5.40 (30 次简报)
```

**高级配置:**

```
OpenAI GPT-4o: $0.05 (文章筛选)
OpenAI GPT-4o: $0.10 (脚本生成)
ElevenLabs TTS: $0.30 (音频生成)
总计: ~$0.45 / 简报
每月: ~$13.50 (30 次简报)
```

**免费配置:**

```
Ollama (本地 LLM): $0 (文章筛选)
Ollama (本地 LLM): $0 (脚本生成)
Piper TTS: $0 (音频生成)
总计: $0 / 简报
成本: 电费 + 硬件损耗 (~$0.01/简报)
```

### 14.3 盈亏平衡分析

**如果提供云服务 (可选):**

```
假设:
- 1000 活跃用户
- 30 次简报/用户/月
- 平均成本: $0.30/简报
- 每月成本: $9,000

所需定价:
- $10/用户/月 = $10,000 收入
- 毛利率: ~10% ($1,000/月)
- 盈亏平衡点: ~900 用户 @ $10/月
```

**结论:** 开源 + 自托管比云服务更具可持续性。

---

## 15. 未来愿景 (2-5 年)

### 15.1 产品演进

**第一年:**

-   稳定、广泛使用的 HA 集成
-   5,000+ 安装量
-   丰富的社区内容包生态
-   多平台支持 (Telegram, Discord)

**第二年:**

-   原生移动应用 (iOS/Android)
-   高级 AI 功能 (事实核查, 偏见检测)
-   语音助手集成 (自定义唤醒词)
-   类播客体验 (章节, 赞助商)

**第三年:**

-   企业功能 (团队简报, 分析)
-   为组织提供白标解决方案
-   用于第三方集成的 API
-   多模态 (文本 + 图片 + 视频摘要)

**第五年:**

-   成为个性化新闻的事实标准
-   与主要新闻出版商集成
-   AI 生成的调查性新闻
-   全球数百万的用户社区

### 15.2 潜在商业模式

**模式 1: 开源 + 云服务**

-   核心: 免费、开源、自托管
-   云: 可选的托管服务 ($10-20/月)
-   目标: 想要零配置的用户

**模式 2: 免费增值 SaaS**

-   基础版: 免费 (功能有限)
-   专业版: $10/月 (无限功能, 高级声音)
-   团队版: $50/月 (协作功能)

**模式 3: 企业许可**

-   个人版开源
-   组织版付费许可 (>10 用户)
-   自定义部署 + 支持合同

**模式 4: 应用市场**

-   免费核心平台
-   付费高级内容包 ($2-5/个)
-   与内容创作者收入分成
-   高级声音/功能

**推荐:** 从纯开源开始，如果需求存在，稍后添加可选的云服务。

---

## 16. 结论

### 16.1 项目总结

**Home Assistant 每日简报** 是智能家居时代一种革命性的新闻消费方式。通过结合：

-   AI 驱动的内容策展
-   听起来自然的音频生成
-   无缝的 Home Assistant 集成
-   隐私优先的本地处理

我们正在创造一个解决真实信息过载问题，同时尊重用户隐私和控制权的产品。

### 16.2 为何会成功

1.  **真实问题:** 信息过载是普遍且日益严重的问题
2.  **清晰的解决方案:** AI + 自动化 + 智能家居集成
3.  **技术可行性:** 所有组件都存在且已得到验证
4.  **市场时机:** AI 工具成熟，智能家居已成为主流
5.  **社区需求:** HA 用户渴望高级集成
6.  **开源优势:** 社区驱动的开发
7.  **低门槛:** 易于尝试，立竿见影的价值

### 16.3 行动号召

**致用户:**

-   试用 Beta 版
-   提供反馈
-   与朋友分享
-   贡献内容包

**致开发者:**

-   审查代码
-   提交 PR
-   创建集成
-   在平台上构建

**致社区:**

-   传播信息
-   编写教程
-   帮助新人
-   塑造路线图

---

## 附录

### A. 术语表

-   **简报 (Briefing):** 生成的每日新闻音频摘要
-   **内容包 (Content Pack):** 预先配置的 RSS 订阅源集合
-   **HACS:** Home Assistant 社区商店
-   **LLM:** 大型语言模型 (GPT, Claude, 等)
-   **RSS:** 真正简单的整合 (Web 订阅源格式)
-   **TTS:** 文本转语音
-   **RSSHub:** 开源 RSS 订阅源生成器

### B. 参考文献

-   Home Assistant 开发者文档: https://developers.home-assistant.io
-   HACS 文档: https://hacs.xyz
-   RSSHub 文档: https://docs.rsshub.app
-   OpenAI API 参考: https://platform.openai.com/docs
-   ElevenLabs API 文档: https://elevenlabs.io/docs

### C. 联系与支持

-   **GitHub:** https://github.com/Ryan-Guo123/ha-ai-daily-brief
-   **Discord:** [Discord 服务器链接]
-   **论坛:** https://community.home-assistant.io/t/daily-brief
-   **邮箱:** support@dailybrief.dev

---

## 文档变更日志

|版本|日期|变更内容|作者|
|---|---|---|---|
|1.0|2025-10-13|初始 PRD|Claude|

---

**文档结束**
