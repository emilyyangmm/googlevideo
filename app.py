#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
使用底层 video_generation_predict 方法
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
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
        
        # 1. 强制使用异步端点
        client_options = {"api_endpoint": f"us-central1-aiplatform.googleapis.com"}
        client = aiplatform_v1beta1.PredictionServiceClient(client_options=client_options)

        # 2. 绝对路径
        endpoint = f"projects/red-atlas-490409-v1/locations/us-central1/publishers/google/models/veo-3.1-generate-001"

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

        # 4. 【核心修正】调用 v1beta1 中真正的异步方法名
        response = client.video_generation_predict(
            endpoint=endpoint,
            instances=[instance],
            parameters=parameters
        )

        return jsonify({
            'success': True, 
            'operation_name': response.operation.name
        })

    except AttributeError:
        # 万一 Google 在这个子版本里又改回去了，做个保底尝试
        logging.info("尝试保底方法...")
        try:
            client_options = {"api_endpoint": f"us-central1-aiplatform.googleapis.com"}
            client = aiplatform_v1beta1.PredictionServiceClient(client_options=client_options)
            endpoint = f"projects/red-atlas-490409-v1/locations/us-central1/publishers/google/models/veo-3.1-generate-001"
            instance = {"prompt": request.json.get('prompt')}
            parameters = {
                "aspectRatio": "16:9",
                "durationSeconds": 5,
                "outputConfig": {
                    "gcsDestination": {
                        "outputUriPrefix": "gs://red-atlas-video-assets/outputs/"
                    }
                }
            }
            response = client.predict(
                endpoint=endpoint,
                instances=[instance],
                parameters=parameters
            )
            return jsonify({'success': True, 'msg': '已尝试保底调用'})
        except Exception as e2:
            return jsonify({'success': False, 'error': str(e2)}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
