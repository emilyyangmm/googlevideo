# Skills 适配扣子平台分析报告

**分析时间**: 2026-03-14 08:32
**总技能数**: 25 个

---

## ✅ 完全适配扣子（12 个）

这些技能纯 API 调用或内容生成，无需本地环境：

| 技能 | 功能 | 适配度 | 备注 |
|------|------|--------|------|
| **stock-analysis** | 股票/加密货币分析 | ✅ 100% | Yahoo Finance API |
| **china-stock-analysis** | A 股价值投资分析 | ✅ 100% | akshare 数据源 |
| **bilibili-subtitle** | B 站字幕提取 | ✅ 100% | API 调用 |
| **bilibili-summarizer** | B 站内容总结 | ✅ 100% | API+AI 转录 |
| **douyin** | 抖音视频下载 | ✅ 100% | API 调用 |
| **douyin-hot-trend** | 抖音热榜数据 | ✅ 100% | API 调用 |
| **xiaohongshu-title** | 小红书标题生成 | ✅ 100% | AI 内容生成 |
| **xiaohongshu-content** | 小红书内容创作 | ✅ 100% | AI 内容生成 |
| **smart-image-generator** | 图片生成 | ✅ 100% | AI 绘图 API |
| **multi-search-engine** | 多搜索引擎 | ✅ 100% | 17 个搜索引擎 API |
| **xiaohongshu-note-analyzer** | 小红书笔记分析 | ✅ 100% | AI 内容分析 |
| **self-improving-agent** | 自我改进记忆 | ✅ 100% | 纯逻辑处理 |

---

## ⚠️ 部分适配（需配置）（3 个）

这些技能需要额外配置或远程服务：

| 技能 | 功能 | 适配度 | 配置要求 |
|------|------|--------|----------|
| **baoyu-post-to-wechat** | 公众号发布 | ⚠️ 70% | 需 API 凭证或远程 MCP |
| **wechat-mp-publisher** | 微信公众号发布 | ⚠️ 60% | 需远程 MCP 服务器 (130.211.249.194) |
| **xiaohongshu-mcp-skill** | 小红书 MCP | ⚠️ 50% | 需本地 MCP 服务 (localhost:18060) |

---

## ❌ 不适配扣子（本地依赖）（4 个）

这些技能依赖本地环境，无法迁移到扣子：

| 技能 | 功能 | 原因 |
|------|------|------|
| **browser-automation** | 浏览器自动化 | ❌ 需要本地 Playwright/Chrome |
| **ffmpeg-video-editor** | 视频编辑 | ❌ 需要本地 FFmpeg |
| **xhs-auto-publisher** | 小红书自动发布 | ❌ 需要浏览器自动化 |
| **xhs-note-creator** | 小红书笔记创作 | ❌ 需要本地图片生成 |

---

## 📊 统计

```
总技能数：25 个
✅ 完全适配：12 个 (48%)
⚠️ 部分适配：3 个 (12%)
❌ 不适配：4 个 (16%)
📝 待分析：6 个 (24%)
```

---

## 🎯 推荐优先迁移到扣子

**第一梯队（高价值 + 高适配）**：
1. stock-analysis - 股票分析（实用性强）
2. china-stock-analysis - A 股分析（本土化）
3. xiaohongshu-title - 标题生成（爆款工具）
4. multi-search-engine - 多引擎搜索（通用工具）

**第二梯队（内容创作类）**：
1. bilibili-subtitle - B 站字幕
2. douyin-hot-trend - 抖音热榜
3. xiaohongshu-content - 内容创作
4. smart-image-generator - 图片生成

---

## 📝 下一步

1. **优先迁移** 第一梯队 4 个技能到扣子
2. **配置远程服务** 解决公众号发布技能
3. **放弃迁移** 本地依赖类技能

---

*更新时间：2026-03-14 08:32*
