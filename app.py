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
    # 1. 获取前端传来的原始路径
    raw_op_name = request.args.get('operation') 
    if not raw_op_name:
        return jsonify({'error': 'Missing operation name'}), 400

    # 2. 【核心修复】路径清洗
    # 无论传进来的是什么，我们只提取最后的 UUID（例如 c91195ec...）
    op_id = raw_op_name.split('/')[-1]
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = "us-central1"

    # 3. 构造标准的、干净的查询路径 (删掉中间的 publishers/google/models)
    # 正确格式：projects/{project}/locations/{location}/operations/{id}
    clean_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/operations/{op_id}"

    token = get_access_token()
    
    # 4. 发送请求
    try:
        res = http_requests.get(clean_url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        
        # 如果还是报错，尝试把 ID 包装成完整路径（这是为了适配某些特定 API 版本）
        if res.status_code != 200:
            return jsonify(res.json()), res.status_code
        
        return jsonify(res.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
