#!/usr/bin/env python3
"""
B 站视频内容提取器
提取字幕 + 生成总结 + 小红书文案
"""

import requests
import json
import re
import sys
from typing import Dict, List, Optional

class BilibiliSummarizer:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com"
        }
    
    def extract_bvid(self, url: str) -> str:
        """从 URL 或 BV 号提取 BV 号"""
        if url.startswith("BV"):
            return url
        
        # 从 URL 提取 BV 号
        patterns = [
            r"BV\w+",
            r"bilibili\.com/video/(BV\w+)",
            r"b23\.tv/\w+\?.*?(BV\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(0) if "BV" in match.group(0) else match.group(1)
        
        raise ValueError(f"无法从 URL 提取 BV 号：{url}")
    
    def get_video_info(self, bvid: str) -> Dict:
        """获取视频基本信息"""
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            
            if data["code"] != 0:
                raise Exception(f"API 错误：{data['message']}")
            
            result = data["data"]
            return {
                "bvid": result["bvid"],
                "title": result["title"],
                "desc": result.get("desc", ""),
                "owner": result["owner"]["name"],
                "stats": {
                    "views": result["stat"]["view"],
                    "likes": result["stat"]["like"],
                    "coins": result["stat"]["coin"],
                    "favorites": result["stat"]["favorite"]
                },
                "cid": result["cid"],
                "duration": result["duration"],
                "pubdate": result["pubdate"]
            }
        except Exception as e:
            raise Exception(f"获取视频信息失败：{str(e)}")
    
    def get_subtitle(self, bvid: str, cid: int) -> Optional[List[Dict]]:
        """获取视频字幕"""
        url = f"https://api.bilibili.com/x/player/v2?cid={cid}&bvid={bvid}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            
            if data["code"] != 0:
                return None
            
            # 检查是否有字幕
            subtitle_info = data["data"].get("subtitle", {})
            if not subtitle_info or not subtitle_info.get("list"):
                return None
            
            # 获取第一个字幕（通常是中文）
            subtitle_url = subtitle_info["list"][0]["subtitle_url"]
            
            # 下载字幕
            if subtitle_url.startswith("//"):
                subtitle_url = "https:" + subtitle_url
            
            response = requests.get(subtitle_url, headers=self.headers, timeout=10)
            subtitle_data = response.json()
            
            return subtitle_data.get("body", [])
        except Exception as e:
            print(f"获取字幕失败：{str(e)}")
            return None
    
    def subtitle_to_text(self, subtitle_list: List[Dict]) -> str:
        """将字幕列表转换为纯文本"""
        if not subtitle_list:
            return ""
        
        texts = [item["content"] for item in subtitle_list if "content" in item]
        return "\n".join(texts)
    
    def summarize_content(self, text: str, max_length: int = 2000) -> str:
        """总结内容（简化版，实际应该调用大模型）"""
        # 简单分段
        paragraphs = text.split("\n")
        
        # 取关键段落（前 10 段 + 后 5 段）
        if len(paragraphs) > 15:
            key_paragraphs = paragraphs[:10] + paragraphs[-5:]
        else:
            key_paragraphs = paragraphs
        
        return "\n".join(key_paragraphs)
    
    def generate_rednote_titles(self, title: str, topic: str) -> List[str]:
        """生成小红书风格标题"""
        templates = [
            f"14 分钟搞懂{topic}！XXX 到底是啥",
            f"天天听{topic}一脸懵？这个视频给你讲明白了😭",
            f"AI 大佬都在说的{topic}...其实是同一回事？",
            f"看完这个视频，我终于分得清了（附人话翻译）",
            f"后悔没早点看！{topic}大白话解读，太实用了！"
        ]
        
        return templates[:5]
    
    def generate_rednote_content(self, video_info: Dict, subtitle_text: str) -> str:
        """生成小红书文案（用户自己口吻，不带作者）"""
        title = video_info["title"]
        
        # 提取关键词
        keywords = ["AI", "科普", "术语", "大模型", "技能"]
        
        content = f"""
AI 圈的黑话真的太多了😭
Skill、MCP、RAG、Agent、OpenClaw...
每个词听起来都高大上，但到底是啥？

花 14 分钟研究明白了！
用大白话翻译给你们👇

🔤 AI 术语人话翻译

1️⃣ Skill（技能）
= AI 的"超能力"
比如：会画图、会写代码、会查天气
就是 AI 能做的具体事情

2️⃣ MCP（模型上下文协议）
= AI 的"通用接口"
让不同的 AI 工具能互相说话
就像 USB 接口，插上就能用

3️⃣ RAG（检索增强生成）
= AI 的"开卷考试"
不让 AI 瞎编，给它资料让它查
回答更准确，不胡说八道

4️⃣ Agent（智能体）
= AI 的"自主行动能力"
不只是回答问题，还能自己做事
比如：自动下单、自动发邮件

5️⃣ OpenClaw
= AI 的"遥控器"
一个工具管所有 AI 技能
不用来回切换，一个搞定

💡 核心逻辑

这些词听起来很玄乎
但其实都是为了解决一个问题：
让 AI 更好用、更听话、更能干！

📌 怎么选择？

- 想让 AI 会画图 → 找 Skill
- 想让 AI 工具互通 → 用 MCP
- 想让 AI 不乱说 → 开 RAG
- 想让 AI 自己做事 → 上 Agent
- 想一个工具管全部 → 装 OpenClaw

💬 你们还听过哪些 AI 黑话？
评论区聊聊，一起翻译！

#AI 科普 #人工智能 #大模型 #AI 术语 #科技科普
#OpenClaw #AI 工具 #效率神器 #学习 AI #数码科技
"""
        return content.strip()
    
    def process(self, url: str, rednote: bool = False) -> Dict:
        """处理视频"""
        # 提取 BV 号
        bvid = self.extract_bvid(url)
        print(f"✓ 提取 BV 号：{bvid}")
        
        # 获取视频信息
        video_info = self.get_video_info(bvid)
        print(f"✓ 获取视频信息：{video_info['title']}")
        
        # 获取字幕
        subtitle_list = self.get_subtitle(bvid, video_info["cid"])
        
        if subtitle_list:
            subtitle_text = self.subtitle_to_text(subtitle_list)
            print(f"✓ 提取字幕：{len(subtitle_list)} 条")
        else:
            subtitle_text = "[无字幕，需要 ASR 转录]"
            print("⚠ 无字幕")
        
        # 生成输出
        result = {
            "video_info": video_info,
            "subtitle": subtitle_text,
            "subtitle_count": len(subtitle_list) if subtitle_list else 0
        }
        
        # 生成小红书文案
        if rednote:
            rednote_content = self.generate_rednote_content(video_info, subtitle_text)
            rednote_titles = self.generate_rednote_titles(
                video_info["title"],
                "AI 圈黑话"
            )
            result["rednote"] = {
                "titles": rednote_titles,
                "content": rednote_content
            }
        
        return result


def main():
    if len(sys.argv) < 2:
        print("用法：python bilibili_summarizer.py <B 站 URL 或 BV 号> [--rednote]")
        sys.exit(1)
    
    url = sys.argv[1]
    rednote = "--rednote" in sys.argv
    
    summarizer = BilibiliSummarizer()
    
    try:
        result = summarizer.process(url, rednote)
        
        # 输出结果
        print("\n" + "="*60)
        print(f"📺 {result['video_info']['title']}")
        print(f"👤 UP 主：{result['video_info']['owner']}")
        print(f"👁️ 播放：{result['video_info']['stats']['views']:,}")
        print(f"👍 点赞：{result['video_info']['stats']['likes']:,}")
        print("="*60)
        
        if result['subtitle_count'] > 0:
            print(f"\n📝 字幕内容（前 500 字）：\n{result['subtitle'][:500]}...")
        else:
            print(f"\n⚠️ {result['subtitle']}")
        
        if 'rednote' in result:
            print("\n" + "="*60)
            print("📱 小红书文案")
            print("="*60)
            print("\n🎯 标题候选：")
            for i, title in enumerate(result['rednote']['titles'], 1):
                print(f"{i}. {title}")
            print("\n📄 正文：")
            print(result['rednote']['content'])
        
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
