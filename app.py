#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
import requests as http_requests
from flask import Flask, render_template, request, jsonify
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# 初始化日志
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_access_token():
    try:
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            logger.error(f"❌ 找不到凭据文件：{creds_path}")
            return None
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        creds.refresh(Request())
        return creds.token
    except Exception as e:
        logger.error(f"❌ Token 刷新失败：{e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        token = get_access_token()

        # Veo 3.1 专用预测接口
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/veo-3.1-generate-001:predictLongRunning"
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"aspectRatio": "16:9", "durationSeconds": 5}
        }
        
        res = http_requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"})
        if res.status_code == 200:
            # 这里返回的 name 是完整的：projects/xxx/locations/xxx/publishers/google/models/xxx/operations/xxx
            return jsonify({'success': True, 'operation_name': res.json().get('name')})
        return jsonify({'success': False, 'error': res.text}), res.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def check_status():
    try:
        op_name = request.args.get('operation')
        if not op_name:
            return jsonify({'error': 'Missing operation'}), 400
        
        token = get_access_token()
        # --- 核心修复点：动态解析 Location 并拼接区域域名 ---
        location = "us-central1"
        if "locations/" in op_name:
            location = op_name.split("locations/")[1].split("/")[0]
        
        # 必须使用 {location}-aiplatform 域名，且直接接上 op_name
        url = f"https://{location}-aiplatform.googleapis.com/v1/{op_name}"
        
        logger.info(f"📡 正在查询 Veo 状态：{url}")
        res = http_requests.get(url, headers={"Authorization": f"Bearer {token}"})
        
        if res.status_code != 200:
            # 如果 404，通常是域名或项目 ID 不匹配
            logger.error(f"❌ 查询失败 {res.status_code}: {res.text}")
            return jsonify({'error': f"Google API Error {res.status_code}"}), res.status_code
        
        return jsonify(res.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
