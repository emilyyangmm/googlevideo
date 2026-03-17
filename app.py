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

        # Veo 3.1 专用预测接口（必须使用 v1beta1）
        url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/us-central1/publishers/google/models/veo-3.1-generate-001:predictLongRunning"
        
        # 💡 关键：Veo 3.1 必须指定 GCS 输出目录
        gcs_bucket = "red-atlas-video-assets"
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "aspectRatio": "16:9", 
                "durationSeconds": 5,
                "outputConfig": {
                    "gcsDestination": {
                        "outputUriPrefix": f"gs://{gcs_bucket}/outputs/"
                    }
                }
            }
        }
        
        logger.info(f"📡 提交 Veo 3.1 生成请求，输出到：gs://{gcs_bucket}/outputs/")
        
        res = http_requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"})
        if res.status_code == 200:
            return jsonify({'success': True, 'operation_name': res.json().get('name')})
        logger.error(f"❌ 生成失败：{res.text}")
        return jsonify({'success': False, 'error': res.text}), res.status_code
    except Exception as e:
        logger.error(f"❌ 程序异常：{str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def check_status():
    try:
        op_name = request.args.get('operation')
        if not op_name:
            return jsonify({'error': 'Missing operation'}), 400
        
        token = get_access_token()
        
        # 💡 关键：直接使用完整的 operation name，v1beta1 端点能正确解析
        url = f"https://us-central1-aiplatform.googleapis.com/v1beta1/{op_name}"
        
        logger.info(f"📡 查询 Veo 状态：{url}")
        
        res = http_requests.get(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        
        if res.status_code == 200:
            return jsonify(res.json())
        
        logger.error(f"❌ 查询失败 {res.status_code}: {res.text[:200]}")
        return jsonify({'error': f"Google API Error {res.status_code}", 'detail': res.text[:200]}), res.status_code
        
    except Exception as e:
        logger.error(f"❌ 程序异常：{str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
