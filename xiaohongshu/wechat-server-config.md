# 微信公众号配置

## 远程 MCP 服务器

**Google Cloud 服务器 IP**: `130.211.249.194`

**用途**: 解决家用宽带 IP 变动问题，用于微信公众号 API 调用

**配置时间**: 2026-03-12 前后

**微信公众号凭证**:
- AppID: `wx728f52aa472fcb3b`
- AppSecret: 已配置在 `~/.baoyu-skills/.env`

## 发布注意事项

1. **图片必须处理** - 文章中的图片需要：
   - 使用网络 URL（微信会自动抓取）
   - 或先上传到微信服务器获取 media_id

2. **封面图必需** - API 发布时必须提供封面图

3. **IP 白名单** - 公众号后台需要添加服务器 IP `130.211.249.194`

## 常用命令

```bash
# API 方式发布（推荐）
npx baoyu-post-to-wechat --markdown article.md --cover cover.jpg --submit

# 浏览器方式发布
npx baoyu-post-to-wechat --browser --markdown article.md
```

---
*更新时间：2026-03-14 08:24*
