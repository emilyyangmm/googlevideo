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
        
        logger.info(f"📊 生成响应状态码：{res.status_code}")
        logger.info(f"📄 生成响应内容：{res.text[:500] if res.text else 'Empty'}")
        
        if res.status_code == 200:
            response_data = res.json()
            logger.info(f"✅ 生成成功，operation name: {response_data.get('name')}")
            return jsonify({'success': True, 'operation_name': response_data.get('name')})
        
        # 详细错误信息
        try:
            error_data = res.json()
            error_msg = error_data.get('error', {}).get('message', res.text)
        except:
            error_msg = res.text
        
        logger.error(f"❌ 生成失败 ({res.status_code}): {error_msg}")
        return jsonify({'success': False, 'error': error_msg, 'status_code': res.status_code}), res.status_code
    except Exception as e:
        logger.error(f"❌ 程序异常：{str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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

@app.route('/status', methods=['GET'])
def check_status():
    raw_op_name = request.args.get('operation', '')
    if not raw_op_name:
        return jsonify({'error': 'No operation'}), 400

    # 1. 提取 UUID (例如 c2df3802...)
    op_id = raw_op_name.split('/')[-1].strip().replace('"', '').replace("'", "")
    project_id = 'red-atlas-490409-v1'
    location = "us-central1"

    # 2. 构造标准查询路径（这是最稳的格式）
    clean_url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/operations/{op_id}"

    logger.info(f"📡 查询操作状态：{clean_url}")

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
        
        # 如果返回 200，说明查到任务了
        if res.status_code == 200:
            data = res.json()
            logger.info(f"📄 响应：{data}")
            # 如果 done 是 True，说明视频已经生成并存入桶里了
            return jsonify(data)
        
        # 如果还是报错，返回具体的 Google 错误信息
        logger.error(f"❌ Google 响应错误 ({res.status_code}): {res.text}")
        return jsonify({'error': 'Google API Error', 'msg': res.text}), res.status_code
        
    except Exception as e:
        logger.error(f"❌ 状态查询崩溃：{str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
