#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
import requests as http_requests
import re
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
        # 💡 关键修复：添加默认项目 ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1')
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
    # 1. 直接获取前端传来的完整路径，不要做任何 split 或清洗
    raw_op_name = request.args.get('operation', '')
    if not raw_op_name:
        return jsonify({'error': 'No operation'}), 400

    # 去掉可能的引号
    full_path = raw_op_name.strip().replace('"', '').replace("'", "")
    
    # 2. 构造正确的 API 完整请求地址
    # 注意：Veo 3.1 的状态查询必须是：https://{location}-aiplatform.googleapis.com/v1beta1/{full_path}
    location = "us-central1"
    clean_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/{full_path}"

    logger.info(f"📡 最终验证路径查询：{clean_url}")

    token = get_access_token()
    if not token:
        logger.error("❌ 无法获取认证 token")
        return jsonify({'error': 'Authentication failed'}), 500
    
    try:
        res = http_requests.get(clean_url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, timeout=30)
        
        logger.info(f"📊 响应状态码：{res.status_code}")
        logger.info(f"📄 响应内容：{res.text[:500] if res.text else 'Empty'}")
        
        # 处理空响应
        if not res.text:
            logger.error("❌ 空响应")
            return jsonify({'error': 'Empty response from Google API'}), res.status_code
        
        # 尝试解析 JSON
        try:
            data = res.json()
        except Exception as json_err:
            logger.error(f"❌ JSON 解析失败：{str(json_err)}")
            logger.error(f"📄 原始响应：{res.text[:200]}")
            return jsonify({'error': 'Invalid JSON response', 'detail': res.text[:200]}), res.status_code
        
        # 3. 这里的逻辑很关键：如果返回 200，说明查到了
        if res.status_code == 200:
            return jsonify(data)
        
        # 如果报错，输出详细信息
        logger.error(f"❌ Google 响应错误 ({res.status_code}): {res.text}")
        return jsonify(data), res.status_code

    except Exception as e:
        logger.error(f"❌ 状态查询崩溃：{str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
