# GitHub发布和HACS提交指南

本指南将帮助您将Daily Brief发布到GitHub并提交到HACS。

## 📋 前提条件

- GitHub账号
- Git已安装并配置
- 项目代码已准备就绪

## 🚀 第一步：创建GitHub仓库

### 1. 在GitHub上创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息:
   - **仓库名**: `ha-ai-daily-brief`
   - **描述**: `AI-powered daily news briefing for Home Assistant`
   - **可见性**: Public (HACS要求)
   - **不要**初始化README、.gitignore或LICENSE（我们已经有了）

3. 点击 "Create repository"

### 2. 推送代码到GitHub

在项目目录中执行:

```bash
cd /Users/ryan/AI/ha-ai-daily-brief

# 初始化Git仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/Ryan-Guo123/ha-ai-daily-brief.git

# 添加所有文件
git add .

# 提交
git commit -m "feat: 初始版本 - AI驱动的每日新闻简报集成"

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 🏷️ 第二步：创建首个版本

### 1. 创建Git Tag

```bash
# 创建v0.1.0标签
git tag -a v0.1.0 -m "Release v0.1.0 - 首个正式版本"

# 推送标签
git push origin v0.1.0
```

### 2. 在GitHub上创建Release

1. 访问你的仓库: `https://github.com/Ryan-Guo123/ha-ai-daily-brief`
2. 点击右侧的 "Releases"
3. 点击 "Create a new release"
4. 填写发布信息:

**Tag version**: `v0.1.0`

**Release title**: `Daily Brief v0.1.0 - 首个正式版本 🎉`

**Description**:

```markdown
## 🎉 首次发布！

Daily Brief for Home Assistant - AI驱动的个性化每日新闻简报

### ✨ 主要功能

- 🤖 **AI智能选择** - 使用GPT-4o-mini智能筛选重要新闻
- 🎙️ **自然语音** - OpenAI TTS高质量语音合成
- 📚 **丰富内容** - 7个预配置内容包（科技、新闻、商业等）
- 🎯 **个性化** - 根据您的兴趣和反馈优化
- 🔒 **隐私优先** - 所有数据本地存储
- 🌍 **多语言** - 支持中文、英文

### 📦 安装方式

#### 通过HACS（推荐）
1. 打开HACS
2. 进入"集成"
3. 点击右上角菜单 → "自定义仓库"
4. 添加: `https://github.com/Ryan-Guo123/ha-ai-daily-brief`
5. 类别: "Integration"
6. 搜索并安装"Daily Brief"

#### 手动安装
1. 下载 `daily_brief.zip`
2. 解压到 `config/custom_components/`
3. 重启Home Assistant

### 📖 快速开始

```yaml
# 生成简报
service: daily_brief.generate
data:
  briefing_type: morning

# 播放简报
service: daily_brief.play
data:
  media_player: media_player.bedroom_speaker
```

### 💰 费用

- **经济版**: GPT-4o-mini + OpenAI TTS ≈ ¥1.19/简报
- **高级版**: GPT-4o + ElevenLabs ≈ ¥3.15/简报
- **免费版**: Ollama + Piper = ¥0

### 📋 要求

- Home Assistant 2024.10.0+
- Python 3.11+
- OpenAI API密钥
- FFmpeg

### 📚 文档

- [README (中文)](README.zh-CN.md)
- [README (English)](README.md)
- [开发文档](DEVELOPMENT.md)
- [贡献指南](CONTRIBUTING.md)

### 🐛 已知问题

- 首次生成需要3-5分钟
- 需要系统安装FFmpeg

### 🙏 致谢

感谢所有测试用户的反馈！

---

