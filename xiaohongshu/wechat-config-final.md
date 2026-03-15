# 微信公众号配置完成

**日期**：2026-03-12 21:30

---

## ✅ 配置信息

| 项目 | 值 |
|------|-----|
| AppID | wx728f52aa472fcb3b |
| 原始 ID | gh_70c0bf383853 |
| AppSecret | 21682a59b2d6bdd1e3f22540d54c3ccc |

---

## ✅ GCP 服务器

| 项目 | 值 |
|------|-----|
| 外网 IP | **34.81.184.105** |
| 区域 | asia-east1-b（台湾） |
| 机型 | e2-small（2 核 2G） |
| 服务 | wenyan-mcp (Docker) |
| 端口 | 3000 |

---

## ⚠️ 待完成：IP 白名单

**需要添加到公众号后台**：
- **34.81.184.105**（GCP 服务器 IP）✅ **杨哥已添加**

**当前出口 IP**（不需要了）：
- 112.97.192.249（本地网络出口）

---

## 📋 下一步

1. ✅ 杨哥添加 GCP IP 到白名单
2. ⏳ 测试 API 连接
3. ⏳ 测试发布文章

---

## 🧪 测试命令

```bash
# 测试服务器 MCP 服务
curl http://34.81.184.105:3000/sse

# 测试微信 API（通过服务器）
# 在服务器上执行：
ssh root@34.81.184.105 "curl -s 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx728f52aa472fcb3b&secret=21682a59b2d6bdd1e3f22540d54c3ccc'"
```

---

*更新时间：2026-03-12 21:30*
