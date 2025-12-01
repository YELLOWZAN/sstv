from flask import Blueprint, request, jsonify, redirect, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.encryption.sstv_encoder import SSTVEncoder
from app.config import Config

# 创建蓝图
encryption_bp = Blueprint('encryption', __name__)

@encryption_bp.route('/encode_image', methods=['POST'])
def encode_image():
    """加密图像为音频文件"""
    try:
        # 检查是否有文件上传
        if 'image_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '请选择图像文件'
            })
        
        file = request.files['image_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '请选择有效的图像文件'
            })
        
        # 获取SSTV模式
        mode_name = request.form.get('mode', 'MartinM1')  # 默认使用MartinM1模式，使用模式名称而非ID
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        name, ext = os.path.splitext(filename)
        image_filename = f"{name}-{timestamp}{ext}"
        image_path = os.path.join(Config.UPLOAD_FOLDER, image_filename)
        file.save(image_path)
        
        # 生成输出音频路径
        audio_filename = f"{name}-{timestamp}.wav"
        audio_path = os.path.join(Config.DATA_FOLDER, audio_filename)
        
        # 加密图像为音频
        result = SSTVEncoder.encode_image(image_path, audio_path, mode_name)
        
        if result['success']:
            return jsonify({
                'success': True,
                'audio_url': url_for('files.download_file', folder='data', filename=audio_filename),
                'mode': result['mode'],
                'audio_path': audio_filename,
                'image_path': image_filename
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@encryption_bp.route('/get_modes', methods=['GET'])
def get_modes():
    """获取所有支持的SSTV模式"""
    try:
        modes = SSTVEncoder.get_supported_modes()
        return jsonify({
            'success': True,
            'modes': modes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@encryption_bp.route('/get_recommended_mode', methods=['POST'])
def get_recommended_mode():
    """根据图像特征推荐合适的加密方式"""
    try:
        if 'image_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '请选择图像文件'
            })
        
        file = request.files['image_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '请选择有效的图像文件'
            })
        
        # 临时保存文件以分析
        temp_image_path = os.path.join(Config.UPLOAD_FOLDER, 'temp_' + secure_filename(file.filename))
        file.save(temp_image_path)
        
        # 推荐模式
        recommended_mode = SSTVEncoder.recommend_mode(temp_image_path)
        
        # 删除临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        return jsonify({
            'success': True,
            'recommended_mode': recommended_mode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })