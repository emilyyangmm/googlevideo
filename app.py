#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 视频生成 Web 应用后端
使用 Flask 提供 API 服务
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.', static_files_path='.')
CORS(app)

# 配置
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "867714362426")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# 内存存储操作状态
operations_cache = {}

def get_access_token_from_sa():
    """从服务账号获取 access token"""
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        return None
    
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"获取 token 失败：{e}")
        return None

def get_api_key():
    """从环境变量获取 API Key"""
    return os.environ.get("GOOGLE_API_KEY")

@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'index.html')

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频 API"""
    data = request.json
    prompt = data.get('prompt', '')
    duration = data.get('duration', 5)
    aspect_ratio = data.get('aspect_ratio', '16:9')
    
    if not prompt:
        return jsonify({'error': '提示词不能为空'}), 400
    
    # 获取认证
    access_token = get_access_token_from_sa()
    api_key = get_api_key()
    
    if not access_token and not api_key:
        return jsonify({'error': '缺少认证信息，请配置服务账号或 API Key'}), 401
    
    # 调用 Vertex AI API
    if api_key:
        # 使用 API Key 方式
        url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-fast-generate-001:predictLongRunning?key={api_key}"
        headers = {"Content-Type": "application/json"}
    else:
        # 使用服务账号方式
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3.1-fast-generate-001:predictLongRunning"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "numberOfVideos": 1,
            "durationSeconds": duration
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            operation = response.json()
            operation_name = operation.get("name", "")
            
            operations_cache[operation_name] = {
                "start_time": time.time(),
                "prompt": prompt
            }
            
            return jsonify({
                'operation_name': operation_name,
                'message': '任务已提交，正在生成视频...'
            })
        else:
            error_msg = response.json().get('error', {}).get('message', '未知错误')
            return jsonify({'error': f'API 调用失败：{error_msg}'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': f'请求失败：{str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def check_status():
    """查询操作状态"""
    operation_name = request.args.get('operation', '')
    
    if not operation_name:
        return jsonify({'error': '缺少操作名'}), 400
    
    access_token = get_access_token_from_sa()
    api_key = get_api_key()
    
    if not access_token and not api_key:
        return jsonify({'error': '缺少认证信息'}), 401
    
    # 查询操作状态
    if api_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/operations/{operation_name}?key={api_key}"
        headers = {}
    else:
        url = f"https://aiplatform.googleapis.com/v1/{operation_name}"
        headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            operation = response.json()
            
            if operation.get("done"):
                video_uri = None
                if "response" in operation:
                    videos = operation["response"].get("generatedVideos", [])
                    if videos:
                        video_uri = videos[0].get("video", {}).get("uri")
                
                return jsonify({
                    'done': True,
                    'video_uri': video_uri,
                    'result': operation.get('response', {})
                })
            else:
                return jsonify({
                    'done': False,
                    'metadata': operation.get('metadata', {})
                })
        else:
            error_msg = response.json().get('error', {}).get('message', '未知错误')
            return jsonify({'error': f'查询失败：{error_msg}'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': f'请求失败：{str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    # Render 需要绑定到 0.0.0.0
    host = os.environ.get("RENDER", "false").lower() == "true" and "0.0.0.0" or "0.0.0.0"
    
    print("=" * 60)
    print("🎬 Google Veo 视频生成 Web 应用")
    print("=" * 60)
    print(f"📱 访问地址：http://localhost:{port}")
    print(f"📂 项目 ID: {PROJECT_ID}")
    print(f"📍 区域：{LOCATION}")
    print(f"🔐 认证：{'服务账号' if SERVICE_ACCOUNT_FILE else 'API Key' if os.environ.get('GOOGLE_API_KEY') else '未配置'}")
    print("=" * 60)
    app.run(debug=True, port=port, host=host)
