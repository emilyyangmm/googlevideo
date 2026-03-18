#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
/generate  - 提交任务，立即返回 operation_name（不阻塞）
/status    - 前端轮询任务状态
"""
import os
import logging
import requests as http_requests
from flask import Flask, render_template, request, jsonify

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1').strip()
LOCATION   = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1').strip()
GCS_OUTPUT = "gs://red-atlas-video-assets/outputs/"

# 提交任务端点
VEO_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1"
    f"/projects/{PROJECT_ID}/locations/{LOCATION}"
    f"/publishers/google/models/veo-3.1-generate-001:predictLongRunning"
)

# 查询任务状态端点（Veo 专用，POST 方式）
FETCH_OP_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1"
    f"/projects/{PROJECT_ID}/locations/{LOCATION}"
    f"/publishers/google/models/veo-3.1-generate-001:fetchPredictOperation"
)


_credentials = None

def get_access_token():
    """获取 Google Cloud 访问令牌（缓存凭证，token 过期才刷新）"""
    global _credentials
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request

        if _credentials is None:
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not creds_path or not os.path.exists(creds_path):
                logging.error("未找到凭证文件")
                return None
            _credentials = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )

        if not _credentials.valid:
            _credentials.refresh(Request())

        return _credentials.token
    except Exception as e:
        logging.error(f"获取 Token 失败: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """提交任务，立即返回 operation_name，不等待生成完成"""
    try:
        body   = request.get_json(silent=True) or {}
        prompt = body.get('prompt', '').strip()
        if not prompt:
            return jsonify({'success': False, 'error': '请输入提示词'}), 400

        # 从前端读取时长和比例，提供合理默认值
        duration     = int(body.get('duration', 8))
        aspect_ratio = body.get('aspect_ratio', '16:9')
        # Veo 只支持 4 / 6 / 8 秒
        if duration not in (4, 6, 8):
            duration = 8

        token = get_access_token()
        if not token:
            return jsonify({'success': False, 'error': '认证失败，请检查服务账号凭证'}), 500

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration,
                "outputConfig": {
                    "gcsDestination": {
                        "outputUriPrefix": GCS_OUTPUT
                    }
                }
            }
        }

        logging.info(f"🚀 提交请求: {VEO_URL}")
        resp = http_requests.post(VEO_URL, headers=headers, json=payload, timeout=60)
        logging.info(f"📊 响应 {resp.status_code}: {resp.text[:300]}")

        if resp.status_code not in (200, 202):
            return jsonify({
                'success': False,
                'error': f'HTTP {resp.status_code}: {resp.text}'
            }), resp.status_code

        operation_name = resp.json().get('name', '')
        logging.info(f"✅ 任务已提交: {operation_name}")

        # 立即返回，不阻塞——前端自己轮询 /status
        return jsonify({
            'success': True,
            'operation_name': operation_name,
            'message': '任务已提交，请等待生成...'
        })

    except Exception as e:
        logging.exception("❌ 请求异常")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """
    前端轮询状态
    GET /status?operation_name=projects/.../operations/uuid
    """
    operation_name = request.args.get('operation_name', '').strip()
    if not operation_name:
        return jsonify({'success': False, 'error': '缺少 operation_name'}), 400

    token = get_access_token()
    if not token:
        return jsonify({'success': False, 'error': '认证失败'}), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 用 fetchPredictOperation（POST）查询 Veo 任务状态
    resp = http_requests.post(
        FETCH_OP_URL,
        headers=headers,
        json={"operationName": operation_name},
        timeout=30
    )
    logging.info(f"🔄 状态查询 {resp.status_code}: {resp.text[:200]}")

    if resp.status_code != 200:
        return jsonify({
            'success': False,
            'done': False,
            'error': f'HTTP {resp.status_code}: {resp.text}'
        }), resp.status_code

    data = resp.json()
    done = data.get('done', False)

    if not done:
        return jsonify({'success': True, 'done': False})

    if 'error' in data:
        return jsonify({
            'success': False,
            'done': True,
            'error': data['error'].get('message', '未知错误')
        })

    videos = data.get('response', {}).get('videos', [])
    if not videos:
        return jsonify({'success': False, 'done': True, 'error': '未获取到视频数据'})

    video = videos[0]

    # 优先用 GCS URI
    gcs_uri = video.get('gcsUri', '')
    if gcs_uri:
        return jsonify({'success': True, 'done': True, 'gcs_uri': gcs_uri})

    # 没有 GCS URI，则处理 base64 数据
    import base64, uuid
    b64_data = video.get('bytesBase64Encoded', '')
    if not b64_data:
        return jsonify({'success': False, 'done': True, 'error': '视频数据为空'})

    # 保存到服务器本地
    os.makedirs('/tmp/veo_videos', exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp4"
    filepath = f"/tmp/veo_videos/{filename}"
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(b64_data))

    logging.info(f"💾 视频已保存: {filepath}")
    return jsonify({'success': True, 'done': True, 'video_url': f'/video/{filename}'})



@app.route('/video/<filename>')
def serve_video(filename):
    from flask import send_from_directory
    return send_from_directory('/tmp/veo_videos', filename)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
