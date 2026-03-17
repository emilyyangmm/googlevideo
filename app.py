#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
使用原生 HTTP 请求调用 :videoGenerationPredict 端点
"""
import os
import logging
import requests as http_requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 配置信息
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1').strip()
LOCATION = "us-central1"

def get_access_token():
    """获取 Google Cloud 访问令牌"""
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            return None
        
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        logging.error(f"获取 Token 失败: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': '请输入提示词'}), 400
        
        token = get_access_token()
        if not token:
            return jsonify({'success': False, 'error': '认证失败'}), 500
        
        # 【终极核武器】直接调用 :videoGenerationPredict 端点（v1beta1 预览版）
        url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/veo-3.1-generate-001:videoGenerationPredict"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "aspectRatio": "16:9",
                "durationSeconds": 5,
                "outputConfig": {
                    "gcsDestination": {
                        "outputUriPrefix": "gs://red-atlas-video-assets/outputs/"
                    }
                }
            }
        }
        
        logging.info(f"🚀 发送 HTTP 请求到: {url}")
        response = http_requests.post(url, headers=headers, json=payload, timeout=60)
        
        logging.info(f"📊 响应状态: {response.status_code}")
        logging.info(f"📄 响应内容: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            operation_name = data.get('name', 'Unknown')
            logging.info(f"✅ 成功！Operation: {operation_name}")
            return jsonify({
                'success': True,
                'operation_name': operation_name,
                'message': '熊猫视频开始渲染！'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'HTTP {response.status_code}: {response.text}'
            }), response.status_code

    except Exception as e:
        logging.error(f"❌ 请求失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
