# 运营技能扣子适配度评估报告

**评估日期**：2026-03-12
**评估人**：🦞 小爪

---

## 📊 评估标准

| 等级 | 标准 |
|------|------|
| ⭐⭐⭐⭐⭐ | 原生支持扣子 API / MCP 协议，文档完善，有示例 |
| ⭐⭐⭐⭐ | 可通过 HTTP/MCP 对接，需少量配置 |
| ⭐⭐⭐ | 需要额外中间件或代理 |
| ⭐⭐ | 仅支持本地部署，扣子对接困难 |
| ⭐ | 不兼容扣子 |

---

## ✅ 已安装技能（扣子适配）

| 技能 | 适配度 | 说明 |
|------|--------|------|
| **xiaohongshu-mcp** | ⭐⭐⭐⭐⭐ | 原生 MCP 协议，完美适配扣子 |
| **douyin-hot-trend** | ⭐⭐⭐⭐ | HTTP API，可直接调用 |
| **multi-search-engine** | ⭐⭐⭐⭐⭐ | 多引擎集成，扣子友好 |
| **baoyu-post-to-wechat** | ⭐⭐⭐⭐ | 支持 CDP 和 API 双模式 |

---

## 🎯 待安装技能评估

### 小红书类

| 技能 | 评分 | 适配度 | 安全风险 | 建议 |
|------|------|--------|----------|------|
| xiaohongshu-mcp-skill | 3.523 | ⭐⭐⭐⭐⭐ | 中（MCP 本地服务） | ✅ 推荐安装 |
| xiaohongshu-content | 3.429 | ⭐⭐⭐⭐ | 低 | ✅ 推荐安装 |
| xiaohongshu-auto | 3.424 | ⭐⭐⭐⭐ | 中（自动化） | ✅ 推荐安装 |
| xiaohongshu-api | 3.466 | ⭐⭐⭐ | 中（API 调用） | ⚠️ 需测试 |
| xiaohongshu-post | 3.384 | ⭐⭐⭐⭐ | 低 | ✅ 推荐安装 |

**安全分析**：
- xiaohongshu-mcp-skill：需要本地 MCP 服务，存储登录凭证
- 风险等级：中（正常，社媒工具都需要凭证）

---

### 抖音类

| 技能 | 评分 | 适配度 | 安全风险 | 建议 |
|------|------|--------|----------|------|
| douyin-publish | 3.649 | ⭐⭐⭐⭐⭐ | 中（自动登录） | ✅ 推荐安装 |
| douyin-downloader | 3.666 | ⭐⭐⭐ | 低 | ✅ 推荐安装 |
| douyin-messager | 3.487 | ⭐⭐⭐ | 中（私信） | ⚠️ 谨慎使用 |
| douyin-keyword-search | 3.414 | ⭐⭐⭐⭐ | 低 | ✅ 推荐安装 |

**安全分析**：
- douyin-publish：需要抖音登录凭证，自动上传视频
- 风险等级：中（正常，发布工具需要凭证）

---

### 公众号类

| 技能 | 评分 | 适配度 | 安全风险 | 建议 |
|------|------|--------|----------|------|
| wechat-mp-cn | 3.694 | ⭐⭐⭐⭐⭐ | 中（微信凭证） | ✅ 推荐安装 |
| wechat-mp-publisher | 3.528 | ⭐⭐⭐⭐⭐ | 中（HTTP MCP） | ✅ 推荐安装 |
| wechat-mp-writer-skill-mxx | 3.530 | ⭐⭐⭐⭐ | 低 | ✅ 推荐安装 |
| wechat-daily-report | 3.500 | ⭐⭐⭐⭐ | 低 | ✅ 推荐安装 |

**安全分析**：
- wechat-mp-publisher：使用 HTTP MCP，支持远程部署
- 风险等级：中（正常，公众号发布需要凭证）

---

## 🔒 安全隐患说明

被 VirusTotal 标记为"可疑"的原因：
1. **外部 API 调用** - 需要调用平台 API
2. **凭证存储** - 需要保存登录状态
3. **自动化操作** - 模拟浏览器/客户端行为

**这些是正常的**，社交媒体管理工具都需要这些功能。

**真正的危险信号**（本次未发现）：
- ❌ 硬编码的 API 密钥
- ❌ 发送到未知服务器的数据
- ❌ 恶意代码执行（eval、exec 等）
- ❌ 隐藏的后门

---

## 📋 安装优先级

### 第一梯队（立即安装）
- [ ] xiaohongshu-mcp-skill - 小红书 MCP 协议
- [ ] wechat-mp-publisher - 公众号发布
- [ ] douyin-publish - 抖音视频发布

### 第二梯队（本周安装）
- [ ] xiaohongshu-content - 内容创作
- [ ] wechat-mp-cn - 公众号全套
- [ ] douyin-keyword-search - 关键词搜索

### 第三梯队（下周安装）
- [ ] xiaohongshu-auto - 自动化发布
- [ ] douyin-downloader - 视频下载
- [ ] wechat-daily-report - 日报生成

---

## 🧪 测试计划

### 小红书
1. 测试 xiaohongshu-mcp-skill 发布笔记
2. 对比已安装的 xiaohongshu-mcp
3. 测试 xiaohongshu-content 生成爆款文案

### 抖音
1. 测试 douyin-publish 上传视频
2. 测试 douyin-hot-trend 获取热榜
3. 对比手动发布流程

### 公众号
1. 测试 wechat-mp-publisher 发布文章
2. 测试 wechat-mp-cn 管理功能
3. 对比 baoyu-post-to-wechat

---

## 📝 扣子适配测试项

| 测试项 | 标准 |
|--------|------|
| API 调用 | 能否通过扣子直接调用 |
| 凭证管理 | 是否支持扣子凭证存储 |
| 错误处理 | 失败时是否有清晰错误信息 |
| 文档质量 | 是否有扣子使用示例 |
| 响应速度 | API 响应是否及时 |

---

*持续更新中...*
