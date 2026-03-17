#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Veo 3.1 视频生成 Web 应用后端
使用 :predictLongRunning 端点 + :fetchPredictOperation 轮询
"""
import os
import time
import logging
import requests as http_requests
from flask import Flask, render_template, request, jsonify

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'red-atlas-490409-v1').strip()
LOCATION = "us-central1"
GCS_OUTPUT = "gs://red-atlas-video-assets/outputs/"

# Veo 3.1 正确端点
VEO_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1"
    f"/projects/{PROJECT_ID}/locations/{LOCATION}"
    f"/publishers/google/models/veo-3.1-generate-001:predictLongRunning"
)

# 轮询状态专用端点（官方文档要求用 fetchPredictOperation，POST 方式）
FETCH_OP_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1"
    f"/projects/{PROJECT_ID}/locations/{LOCATION}"
    f"/publishers/google/models/veo-3.1-generate-001:fetchPredictOperation"
)


def get_access_token():
    """获取 Google Cloud 访问令牌"""
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request

        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            logging.error("未找到凭证文件，请设置 GOOGLE_APPLICATION_CREDENTIALS")
            return None

        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        logging.error(f"获取 Token 失败: {e}")
        return None


def poll_operation(operation_name: str, token: str, max_wait_seconds: int = 300):
    """
    轮询 Long-Running Operation 直到完成
    返回 (success: bool, result_or_error: dict)
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    interval = 10  # 每 10 秒轮询一次
    elapsed = 0

    while elapsed < max_wait_seconds:
        time.sleep(interval)
        elapsed += interval

        # 用 POST :fetchPredictOperation 查询状态，传完整 operation name
        resp = http_requests.post(
            FETCH_OP_URL,
            headers=headers,
            json={"operationName": operation_name},
            timeout=30,
        )
        logging.info(f"🔄 轮询 [{elapsed}s] 状态: {resp.status_code}")

        if resp.status_code != 200:
            return False, {"error": f"轮询失败 HTTP {resp.status_code}: {resp.text}"}

        data = resp.json()
        done = data.get("done", False)

        if not done:
            logging.info("⏳ 视频还在生成中...")
            continue

        # 完成，检查是否有错误
        if "error" in data:
            return False, {"error": data["error"].get("message", "未知错误")}

        # 成功，从 response 里取视频 URI
        response_payload = data.get("response", {})
        videos = response_payload.get("videos", [])
        if videos:
            gcs_uri = videos[0].get("gcsUri", "")
            return True, {"gcs_uri": gcs_uri, "videos": videos}

        return True, {"raw_response": response_payload}

    return False, {"error": f"超时：{max_wait_seconds} 秒内未完成"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """提交生成任务，同步等待结果（最多 5 分钟）"""
    try:
        body = request.get_json(silent=True) or {}
        prompt = body.get('prompt', '').strip()
        if not prompt:
            return jsonify({'success': False, 'error': '请输入提示词'}), 400

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
                "aspectRatio": "16:9",
                "durationSeconds": 8,
                "outputConfig": {
                    "gcsDestination": {
                        "outputUriPrefix": GCS_OUTPUT
                    }
                }
            }
        }

        logging.info(f"🚀 提交生成请求: {VEO_URL}")
        resp = http_requests.post(VEO_URL, headers=headers, json=payload, timeout=60)
        logging.info(f"📊 响应状态: {resp.status_code} | 内容: {resp.text[:300]}")

        if resp.status_code not in (200, 202):
            return jsonify({
                'success': False,
                'error': f'HTTP {resp.status_code}: {resp.text}'
            }), resp.status_code

        data = resp.json()
        operation_name = data.get('name', '')
        logging.info(f"✅ 任务已提交，Operation: {operation_name}")

        # 同步等待结果（最多 5 分钟）
        success, result = poll_operation(operation_name, token, max_wait_seconds=300)

        if success:
            gcs_uri = result.get("gcs_uri", "")
            return jsonify({
                'success': True,
                'operation_name': operation_name,
                'gcs_uri': gcs_uri,
                'message': '🎉 视频生成完成！'
            })
        else:
            return jsonify({
                'success': False,
                'operation_name': operation_name,
                'error': result.get('error', '生成失败')
            }), 500

    except Exception as e:
        logging.exception("❌ 请求异常")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """
    异步模式：前端主动查询 operation 状态
    GET /status?operation_name=projects/.../operations/xxx
    """
    operation_name = request.args.get('operation_name', '').strip()
    if not operation_name:
        return jsonify({'success': False, 'error': '缺少 operation_name 参数'}), 400

    token = get_access_token()
    if not token:
        return jsonify({'success': False, 'error': '认证失败'}), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 用 POST :fetchPredictOperation 查询状态
    resp = http_requests.post(
        FETCH_OP_URL,
        headers=headers,
        json={"operationName": operation_name},
        timeout=30,
    )
    
    if resp.status_code != 200:
        return jsonify({'success': False, 'error': f'HTTP {resp.status_code}: {resp.text}'}), resp.status_code

    data = resp.json()
    done = data.get("done", False)

    if not done:
        return jsonify({'success': True, 'done': False, 'message': '⏳ 生成中...'})

    if "error" in data:
        return jsonify({'success': False, 'done': True, 'error': data["error"].get("message")})

    videos = data.get("response", {}).get("videos", [])
    gcs_uri = videos[0].get("gcsUri", "") if videos else ""
    return jsonify({'success': True, 'done': True, 'gcs_uri': gcs_uri, 'videos': videos})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
