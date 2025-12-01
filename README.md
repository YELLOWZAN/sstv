# SSTV 图像加密解密系统

## 项目概述

本应用是一个基于 Flask 开发的 Web 应用程序，用于实现慢扫描电视（Slow Scan Television, SSTV）图像与音频之间的相互转换。该系统支持多种 SSTV 模式，可以将图像加密为音频文件，或将包含 SSTV 信号的音频文件解码还原为图像。

## 功能特点

### 加密功能
- 支持多种 SSTV 模式（MartinM1/M2、ScottieS1/S2/DX、Robot36 等）
- 可上传任意图像文件并转换为对应 SSTV 模式的音频文件
- 支持音频文件下载功能

### 解密功能
- 支持上传 SSTV 音频文件并解码为图像
- 自动识别音频中的 SSTV 模式
- 支持解码后的图像下载功能

### 系统特性
- 基于 Flask 的 Web 界面，操作简便
- 支持加密/解密模式切换
- 文件存储和管理功能
- 响应式设计，适配不同设备

## 环境要求

- Python 3.6+
- 依赖包见 requirements.txt

## 安装与部署

### 克隆项目

```bash
git clone <项目仓库地址>
cd sstv
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

开发环境下可以使用默认配置，生产环境建议设置以下环境变量：

```bash
# 生产环境密钥
export SECRET_KEY="your-secret-key"

# 配置类型
export FLASK_CONFIG="prod"
```

### 运行应用

#### 开发环境

```bash
python main.py
```

应用将在 http://localhost:3000 启动。

#### 生产环境

建议使用 Gunicorn 或 uWSGI 作为 WSGI 服务器，并配合 Nginx 使用。

```bash
# 使用 Gunicorn 启动
gunicorn -w 4 -b 0.0.0.0:3000 "app:create_app('prod')"
```

## 使用方法

### 图像加密

1. 访问应用首页，确保当前处于加密模式
2. 点击选择图像文件按钮，上传需要加密的图像
3. 从下拉菜单中选择需要的 SSTV 模式
4. 点击「加密」按钮，等待处理完成
5. 加密完成后，可点击下载按钮获取生成的音频文件

### 图像解密

1. 访问应用首页，点击导航栏中的解密模式
2. 点击选择音频文件按钮，上传包含 SSTV 信号的音频文件
3. 点击「解密」按钮，等待处理完成
4. 解密完成后，可查看解码后的图像并选择下载

## 项目结构

```
sstv/
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用初始化
│   ├── config.py           # 配置文件
│   ├── decryption/         # 解密相关模块
│   │   ├── __init__.py
│   │   └── sstv_decoder.py # SSTV解码器
│   ├── encryption/         # 加密相关模块
│   │   ├── __init__.py
│   │   └── sstv_encoder.py # SSTV编码器
│   ├── routes/             # 路由模块
│   │   ├── __init__.py
│   │   ├── decryption_routes.py  # 解密路由
│   │   ├── encryption_routes.py  # 加密路由
│   │   ├── file_routes.py        # 文件路由（已移除）
│   │   └── main_routes.py        # 主路由
│   ├── static/             # 静态资源
│   │   ├── css/            # 样式文件
│   │   ├── images/         # 图片资源
│   │   └── js/             # JavaScript文件
│   ├── templates/          # HTML模板
│   │   ├── base.html       # 基础模板
│   │   └── index.html      # 主页面
│   └── utils/              # 工具类
│       ├── __init__.py
│       └── file_manager.py # 文件管理工具
├── data/                   # 数据存储目录（音频和图像）
├── uploads/                # 文件上传目录
├── .gitignore              # Git忽略文件
├── main.py                 # 应用入口
├── requirements.txt        # 依赖列表
```

## 配置说明

应用配置位于 `app/config.py` 中，主要配置项包括：

- `SECRET_KEY`: 应用密钥，用于会话加密
- `UPLOAD_FOLDER`: 文件上传目录
- `DATA_FOLDER`: 数据存储目录
- `SSTV_SAMPLE_RATE`: SSTV 音频采样率
- `SSTV_BITS`: SSTV 音频位深度

应用支持两种配置环境：
- `DevelopmentConfig`: 开发环境配置，开启调试模式
- `ProductionConfig`: 生产环境配置，关闭调试模式

## 开发指南

### 添加新的 SSTV 模式

在 `app/encryption/sstv_encoder.py` 文件中的 `SUPPORTED_MODES` 列表中添加新的模式：

```python
SUPPORTED_MODES = [
    # 现有模式
    ('新模式名称', color.新模式类),
]
```

### 扩展功能

如果需要扩展功能，可以按照以下步骤进行：

1. 在相应模块中添加新功能
2. 在 `routes` 目录中创建或修改路由处理函数
3. 更新前端模板或静态文件

## 依赖说明

主要依赖包包括：
- Flask: Web 框架
- pysstv: SSTV 编码解码库
- numpy: 数值计算
- Pillow: 图像处理
- soundfile: 音频文件处理

详细依赖列表见 `requirements.txt` 文件。

## 注意事项

1. 上传的图像文件和音频文件会被保存在服务器上，请注意管理存储空间
2. 解码过程可能会因为音频质量、采样率等因素影响解码成功率
3. 生产环境部署时请确保设置安全的密钥和适当的文件权限

## 许可证

[在此添加许可证信息]
