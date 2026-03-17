#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
使用 Vertex AI SDK 调用 Veo 模型
"""
import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from google.cloud import aiplatform
from google.api_core import operation as operation_module

# 初始化日志
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化 Vertex AI SDK
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1')
LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': '请提供提示词'}), 400
        
        logger.info(f"📡 提交 Veo 3.1 生成请求：{prompt[:50]}...")
        
        # 使用 Vertex AI SDK 调用 Veo 3.1
        # 初始化 SDK
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        # 调用 Veo 3.1 模型
        model_endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3.1-generate-001"
        
        # 使用 predictLongRunning 方法
        response = aiplatform.Model(model_endpoint).predict_long_running(
            instances=[{"prompt": prompt}],
            parameters={
                "aspectRatio": "16:9",
                "durationSeconds": 5,
                "outputConfig": {
                    "gcsDestination": {
                        "outputUriPrefix": "gs://red-atlas-video-assets/outputs/"
                    }
                }
            }
        )
        
        # 获取 operation name
        operation_name = response.operation.name
        logger.info(f"✅ 生成任务已提交，operation: {operation_name}")
        
        return jsonify({
            'success': True,
            'operation_name': operation_name
        })
        
    except Exception as e:
        logger.error(f"❌ 生成失败：{str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def check_status():
    try:
        operation_name = request.args.get('operation')
        if not operation_name:
            return jsonify({'error': 'No operation'}), 400
        
        logger.info(f"📡 查询操作状态：{operation_name}")
        
        # 使用 SDK 查询操作状态
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        # 使用 OperationsClient 查询
        from google.api_core.operations_v1 import OperationsClient
        from google.api_core.client_options import ClientOptions
        
        client_options = ClientOptions(api_endpoint=f"{LOCATION}-aiplatform.googleapis.com")
        operations_client = OperationsClient(client_options=client_options)
        
        # 查询操作状态
        response = operations_client.get_operation(name=operation_name)
        
        # 转换为字典
        from google.protobuf.json_format import MessageToDict
        result = MessageToDict(response._pb) if hasattr(response, '_pb') else {}
        
        logger.info(f"📊 响应：{result}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ 状态查询失败：{str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug/gcs', methods=['GET'])
def debug_gcs():
    """调试端点：检查 GCS 存储桶是否存在及权限"""
    try:
        from google.cloud import storage
        
        gcs_bucket = "red-atlas-video-assets"
        logger.info(f"🔍 检查 GCS 存储桶：{gcs_bucket}")
        
        # 尝试创建 storage client
        storage_client = storage.Client()
        logger.info("✅ Storage Client 创建成功")
        
        # 检查存储桶是否存在
        bucket = storage_client.bucket(gcs_bucket)
        exists = bucket.exists()
        logger.info(f"📦 存储桶 {'存在' if exists else '不存在'}")
        
        if exists:
            # 尝试列出文件
            blobs = list(bucket.list_blobs(max_results=5))
            logger.info(f"📄 存储桶中有 {len(blobs)} 个文件")
            
            return jsonify({
                'bucket': gcs_bucket,
                'exists': exists,
                'file_count': len(blobs),
                'files': [blob.name for blob in blobs]
            })
        else:
            return jsonify({
                'bucket': gcs_bucket,
                'exists': False,
                'error': '存储桶不存在，请创建它'
            }), 404
            
    except Exception as e:
        logger.error(f"❌ GCS 调试失败：{str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 启动 Flask 应用，端口：{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
