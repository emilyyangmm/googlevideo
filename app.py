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

app = Flask(__name__, static_folder='.')
CORS(app)

# 配置
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
API_KEY = os.environ.get("GOOGLE_API_KEY", "")
SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

# 服务账号文件路径
SERVICE_ACCOUNT_FILE_PATH = None

# 优先使用 API Key，其次使用服务账号
if API_KEY:
    print(f"✅ 使用 API Key 认证：***{API_KEY[-10:]}")
    # API Key 方式：设置环境变量
    os.environ["GOOGLE_API_KEY"] = API_KEY
    # 如果是 AQ. 开头的临时 Token，也尝试使用
    if API_KEY.startswith("AQ."):
        print("⚠️  检测到 AQ. 开头的 Token，可能是临时认证")
elif SERVICE_ACCOUNT_JSON and len(SERVICE_ACCOUNT_JSON) > 100:
    try:
        json_data = json.loads(SERVICE_ACCOUNT_JSON)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write(SERVICE_ACCOUNT_JSON)
        temp_file.close()
        SERVICE_ACCOUNT_FILE_PATH = temp_file.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE_PATH
        print(f"✅ 使用服务账号认证：{json_data.get('project_id', 'unknown')}")
    except Exception as e:
        print(f"❌ 服务账号 JSON 格式错误：{e}")
else:
    print("❌ 未配置任何认证方式")

# 内存存储操作状态
operations_cache = {}

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
        'location': LOCATION,
        'has_service_account': bool(SERVICE_ACCOUNT_FILE_PATH)
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """生成视频 API - 使用 Google Gen AI SDK"""
    data = request.json
    prompt = data.get('prompt', '')
    duration = data.get('duration', 5)
    aspect_ratio = data.get('aspect_ratio', '16:9')
    
    if not prompt:
        return jsonify({'error': '提示词不能为空'}), 400
    
    if not API_KEY and not SERVICE_ACCOUNT_FILE_PATH:
        return jsonify({
            'error': '缺少认证信息',
            'hint': '请配置 GOOGLE_API_KEY 或 GOOGLE_APPLICATION_CREDENTIALS'
        }), 401
    
    try:
        print(f"\n{'='*60}")
        print(f"🎬 视频生成请求")
        print(f"{'='*60}")
        print(f"提示词：{prompt}")
        print(f"时长：{duration}秒")
        print(f"比例：{aspect_ratio}")
        print(f"项目：{PROJECT_ID}")
        print(f"区域：{LOCATION}")
        print(f"{'='*60}")
        
        # 使用 Google Gen AI SDK
        from google import genai
        from google.genai import types
        
        # 创建客户端（SDK 会自动使用环境变量中的认证）
        client = genai.Client(
            project=PROJECT_ID,
            location=LOCATION,
        )
        
        print(f"✅ SDK 客户端已创建，认证方式：{'API Key' if API_KEY else '服务账号'}")
        
        # 根据网页版官方示例代码（完全一致）
        # 参考：网页版"获取代码" → Python 示例
        source = types.GenerateVideosSource(
            prompt=prompt,
        )
        
        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            number_of_videos=1,
            duration_seconds=duration,
            person_generation="allow_all",
            generate_audio=False,
            resolution="720p",
        )
        
        print(f"📋 请求参数：prompt={prompt[:50]}..., aspect_ratio={aspect_ratio}, duration={duration}s")
        
        # 生成视频
        operation = client.models.generate_videos(
            model="veo-3.1-generate-001",
            source=source,
            config=config,
        )
        
        operation_name = operation.operation_name
        
        # 缓存操作信息
        operations_cache[operation_name] = {
            "start_time": time.time(),
            "prompt": prompt,
            "client": client,
            "operation": operation
        }
        
        print(f"✅ 任务提交成功：{operation_name}")
        
        return jsonify({
            'operation_name': operation_name,
            'message': '任务已提交，正在生成视频...'
        })
        
    except Exception as e:
        print(f"❌ 生成失败：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'生成失败：{str(e)}',
            'type': type(e).__name__
        }), 500

@app.route('/api/status', methods=['GET'])
def check_status():
    """查询操作状态"""
    operation_name = request.args.get('operation', '')
    
    if not operation_name:
        return jsonify({'error': '缺少操作名'}), 400
    
    try:
        # 从缓存获取操作
        cached = operations_cache.get(operation_name)
        
        if not cached:
            return jsonify({'error': '操作不存在'}), 404
        
        client = cached.get('client')
        operation = cached.get('operation')
        
        if not client or not operation:
            return jsonify({'error': '操作信息不完整'}), 404
        
        # 查询操作状态
        operation = client.operations.get(operation)
        
        # 更新缓存
        operations_cache[operation_name]['operation'] = operation
        
        if operation.done:
            response = operation.result
            
            if not response:
                return jsonify({
                    'done': True,
                    'error': '生成失败，无响应'
                })
            
            generated_videos = response.generated_videos
            
            if not generated_videos:
                return jsonify({
                    'done': True,
                    'error': '未生成视频'
                })
            
            # 获取第一个视频的 URI
            video_uri = None
            if generated_videos[0].video:
                video_uri = generated_videos[0].video.uri
            
            print(f"✅ 视频生成完成：{video_uri}")
            
            return jsonify({
                'done': True,
                'video_uri': video_uri,
                'result': {
                    'generated_videos': len(generated_videos)
                }
            })
        else:
            return jsonify({
                'done': False,
                'metadata': {}
            })
            
    except Exception as e:
        print(f"❌ 查询失败：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'查询失败：{str(e)}'
        }), 500

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
    else:
        print("✅ 服务账号已配置，可以正常使用")
    print("=" * 60)
    
    app.run(debug=True, port=port, host='0.0.0.0')
