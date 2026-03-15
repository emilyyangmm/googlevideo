---
name: bilibili-summarizer
description: B 站视频内容一键提取 + 总结。支持字幕提取、AI 转录、内容摘要、小红书文案生成。
emoji: 📺
dependency:
  python:
    - requests>=2.28.0
    - beautifulsoup4>=4.11.0
---

# B 站视频内容提取器

**一键完成：** 视频 URL → 字幕提取 → 内容总结 → 小红书文案

## 使用场景

- 用户发送 B 站视频链接，需要快速了解内容
- 需要将视频内容转化为文字笔记
- 需要将视频内容改编为小红书文案
- 需要提取视频中的关键信息/知识点

## 工作流程

### 第 1 步：提取视频信息

从 B 站视频 URL 或 BV 号获取：
- 视频标题
- UP 主
- 播放量/点赞数
- 视频简介
- 字幕列表

**API 端点：**
```
https://api.bilibili.com/x/web-interface/view?bvid={BV 号}
https://api.bilibili.com/x/player/wbi/v2?bvid={BV 号}&cid={CID}
```

### 第 2 步：提取字幕

**优先级：**
1. **CC 字幕** - UP 主上传的字幕（最准确）
2. **AI 生成字幕** - B 站自动生成的字幕
3. **ASR 转录** - 如果前两者都没有，调用阿里云 ASR

**字幕 API：**
```
https://api.bilibili.com/x/player/v2?cid={CID}&bvid={BV 号}
```

### 第 3 步：内容总结

使用大模型对字幕内容进行总结：

**输出结构：**
```markdown
# 视频标题

## 📌 核心观点
- 观点 1
- 观点 2
- 观点 3

## 📝 详细内容
分章节/分知识点总结

## 💡 金句/亮点
- 引人深思的原话
- 有趣的比喻

## 🔗 相关信息
- UP 主：xxx
- 播放：xxx
- 原视频：URL
```

### 第 4 步：小红书文案（可选）

根据视频内容生成小红书风格的文案：

**文案结构：**
- 爆款标题（5 个候选）
- 正文（带 emoji）
- Tags

## 使用方式

**用户输入：**
```
https://www.bilibili.com/video/BV1ojfDBSEPv
```

**输出：**
1. 视频基本信息
2. 完整字幕/转录稿
3. 内容总结
4. 小红书文案（可选）

## 命令行调用

```bash
# 基本使用
python scripts/bilibili_summarizer.py "BV1ojfDBSEPv"

# 生成小红书文案
python scripts/bilibili_summarizer.py "BV1xxx" --rednote

# 仅提取字幕
python scripts/bilibili_summarizer.py "BV1xxx" --subtitle-only

# 输出到文件
python scripts/bilibili_summarizer.py "BV1xxx" -o output.md
```

## API 配置

可选配置 API Key 增强功能：

```bash
# 阿里云 ASR（无字幕时自动转录）
export DASHSCOPE_API_KEY="your_key"

# 大模型总结
export DASHSCOPE_API_KEY="your_key"
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 视频不存在 | URL 错误或视频已删除 | 检查 URL |
| 无字幕 | UP 主未上传字幕 | 自动触发 ASR 转录 |
| API 限流 | 请求过于频繁 | 稍后重试 |
| 需要登录 | 部分内容需要登录 | 配置 Cookie |

## 输出示例

### 输入
```
https://www.bilibili.com/video/BV1ojfDBSEPv
```

### 输出
```markdown
# 【闪客】一口气拆穿 Skill/MCP/RAG/Agent/OpenClaw 底层逻辑

**UP 主**: 飞天闪客  
**播放**: 52.8 万  
**时长**: 14:46

---

## 📌 核心观点

1. AI 术语都是为了解决同一个问题：让 AI 更好用
2. Skill = AI 的超能力
3. MCP = AI 的通用接口
4. RAG = AI 的开卷考试
5. Agent = AI 的自主行动能力
6. OpenClaw = AI 的遥控器

## 📝 详细内容

### 1. Skill（技能）
- 定义：AI 能做的具体事情
- 例子：画图、写代码、查天气
- 人话：AI 的"超能力"

### 2. MCP（模型上下文协议）
- 定义：让不同 AI 工具互相通信
- 例子：USB 接口，插上就能用
- 人话：AI 的"通用接口"

...（更多内容）

## 💡 金句
- "这些词听起来很玄乎，但其实都是为了解决一个问题"

## 📱 小红书文案

**标题候选：**
1. "14 分钟搞懂 AI 圈黑话！Skill/MCP/RAG/Agent 到底是啥"
2. "天天听 AI 术语一脸懵？这个视频给你讲明白了😭"
...

**正文：**
AI 圈的黑话真的太多了😭
Skill、MCP、RAG、Agent、OpenClaw...
每个词听起来都高大上，但到底是啥？
...
```

---

**版本**: v1.0  
**作者**: 小爪 🦞
