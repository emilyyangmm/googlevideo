# 🎬 AI 视频生成器 - Google Veo

基于 Google Cloud Vertex AI Veo 3.1 模型的视频生成 Web 应用。

## 🚀 部署到 Zeabur

1. 登录 [Zeabur](https://zeabur.com)
2. Deploy New Service → Deploy from GitHub
3. 选择此仓库
4. 配置环境变量：
   - `GOOGLE_CLOUD_PROJECT=867714362426`
   - `GOOGLE_APPLICATION_CREDENTIALS`（服务账号 JSON 内容）
5. Deploy!

## 💰 成本

- Veo 3.1 Fast: 约 $0.06/秒
- 5 秒视频约 $0.30
- 使用 Google Cloud 300 美金免费额度

## 📁 文件结构

- `index.html` - 前端页面
- `app.py` - Flask 后端
- `requirements.txt` - Python 依赖

---

Made with ❤️
