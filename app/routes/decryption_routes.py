from flask import Blueprint, request, jsonify, redirect, url_for, send_from_directory
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.decryption.sstv_decoder import SSTVDecoder
from app.config import Config
from app.utils.file_manager import FileManager

# 创建蓝图
decryption_bp = Blueprint('decryption', __name__)

@decryption_bp.route('/decode_audio', methods=['POST'])
def decode_audio():
    """解码音频文件"""
    try:
        # 检查是否有文件上传
        if 'audio_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '请选择音频文件'
            })
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '请选择有效的音频文件'
            })
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        name, ext = os.path.splitext(filename)
        audio_filename = f"{name}-{timestamp}{ext}"
        audio_path = os.path.join(Config.UPLOAD_FOLDER, audio_filename)
        file.save(audio_path)
        
        # 生成输出图像路径
        image_filename = f"decoded-{name}-{timestamp}.jpg"
        image_path = os.path.join(Config.DATA_FOLDER, image_filename)
        
        # 解码音频
        result = SSTVDecoder.decode_audio(audio_path, image_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'image_url': url_for('files.download_file', filename=image_filename, folder='data'),
                'mode': result['mode'],
                'image_path': image_filename
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@decryption_bp.route('/record_and_decode', methods=['POST'])
def record_and_decode():
    """录音并解码"""
    try:
        # 获取录音时长
        duration = request.form.get('duration', 10, type=int)
        
        # 生成输出图像路径
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        image_filename = f"decoded-mic-{timestamp}.jpg"
        image_path = os.path.join(Config.DATA_FOLDER, image_filename)
        
        # 录音并解码
        result = SSTVDecoder.record_and_decode(image_path, duration)
        
        if result['success']:
            return jsonify({
                'success': True,
                'image_url': url_for('files.download_file', filename=image_filename, folder='data'),
                'mode': result['mode'],
                'image_path': image_filename
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })