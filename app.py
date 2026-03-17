#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
使用官方 2026 最新调用规范
"""
import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from google.cloud import aiplatform
from vertexai.generative_ai import VideoGenerationModel  # 必须使用这个类

# 初始化日志
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化配置
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1').strip()
LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1').strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': '请输入提示词'}), 400

        # 初始化，必须指定中心区域
        aiplatform.init(project=PROJECT_ID, location="us-central1")
        
        # 1. 加载 Veo 3.1 模型 (这是官方指定的加载方式)
        # 不要手动拼 projects/... 路径，直接用模型 ID
        model = VideoGenerationModel("veo-3.1-generate-001")
        
        logger.info(f"📡 正在发起 Veo 3.1 视频生成请求...")

        # 2. 调用官方指定的 generate_video 方法
        # 这一步会自动处理你之前遇到的所有 429 LRO 报错
        operation = model.generate_video(
            prompt=prompt,
            aspect_ratio="16:9",
            duration_seconds=5,
            # GCS 路径必须是这种格式
            output_gcs_uri=f"gs://red-atlas-video-assets/outputs/"
        )
        
        # 3. 获取异步任务 ID
        operation_name = operation.name
        logger.info(f"✅ 任务提交成功！任务 ID: {operation_name}")
        
        return jsonify({
            'success': True,
            'operation_name': operation_name,
            'message': '熊猫视频正在生成中，请稍候...'
        })

    except Exception as e:
        logger.error(f"❌ 调用失败：{str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 启动 Flask 应用，端口：{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
