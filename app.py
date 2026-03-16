#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 视频生成 Web 应用后端
使用 Flask 提供 API 服务
"""

import os
import json
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

# 配置
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# 内存存储操作状态
operations_cache = {}

def check_api_key_validity(api_key):
    """检查 API Key 是否有效，并获取所属项目"""
    try:
        # 调用 API Keys 检查接口
        url = f"https://apikeys.googleapis.com/v1/keys?key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return True, data
        return False, None
    except:
        return None, None

@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'project_id': PROJECT_ID,
        'has_api_key': bool(API_KEY),
        'has_service_account': bool(SERVICE_ACCOUNT_FILE)
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频 API"""
    data = request.json
    prompt = data.get('prompt', '')
    duration = data.get('duration', 5)
    aspect_ratio = data.get('aspect_ratio', '16:9')
    
    if not prompt:
        return jsonify({'error': '提示词不能为空'}), 400
    
    # 优先使用 API Key
    api_key = API_KEY
    access_token = None
    
    if not api_key:
        # 尝试从服务账号获取 token
        if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
            try:
                from google.oauth2 import service_account
                from google.auth.transport.requests import Request
                
                credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                credentials.refresh(Request())
                access_token = credentials.token
            except Exception as e:
                print(f"服务账号认证失败：{e}")
    
    if not api_key and not access_token:
        return jsonify({
            'error': '缺少认证信息',
            'hint': '请在 Render 环境变量中配置 GOOGLE_API_KEY 或 GOOGLE_APPLICATION_CREDENTIALS'
        }), 401
    
    # 构建 API 请求
    # 使用 API Key 时，通过 Vertex AI 端点
    if api_key:
        # 注意：PROJECT_ID 应该从 API Key 所属项目获取，这里使用环境变量
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3.1-fast-generate-001:predictLongRunning"
        params = {'key': api_key}
        headers = {"Content-Type": "application/json"}
    else:
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3.1-fast-generate-001:predictLongRunning"
        params = {}
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
        print(f"\n{'='*60}")
        print(f"🎬 视频生成请求")
        print(f"{'='*60}")
        print(f"提示词：{prompt}")
        print(f"时长：{duration}秒")
        print(f"比例：{aspect_ratio}")
        print(f"URL: {url}")
        print(f"Project ID: {PROJECT_ID}")
        print(f"API Key: {'***' + api_key[-4:] if api_key else 'None'}")
        print(f"{'='*60}")
        
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=60)
        
        print(f"\n响应状态码：{response.status_code}")
        print(f"响应内容：{response.text[:500] if response.text else 'Empty'}")
        
        if response.status_code == 200:
            operation = response.json()
            operation_name = operation.get("name", "")
            
            operations_cache[operation_name] = {
                "start_time": time.time(),
                "prompt": prompt
            }
            
            print(f"✅ 任务提交成功：{operation_name}")
            
            return jsonify({
                'operation_name': operation_name,
                'message': '任务已提交，正在生成视频...'
            })
        else:
            # 尝试解析错误信息
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '未知错误')
                error_status = error_data.get('error', {}).get('status', '')
            except:
                error_msg = f'HTTP {response.status_code}: {response.text[:300]}'
                error_status = ''
            
            print(f"❌ API 错误：{error_status} - {error_msg}")
            
            # 提供有用的错误提示
            hint = ""
            if "PERMISSION_DENIED" in error_status:
                hint = "权限不足，请确保 API Key 有 Vertex AI 调用权限"
            elif "INVALID_ARGUMENT" in error_status:
                hint = "参数错误，请检查提示词格式"
            elif "NOT_FOUND" in error_status:
                hint = "模型未找到，请确认项目已启用 Vertex AI API"
            elif "RESOURCE_EXHAUSTED" in error_status:
                hint = "配额已用尽，请检查项目配额"
            elif "UNAUTHENTICATED" in error_status:
                hint = "认证失败，请检查 API Key 是否正确"
            
            return jsonify({
                'error': f'API 调用失败：{error_msg}',
                'status': error_status,
                'hint': hint
            }), response.status_code
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return jsonify({'error': '请求超时，请稍后重试'}), 504
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误：{e}")
        return jsonify({'error': f'网络错误：{str(e)}'}), 503
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return jsonify({'error': f'服务器错误：{str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def check_status():
    """查询操作状态"""
    operation_name = request.args.get('operation', '')
    
    if not operation_name:
        return jsonify({'error': '缺少操作名'}), 400
    
    api_key = API_KEY
    access_token = None
    
    if not api_key and SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            credentials.refresh(Request())
            access_token = credentials.token
        except:
            pass
    
    if not api_key and not access_token:
        return jsonify({'error': '缺少认证信息'}), 401
    
    # 构建查询 URL
    if api_key:
        url = f"https://aiplatform.googleapis.com/v1/{operation_name}"
        params = {'key': api_key}
        headers = {}
    else:
        url = f"https://aiplatform.googleapis.com/v1/{operation_name}"
        params = {}
        headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            operation = response.json()
            
            if operation.get("done"):
                video_uri = None
                if "response" in operation:
                    videos = operation["response"].get("generatedVideos", [])
                    if videos:
                        video_uri = videos[0].get("video", {}).get("uri")
                
                print(f"✅ 视频生成完成：{video_uri}")
                
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
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', '未知错误')
            except:
                error_msg = f'HTTP {response.status_code}'
            return jsonify({'error': f'查询失败：{error_msg}'}), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': '查询超时'}), 504
    except Exception as e:
        return jsonify({'error': f'查询失败：{str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    print("=" * 60)
    print("🎬 Google Veo 视频生成 Web 应用")
    print("=" * 60)
    print(f"📱 访问地址：http://localhost:{port}")
    print(f"📂 项目 ID: {PROJECT_ID or '未设置'}")
    print(f"📍 区域：{LOCATION}")
    print(f"🔑 API Key: {'已配置' + ' (***' + API_KEY[-4:] + ')' if API_KEY else '未配置'}")
    print(f"🔐 服务账号：{'已配置' if SERVICE_ACCOUNT_FILE else '未配置'}")
    print("=" * 60)
    
    if not API_KEY and not SERVICE_ACCOUNT_FILE:
        print("⚠️  警告：未配置任何认证信息，API 调用将失败！")
        print("请在环境变量中配置 GOOGLE_API_KEY 或 GOOGLE_APPLICATION_CREDENTIALS")
    print("=" * 60)
    
    app.run(debug=True, port=port, host='0.0.0.0')
