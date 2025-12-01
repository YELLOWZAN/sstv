from flask import Flask
import os
from app.config import Config, config

def create_app(config_name='dev'):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 确保必要的目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
    
    # 注册蓝图
    from app.routes.main_routes import main_bp
    from app.routes.encryption_routes import encryption_bp
    from app.routes.decryption_routes import decryption_bp
    from app.routes.file_routes import file_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(encryption_bp, url_prefix='/api/encryption')
    app.register_blueprint(decryption_bp, url_prefix='/api/decryption')
    app.register_blueprint(file_bp, url_prefix='/api')
    
    return app