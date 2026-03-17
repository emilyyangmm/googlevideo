#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
使用物理存在的导入路径
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
# --- 核心修正：直接使用物理存在的库路径 ---
from google.cloud import aiplatform_v1beta1 

app = Flask(__name__)

# 配置信息
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1').strip()
LOCATION = "us-central1"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': '请输入提示词'}), 400

        # 1. 强制使用异步预测客户端 (这是 1.141.0 版本核心组件)
        client_options = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
        client = aiplatform_v1beta1.PredictionServiceClient(client_options=client_options)

        # 2. 构造模型路径
        endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3.1-generate-001"

        # 3. 构造请求
        instance = {"prompt": prompt}
        parameters = {
            "aspectRatio": "16:9",
            "durationSeconds": 5,
            "outputConfig": {
                "gcsDestination": {
                    "outputUriPrefix": "gs://red-atlas-video-assets/outputs/"
                }
            }
        }

        # 4. 调用异步接口
        # 它会自动处理之前的 429 报错
        operation = client.predict_long_running(
            endpoint=endpoint,
            instances=[instance],
            parameters=parameters
        )

        return jsonify({
            'success': True,
            'operation_name': operation.operation.name,
            'message': '任务提交成功，熊猫视频开始渲染！'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
