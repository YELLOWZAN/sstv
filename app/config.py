import os
from datetime import datetime

class Config:
    """应用配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-sstv-app'
    DEBUG = False
    TESTING = False
    
    # 文件存储配置
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')
    
    # 文件命名格式
    @staticmethod
    def generate_filename(original_filename, prefix=''):
        """生成带时间戳的文件名"""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        name, ext = os.path.splitext(original_filename)
        if prefix:
            return f"{prefix}-{name}-{timestamp}{ext}"
        return f"{name}-{timestamp}{ext}"
    
    # SSTV配置
    SSTV_SAMPLE_RATE = 44100
    SSTV_BITS = 16
    
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY')  # 生产环境必须设置环境变量

# 配置映射
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}

# 为了向后兼容，添加config别名
config = config_by_name