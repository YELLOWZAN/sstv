import os
import shutil
import time
from datetime import datetime

class FileManager:
    """文件管理类"""
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件基本信息"""
        try:
            stat_info = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat_info.st_size,
                'created_at': datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified_at': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': stat_info.st_mtime,  # 添加时间戳用于排序
                'type': 'image' if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) else 'audio',
                'relative_path': os.path.relpath(file_path)
            }
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    @staticmethod
    def get_files_in_directory(directory):
        """获取目录中所有文件的信息"""
        files_info = []
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_info = FileManager.get_file_info(file_path)
                    if file_info:
                        files_info.append(file_info)
        except Exception as e:
            print(f"获取目录文件失败: {e}")
        return files_info
    
    @staticmethod
    def list_files(directory, file_type='all'):
        """列出指定目录中的文件，支持按类型过滤"""
        files = FileManager.get_files_in_directory(directory)
        
        if file_type == 'all':
            return files
        
        # 根据文件类型过滤
        filtered_files = []
        for file in files:
            # 添加folder字段
            file['folder'] = os.path.basename(directory)
            
            # 检查文件扩展名
            ext = os.path.splitext(file['name'])[1].lower()
            if file_type == 'image' and ext in ['.jpg', '.jpeg', '.png', '.gif']:
                filtered_files.append(file)
            elif file_type == 'audio' and ext in ['.wav', '.mp3', '.flac']:
                filtered_files.append(file)
        
        return filtered_files
    
    @staticmethod
    def delete_file(file_path):
        """删除单个文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    @staticmethod
    def delete_files(file_paths):
        """批量删除文件"""
        deleted_count = 0
        for file_path in file_paths:
            if FileManager.delete_file(file_path):
                deleted_count += 1
        return deleted_count
    
    @staticmethod
    def get_file_size_formatted(size_bytes):
        """将文件大小格式化为人类可读形式"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    @staticmethod
    def clean_old_files(directory, max_age_hours=24):
        """清理指定时间之前的旧文件"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        deleted_count = 0
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        if FileManager.delete_file(file_path):
                            deleted_count += 1
        except Exception as e:
            print(f"清理旧文件失败: {e}")
        
        return deleted_count