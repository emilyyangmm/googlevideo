#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 视频生成 Web 应用后端
使用 Vertex AI HTTP API 调用 Veo 模型
"""

import os
import sys
import json
import tempfile
import requests as http_requests
import traceback
import logging
from flask import Flask, render_template, request, jsonify
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud import storage
from google.cloud.aiplatform_v1 import JobServiceClient
from google.api_core.operations_v1 import OperationsClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 获取 access token
def get_access_token():
    """从服务账号获取 access token"""
    try:
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        logger.info(f"🔍 检查服务账号文件路径：{credentials_path}")
        
        if not credentials_path:
            logger.error("❌ 环境变量 GOOGLE_APPLICATION_CREDENTIALS 未设置")
            return None
        
        if not os.path.exists(credentials_path):
            logger.error(f"❌ 文件不存在：{credentials_path}")
            logger.info(f"📁 当前目录：{os.getcwd()}")
            secrets_dir = '/etc/secrets/'
            if os.path.exists(secrets_dir):
                logger.info(f"📂 /etc/secrets/ 目录内容：{os.listdir(secrets_dir)}")
            else:
                logger.error("📂 /etc/secrets/ 目录不存在")
            return None
        
        logger.info(f"✅ 文件存在，加载服务账号：{credentials_path}")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        logger.info("✅ 服务账号加载成功，刷新 token...")
        credentials.refresh(Request())
        logger.info("✅ Token 刷新成功")
        return credentials.token
    except Exception as e:
        logger.error(f"❌ 获取 token 失败：{str(e)}")
        logger.error(f"📋 详细堆栈：{traceback.format_exc()}")
        return None

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 视频生成 API 路由
@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        # 获取请求中的提示词
        data = request.json
        prompt = data.get('prompt', '')
        
        logger.info(f"🎬 收到生成请求，提示词：{prompt}")
        
        if not prompt:
            logger.error("❌ 提示词为空")
            return jsonify({'success': False, 'error': '请提供提示词'}), 400
        
        # 获取认证 token
        access_token = get_access_token()
        if not access_token:
            logger.error("❌ 认证失败，无法获取 access token")
            return jsonify({
                'success': False, 
                'error': '认证失败，请检查服务账号配置'
            }), 500
        
        # 获取项目配置
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        if not project_id:
            logger.error("❌ 缺少 GOOGLE_CLOUD_PROJECT 环境变量")
            return jsonify({
                'success': False,
                'error': '缺少 GOOGLE_CLOUD_PROJECT 环境变量'
            }), 500
        
        # 尝试多个模型 ID
        model_ids = [
            "veo-3.1-generate-001",
            "veo-3.1-fast-generate-001",
            "veo-3.0-generate-001",
            "veo-3.0-fast-generate-001",
            "veo-2.0-generate-001",
        ]
        
        operation_name = None
        
        for model_id in model_ids:
            try:
                # 调用 Vertex AI API
                url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predictLongRunning"
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "instances": [{"prompt": prompt}],
                    "parameters": {
                        "aspectRatio": "16:9",
                        "durationSeconds": 8,
                        "numberOfVideos": 1,
                        "personGeneration": "allow_adult",
                        "generateAudio": False,
                        "resolution": "720p",
                    }
                }
                
                logger.info(f"📡 调用模型：{model_id}")
                response = http_requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    operation = response.json()
                    operation_name = operation.get("name", "")
                    logger.info(f"✅ 模型 {model_id} 调用成功，操作名：{operation_name}")
                    break
                else:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', '未知错误')
                    logger.warning(f"⚠️ 模型 {model_id} 调用失败：{error_msg}")
                    continue
                    
            except Exception as e:
                logger.warning(f"⚠️ 模型 {model_id} 调用异常：{str(e)}")
                continue
        
        if not operation_name:
            logger.error("❌ 所有模型调用均失败")
            return jsonify({
                'success': False,
                'error': '所有模型调用均失败，请检查项目配置和 API 权限'
            }), 500
        
        # 缓存操作信息
        return jsonify({
            'success': True,
            'operation_name': operation_name,
            'message': '任务已提交，正在生成视频...',
            'prompt': prompt
        })
        
    except Exception as e:
        logger.error(f"❌ 服务器错误：{str(e)}")
        logger.error(f"📋 详细堆栈：{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误：{str(e)}'
        }), 500

# 查询操作状态
@app.route('/status', methods=['GET'])
def check_status():
    try:
        operation_name = request.args.get('operation', '')
        
        logger.info(f"🔍 查询操作状态：{operation_name}")
        
        if not operation_name:
            logger.error("❌ 缺少操作名")
            return jsonify({'error': '缺少操作名'}), 400
        
        # 获取认证
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path or not os.path.exists(credentials_path):
            logger.error("❌ 服务账号文件不存在")
            return jsonify({'error': '认证失败'}), 500
        
        # 使用 SDK 查询操作状态
        # 对于 Veo 3.1+ 的 predictLongRunning，需要提取项目和位置信息
        # operation_name 格式：projects/xxx/locations/xxx/publishers/google/models/xxx/operations/xxx
        try:
            if '/publishers/google/models/' in operation_name:
                parts = operation_name.split('/')
                if len(parts) >= 10:
                    project_id = parts[1]
                    location = parts[3]
                    operation_id = parts[9]
                    
                    # 创建 OperationsClient
                    client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
                    operations_client = OperationsClient(client_options=client_options)
                    
                    # 构建 operation 名称用于查询
                    name = f"projects/{project_id}/locations/{location}/operations/{operation_id}"
                    logger.info(f"📡 使用 SDK 查询：{name}")
                    
                    # 使用 SDK 查询操作
                    response = operations_client.get_operation(name=name)
                    
                    # 转换为字典
                    from google.protobuf.json_format import MessageToDict
                    operation = MessageToDict(response._pb) if hasattr(response, '_pb') else {}
                else:
                    logger.error(f"❌ operation name 格式错误：{operation_name}")
                    return jsonify({'error': 'operation name 格式错误'}), 400
            else:
                logger.error(f"❌ 不支持的 operation name 格式：{operation_name}")
                return jsonify({'error': '不支持的 operation name 格式'}), 400
        except Exception as sdk_error:
            logger.error(f"❌ SDK 查询失败：{str(sdk_error)}")
            logger.error(f"📋 详细堆栈：{traceback.format_exc()}")
            return jsonify({'error': f'查询失败：{str(sdk_error)}'}), 500
        
            # 操作完成
            if "response" in operation:
                videos = operation["response"].get("generatedVideos", [])
                if videos:
                    video_uri = videos[0].get("video", {}).get("uri")
                    logger.info(f"✅ 视频生成完成：{video_uri}")
                    
                    # 如果是 gs:// 链接，尝试转换为签名 URL
                    public_url = video_uri
                    if video_uri.startswith('gs://'):
                        try:
                            # 解析 GCS 路径
                            bucket_name = video_uri.split('/')[2]
                            blob_name = '/'.join(video_uri.split('/')[3:])
                            
                            # 创建存储客户端
                            storage_client = storage.Client()
                            bucket = storage_client.bucket(bucket_name)
                            blob = bucket.blob(blob_name)
                            
                            # 生成签名 URL（有效期 1 小时）
                            public_url = blob.generate_signed_url(
                                version="v4",
                                expiration=3600,  # 1 小时
                                method="GET"
                            )
                            logger.info(f"✅ 生成签名 URL: {public_url}")
                        except Exception as e:
                            logger.warning(f"⚠️ 无法生成签名 URL: {str(e)}")
                            # 继续使用原始 gs:// 链接
                    
                    return jsonify({
                        'done': True,
                        'video_uri': public_url,
                        'original_uri': video_uri,
                        'success': True
                    })
            
            logger.error("❌ 视频生成失败，无返回结果")
            return jsonify({
                'done': True,
                'error': '视频生成失败，无返回结果'
            })
        else:
            # 进行中
            logger.info("⏳ 视频还在生成中...")
            return jsonify({
                'done': False,
                'metadata': operation.get('metadata', {})
            })
            
    except Exception as e:
        logger.error(f"❌ 查询状态失败：{str(e)}")
        logger.error(f"📋 详细堆栈：{traceback.format_exc()}")
        return jsonify({'error': f'查询失败：{str(e)}'}), 500

# 健康检查
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 启动 Flask 应用，端口：{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
