from flask import Blueprint, request, jsonify, send_from_directory
import os
from app.config import Config
from app.utils.file_manager import FileManager

# 创建蓝图
file_bp = Blueprint('files', __name__)

@file_bp.route('/files', methods=['GET'])
def get_files():
    """获取所有文件列表"""
    try:
        # 获取文件类型过滤参数
        file_type = request.args.get('type', 'all')  # 'image', 'audio', 'all'
        
        file_manager = FileManager()
        
        # 获取上传文件夹中的图像文件
        images = file_manager.list_files(Config.UPLOAD_FOLDER, file_type='image')
        
        # 获取data文件夹中的音频文件
        audios = file_manager.list_files(Config.DATA_FOLDER, file_type='audio')
        
        # 合并结果
        if file_type == 'image':
            files = images
        elif file_type == 'audio':
            files = audios
        else:
            files = images + audios
        
        # 按时间倒序排列
        files.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@file_bp.route('/download_file/<folder>/<filename>', methods=['GET'])
def download_file(filename, folder):
    """下载文件"""
    try:
        # 确定文件路径
        if folder == 'uploads':
            file_path = Config.UPLOAD_FOLDER
        elif folder == 'data':
            file_path = Config.DATA_FOLDER
        else:
            return jsonify({
                'success': False,
                'error': '无效的文件夹路径'
            })
        
        # 安全检查：确保文件名合法且文件存在
        if not os.path.isfile(os.path.join(file_path, filename)):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            })
        
        return send_from_directory(file_path, filename, as_attachment=True)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@file_bp.route('/delete_file', methods=['POST'])
def delete_file():
    """删除单个文件"""
    try:
        data = request.json
        filename = data.get('filename')
        folder = data.get('folder')
        
        if not filename or not folder:
            return jsonify({
                'success': False,
                'error': '缺少文件名或文件夹信息'
            })
        
        # 确定文件路径
        if folder == 'uploads':
            file_path = Config.UPLOAD_FOLDER
        elif folder == 'data':
            file_path = Config.DATA_FOLDER
        else:
            return jsonify({
                'success': False,
                'error': '无效的文件夹路径'
            })
        
        # 安全检查：确保文件存在
        full_path = os.path.join(file_path, filename)
        if not os.path.isfile(full_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            })
        
        # 删除文件
        file_manager = FileManager()
        file_manager.delete_file(full_path)
        
        return jsonify({
            'success': True,
            'message': '文件删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@file_bp.route('/batch_delete_files', methods=['POST'])
def batch_delete_files():
    """批量删除文件"""
    try:
        data = request.json
        files = data.get('files', [])
        
        if not files:
            return jsonify({
                'success': False,
                'error': '请选择要删除的文件'
            })
        
        file_manager = FileManager()
        deleted_count = 0
        failed_count = 0
        
        for file_info in files:
            filename = file_info.get('filename')
            folder = file_info.get('folder')
            
            if not filename or not folder:
                failed_count += 1
                continue
            
            # 确定文件路径
            if folder == 'uploads':
                file_path = Config.UPLOAD_FOLDER
            elif folder == 'data':
                file_path = Config.DATA_FOLDER
            else:
                failed_count += 1
                continue
            
            # 删除文件
            full_path = os.path.join(file_path, filename)
            if os.path.isfile(full_path):
                file_manager.delete_file(full_path)
                deleted_count += 1
            else:
                failed_count += 1
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'failed_count': failed_count,
            'message': f'批量删除完成：成功{deleted_count}个，失败{failed_count}个'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })