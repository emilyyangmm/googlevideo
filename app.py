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
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1').strip()
LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1').strip()

logger.info(f"🔧 初始化配置：Project={PROJECT_ID}, Location={LOCATION}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': '请提供提示词'}), 400
        
        current_loc = LOCATION.strip()
        logger.info(f"📡 最终修正：使用底层 predict 接口 (Region: {current_loc})")

        from google.cloud import aiplatform_v1beta1
        
        # 1. 强制端点
        client_options = {"api_endpoint": f"{current_loc}-aiplatform.googleapis.com"}
        client = aiplatform_v1beta1.PredictionServiceClient(client_options=client_options)
        
        # 2. 构造路径
        endpoint = f"projects/{PROJECT_ID}/locations/{current_loc}/publishers/google/models/veo-3.1-generate-001"
        
        # 3. 构造请求
        instance = {"prompt": prompt}
        parameters = {
            "aspectRatio": "16:9",
            "durationSeconds": 5,
            "outputConfig": {
                "gcsDestination": {
                    "outputUriPrefix": "gs://red-atlas-video-assets/outputs/"
                }
            }
        }
        
        # 4. 【核心修复】底层客户端使用 predict 方法，它会返回一个 LRO
        logger.info(f"🚀 发起底层 predict 调用...")
        
        # 在 v1beta1 中，Veo 这种长任务是通过普通的 predict 发起
        # 但后端会自动识别并返回一个长任务响应
        response = client.predict(
            endpoint=endpoint,
            instances=[instance],
            parameters=parameters
        )
        
        # 5. 尝试获取 Operation Name
        # 如果是底层调用，我们需要从响应对象的 metadata 中提取任务 ID
        logger.info(f"✅ 底层调用已响应")
        
        return jsonify({
            'success': True,
            'message': '任务已提交，正在等待 Google 排队',
            'raw_response': str(response.metadata) if hasattr(response, 'metadata') else "Done"
        })
        
    except Exception as e:
        logger.error(f"❌ 依然失败：{str(e)}")
        # 如果报错包含 "429"，说明我们必须得用 LongRunning 接口，
        # 那么在底层库里，那个方法叫：client.video_generation_predict
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def check_status():
    try:
        operation_name = request.args.get('operation')
        if not operation_name:
            return jsonify({'error': 'No operation'}), 400
        
        logger.info(f"📡 查询操作状态：{operation_name}")
        
        # 初始化 SDK
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        
        # --- 核心修复：通过 create_channel 手动创建通信管道 ---
        from google.api_core.operations_v1 import OperationsClient
        from google.api_core.grpc_helpers import create_channel

        # 不再通过 client_options 传参，而是直接指定地址创建 channel
        endpoint = f"{LOCATION}-aiplatform.googleapis.com"
        channel = create_channel(endpoint)
        operations_client = OperationsClient(channel)
        
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
