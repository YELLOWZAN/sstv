from app import create_app
import os

# 获取配置类型
config_name = os.environ.get('FLASK_CONFIG', 'default')

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 指定端口为3000，启动应用
    app.run(host='0.0.0.0', port=3000, debug=True)