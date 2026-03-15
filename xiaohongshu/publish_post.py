#!/usr/bin/env python3
"""
小红书自动发布脚本
使用 xiaohongshu-mcp 技能
"""

import subprocess
import sys
import os

# 小红书文案
title = "0编程基础做AI网站，这3个坑让我多花了1周😭"

content = """兄弟姐妹们，接着聊聊之前做网站踩的坑
今天分享3个让我多花了1周的坑
希望能帮你们少走弯路💡

🚨 坑1：免费部署平台的"隐形限制"

【我踩的坑】
一开始用Vercel，部署成功很开心
结果第二天访问，显示"Invalid URL"
查了半天，发现免费版有域名限制
换replit后又遇到IP池耗尽
高峰期直接502错误，railway也是各种水土不服

【解决方案】
✅ 直接选择Zeabur，每个月5美元免费额度，界面简单 ，部署日志清晰可见，还可以让zeabur机器人帮你判断问题

【省下的时间】3天→1天

🚨 坑2：API认证token过期

【我踩的坑】
豆包API接入后，运行3小时全挂
日志显示认证失败
原来access_token只有2小时有效期
没做自动刷新机制

【解决方案】
✅ 用异步调用框架（asyncio）
✅ 写AuthManager自动刷新token
✅ 加错误重试机制，失败自动重连

【代码核心逻辑】
if token_expired():
refresh_token()
retry_request()

【省下的时间】2天→半天

🚨 坑3：本地图片后端收不到

【我踩的坑】
用户选了本地图片，前端显示正常
传给后端API，后端说收不到文件
查了半天，原来本地URI(file://)后端访问不了
必须上传到对象存储

【解决方案】
✅ 前端判断：本地图片先上传到OSS
✅ 获取签名URL后再传给后端
✅ 后端直接用URL处理

【流程图】
用户选图 → 前端上传到OSS → 获取URL → 传给后端 → 后端处理

【省下的时间】2天→半天

💡 总结：避开这3个坑，我省了7天

兄弟姐妹们，你们做项目时踩过什么坑？
评论区聊聊，我帮你看看怎么解决👇

#AI生图 #网站开发 #踩坑实录 #从0到1 #地产人转型 #避坑指南"""

def publish_text_only():
    """发布纯文字笔记（测试）"""
    print("📝 发布纯文字笔记...")
    
    # 使用 xiaohongshu-mcp 发布
    cmd = [
        "python3", 
        "~/.openclaw/skills/xiaohongshu-mcp/scripts/xhs_client.py",
        "publish",
        title,
        content,
        ""  # 无图片
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(result.stdout)
    print(result.stderr)
    
def publish_with_images(image_paths):
    """发布带图片的笔记"""
    print(f"📝 发布带图片笔记，图片: {image_paths}")
    
    # 使用 xiaohongshu-mcp 发布
    cmd = [
        "python3", 
        "~/.openclaw/skills/xiaohongshu-mcp/scripts/xhs_client.py",
        "publish",
        title,
        content,
        ",".join(image_paths)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(result.stdout)
    print(result.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果有图片路径参数，发布带图片的
        image_paths = sys.argv[1:]
        publish_with_images(image_paths)
    else:
        # 否则发布纯文字
        print("💡 使用方式:")
        print("  python3 publish_post.py              # 发布纯文字")
        print("  python3 publish_post.py img1.png img2.png  # 发布带图片")
        print()
        print("📝 准备发布纯文字笔记...")
        publish_text_only()