**完整更新日志**: [CHANGELOG.md](CHANGELOG.md)
```

5. 勾选 "Set as the latest release"
6. 点击 "Publish release"

**GitHub Actions会自动创建并上传 `daily_brief.zip` 文件**

## 📦 第三步：提交到HACS

### 1. 准备工作

确保以下文件存在且正确：

- ✅ `hacs.json` - HACS配置文件
- ✅ `info.md` - HACS展示文档
- ✅ `README.md` - 项目说明
- ✅ `manifest.json` - 集成清单
- ✅ 至少一个release（v0.1.0）

### 2. 提交到HACS默认仓库

#### 方式一：通过GitHub（推荐）

1. Fork HACS仓库: https://github.com/hacs/default
2. 编辑文件 `integration`
3. 按字母顺序添加你的仓库:

```json
{
  "Ryan-Guo123/ha-ai-daily-brief": {
    "name": "Daily Brief"
  }
}
```

4. 提交Pull Request
5. PR标题: `Add Ryan-Guo123/ha-ai-daily-brief`
6. 等待HACS团队审核（通常1-3天）

#### 方式二：填写表单

访问: https://github.com/hacs/default/issues/new/choose

选择 "Integration" 并填写表单。

### 3. 验证HACS要求

HACS要求检查清单：

- ✅ 仓库是public
- ✅ 有至少一个release
- ✅ 有`hacs.json`文件
- ✅ 有`info.md`文件
- ✅ `manifest.json`中的`domain`与仓库中的目录名一致
- ✅ 代码在`custom_components/<domain>/`目录下
- ✅ 遵循Home Assistant集成标准

## ✅ 验证安装

### 本地测试

1. 在Home Assistant中安装HACS（如果还没有）
2. 添加自定义仓库:
   - HACS → 集成 → 右上角菜单 → 自定义仓库
   - URL: `https://github.com/Ryan-Guo123/ha-ai-daily-brief`
   - 类别: Integration
3. 搜索并安装"Daily Brief"
4. 重启Home Assistant
5. 添加集成并测试

### GitHub Actions检查

访问仓库的Actions页面，确保：
- ✅ Validate工作流通过
- ✅ Release工作流成功创建ZIP

## 📢 推广和宣传

### 1. Home Assistant社区论坛

创建主题: https://community.home-assistant.io/c/third-party/9

标题示例:
```
[New Integration] Daily Brief - AI-powered news briefing
```

内容包含:
- 功能介绍
- 安装指南
- 截图/视频
- GitHub链接

### 2. Reddit

发布到:
- r/homeassistant
- r/homeautomation

### 3. 社交媒体

- Twitter/X
- 微信公众号
- 知乎
- B站

## 🔄 后续更新

### 发布新版本

1. 更新代码
2. 更新版本号:
   - `manifest.json` 中的 `version`
   - `const.py` 中的版本常量（如果有）
3. 更新 `CHANGELOG.md`
4. 提交代码
5. 创建新tag:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```
6. 在GitHub上创建新Release
7. HACS会自动检测新版本

## 🆘 常见问题

### Q: HACS验证失败？

检查：
- `hacs.json`格式是否正确
- `manifest.json`中的domain是否与目录名一致
- 是否有至少一个release

### Q: GitHub Actions失败？

查看Actions日志，常见原因：
- 权限问题
- 文件路径错误
- 依赖缺失

### Q: 如何处理用户反馈？

- 在GitHub Issues中跟踪
- 及时回复
- 创建milestone管理版本
- 使用labels分类问题

## 📝 检查清单

发布前最终检查：

- [ ] 所有代码已提交并推送
- [ ] 版本号已更新
- [ ] CHANGELOG.md已更新
- [ ] README.md完整且准确
- [ ] 创建了git tag
- [ ] GitHub Release已发布
- [ ] HACS PR已提交
- [ ] 本地测试通过
- [ ] 文档齐全

## 🎉 完成！

恭喜！您的集成现在可以通过HACS安装了！

---

**需要帮助？**
- [HACS文档](https://hacs.xyz/)
- [Home Assistant开发者文档](https://developers.home-assistant.io/)
- [GitHub Actions文档](https://docs.github.com/actions)
