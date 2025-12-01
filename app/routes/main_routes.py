from flask import Blueprint, render_template, redirect, url_for, session

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页路由"""
    # 获取当前模式，如果不存在则默认为加密模式
    mode = session.get('mode', 'encryption')
    return render_template('index.html', mode=mode)

@main_bp.route('/switch_mode/<mode>')
def switch_mode(mode):
    """切换加密/解密模式"""
    if mode in ['encryption', 'decryption']:
        session['mode'] = mode
    return redirect(url_for('main.index'))