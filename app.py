#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 视频生成 Web 应用后端
使用 Flask 提供 API 服务
"""

import os
import json
import time
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

# 配置
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# 服务账号文件路径
SERVICE_ACCOUNT_FILE_PATH = None

# 如果配置的是 JSON 字符串，保存到临时文件
if SERVICE_ACCOUNT_JSON and SERVICE_ACCOUNT_JSON.strip().startswith('{'):
    try:
        # 验证 JSON 格式
        json.loads(SERVICE_ACCOUNT_JSON)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write(SERVICE_ACCOUNT_JSON)
        temp_file.close()
        SERVICE_ACCOUNT_FILE_PATH = temp_file.name
        print(f"✅ 服务账号配置成功：{SERVICE_ACCOUNT_FILE_PATH}")
    except Exception as e:
        print(f"❌ 服务账号 JSON 格式错误：{e}")
elif SERVICE_ACCOUNT_JSON and os.path.exists(SERVICE_ACCOUNT_JSON):
    SERVICE_ACCOUNT_FILE_PATH = SERVICE_ACCOUNT_JSON

# 内存存储操作状态
operations_cache = {}

def get_access_token():
    """从服务账号获取 access token"""
    if not SERVICE_ACCOUNT_FILE_PATH:
        return None
    
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE_PATH,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"❌ 获取 token 失败：{e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    access_token = get_access_token()
    
    return jsonify({
        'status': 'ok',
        'project_id': PROJECT_ID,
        'location': LOCATION,
        'has_service_account': bool(SERVICE_ACCOUNT_FILE_PATH),
        'service_account_valid': access_token is not None,
        'token_preview': (access_token[:20] + '...') if access_token else None
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
    
    # 获取 access token
    access_token = get_access_token()
    
    if not access_token:
        return jsonify({
            'error': '缺少认证信息',
            'hint': '请检查服务账号配置是否正确',
            'debug': {
                'has_json': bool(SERVICE_ACCOUNT_JSON),
                'has_file_path': bool(SERVICE_ACCOUNT_FILE_PATH)
            }
        }), 401
    
    # 构建 API 请求（Vertex AI API）
    # Veo 模型的端点 - 使用正确的 API 版本和路径
    model_id = "veo-3.1-fast-generate-001"
    
    # 使用 v1beta1 API（Veo 可能需要 beta 版本）
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{model_id}:predictLongRunning"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Veo API 请求格式
    payload = {
        "prompt": prompt,
        "video": {
            "aspectRatio": aspect_ratio,
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
        print(f"{'='*60}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        print(f"\n响应状态码：{response.status_code}")
        print(f"响应头：{dict(response.headers)}")
        print(f"响应内容：{response.text[:1000] if response.text else 'Empty'}")
        
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
                hint = "权限不足，请确保服务账号有 Vertex AI User 角色"
            elif "INVALID_ARGUMENT" in error_status:
                hint = "参数错误，请检查提示词格式"
            elif "NOT_FOUND" in error_status:
                hint = "模型未找到，请确认项目已启用 Vertex AI API"
            elif "RESOURCE_EXHAUSTED" in error_status:
                hint = "配额已用尽，请检查项目配额"
            elif "UNAUTHENTICATED" in error_status:
                hint = "认证失败，请检查服务账号是否有效"
            
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
    
    access_token = get_access_token()
    
    if not access_token:
        return jsonify({'error': '缺少认证信息'}), 401
    
    # 构建查询 URL
    url = f"https://aiplatform.googleapis.com/v1/{operation_name}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        
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
    print(f"🔐 服务账号：{'✅ 已配置' if SERVICE_ACCOUNT_FILE_PATH else '❌ 未配置'}")
    print("=" * 60)
    
    if not SERVICE_ACCOUNT_FILE_PATH:
        print("⚠️  警告：未配置服务账号，API 调用将失败！")
        print("请在环境变量中配置 GOOGLE_APPLICATION_CREDENTIALS")
    else:
        # 测试 token 获取
        token = get_access_token()
        if token:
            print("✅ 服务账号认证成功！")
        else:
            print("❌ 服务账号认证失败，请检查配置")
    print("=" * 60)
    
    app.run(debug=True, port=port, host='0.0.0.0')
