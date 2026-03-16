#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 视频生成 Web 应用后端
使用 Vertex AI SDK 调用 Veo 模型
"""

import os
import json
import tempfile
from flask import Flask, render_template, request, jsonify
import vertexai
from vertexai import vision_models
from google.oauth2 import service_account

app = Flask(__name__)

# 初始化 Vertex AI 配置
def init_vertex_ai():
    """初始化 Vertex AI 客户端"""
    try:
        # 从 Render 的环境变量中获取项目 ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        # 检查是否有服务账号 JSON 文件路径
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        credentials = None
        if credentials_path and os.path.exists(credentials_path):
            # ✅ 正确：先加载凭证对象
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            print(f"✅ 已加载服务账号文件：{credentials_path}")
        
        # 初始化 SDK
        vertexai.init(
            project=project_id,
            location=location,
            credentials=credentials
        )
        return True
        
    except Exception as e:
        print(f"❌ Vertex AI 初始化失败：{str(e)}")
        return False

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 视频生成 API 路由
@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        # 获取请求中的提示词
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': '请提供提示词'}), 400
        
        print(f"🎬 开始生成视频，提示词：{prompt}")
        
        # 初始化 Vertex AI
        if not init_vertex_ai():
            return jsonify({
                'success': False, 
                'error': 'Vertex AI 初始化失败，请检查服务账号配置'
            }), 500
        
        # 加载 Veo 模型（根据官方文档：https://cloud.google.com/vertex-ai/generative-ai/docs/models/veo-models）
        model = None
        # 按优先级尝试官方支持的模型 ID
        for model_id in [
            "veo-3.1-generate-001",      # Veo 3.1 正式版
            "veo-3.1-fast-generate-001", # Veo 3.1 快速版
            "veo-3.0-generate-001",      # Veo 3.0 正式版
            "veo-3.0-fast-generate-001", # Veo 3.0 快速版
            "veo-2.0-generate-001",      # Veo 2.0
        ]:
            try:
                model = vision_models.VideoGenerationModel.from_pretrained(model_id)
                print(f"✅ Veo 模型加载成功：{model_id}")
                break
            except Exception as e:
                print(f"⚠️ 模型 {model_id} 加载失败：{str(e)}")
                continue
        
        if not model:
            return jsonify({
                'success': False,
                'error': 'Veo 模型加载失败，请确认模型名称是否正确。请查看 Vertex AI 文档获取最新模型 ID。'
            }), 500
        
        # 生成视频
        try:
            print("⏳ 正在生成视频，这可能需要几分钟...")
            
            # 生成视频（根据官方文档设置参数）
            # 文档：https://cloud.google.com/vertex-ai/generative-ai/docs/models/veo-models
            generated_video = model.generate_video(
                prompt=prompt,
                duration_seconds=8,  # Veo 3: 4/6/8 秒，Veo 2: 5-8 秒
                aspect_ratio="16:9",
                person_generation="allow_adult",  # 默认允许生成人物
                generate_audio=False,  # Veo 3 模型必需参数
                resolution="720p",  # Veo 3 模型：720p 或 1080p
                sample_count=1,  # 生成 1 个视频
            )
            
            print(f"✅ 视频生成成功!")
            
            # 获取视频 URI
            video_uri = generated_video.video.uri
            print(f"📁 视频 URI: {video_uri}")
            
            return jsonify({
                'success': True,
                'video_url': video_uri,
                'prompt': prompt
            })
            
        except Exception as e:
            print(f"❌ 视频生成失败：{str(e)}")
            error_msg = str(e)
            if "quota" in error_msg.lower():
                error_msg = "配额不足，请检查 Vertex AI 配额设置"
            elif "permission" in error_msg.lower():
                error_msg = "权限不足，请确保服务账号有 Vertex AI User 角色"
            
            return jsonify({
                'success': False,
                'error': f'视频生成失败：{error_msg}'
            }), 500
        
    except Exception as e:
        print(f"❌ 服务器错误：{str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误：{str(e)}'
        }), 500

# 健康检查
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)  # 生产环境关闭 debug
