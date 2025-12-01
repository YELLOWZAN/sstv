import os
import numpy as np
from PIL import Image
import soundfile as sf
from pysstv import color

# 支持的SSTV模式列表
SUPPORTED_MODES = [
    ('MartinM1', color.MartinM1),
    ('MartinM2', color.MartinM2),
    ('ScottieS1', color.ScottieS1),
    ('ScottieS2', color.ScottieS2),
    ('ScottieDX', color.ScottieDX),
    ('Robot36', color.Robot36),
    ('PasokonP3', color.PasokonP3),
    ('PasokonP5', color.PasokonP5),
    ('PasokonP7', color.PasokonP7),
    ('PD90', color.PD90),
    ('PD120', color.PD120),
    ('PD160', color.PD160),
    ('PD180', color.PD180),
    ('PD240', color.PD240),
    ('PD290', color.PD290),
    ('WraaseSC2120', color.WraaseSC2120),
    ('WraaseSC2180', color.WraaseSC2180)
]

class SSTVEncoder:
    """SSTV编码器类"""
    
    @staticmethod
    def get_supported_modes():
        """获取所有支持的SSTV模式"""
        modes_info = []
        for mode_name, mode_class in SUPPORTED_MODES:
            try:
                width, height, vis_code = SSTVEncoder.get_mode_info(mode_class)
                modes_info.append({
                    'name': mode_name,
                    'width': width,
                    'height': height,
                    'vis_code': vis_code
                })
            except Exception as e:
                print(f"获取{mode_name}模式信息失败: {e}")
        return modes_info
    
    @staticmethod
    def get_mode_info(mode_class):
        """获取SSTV模式信息"""
        # 创建临时空白图像用于获取模式信息
        temp_img = Image.new('RGB', (10, 10), color='black')
        # 使用位置参数实例化，避免关键字参数不兼容问题
        instance = mode_class(temp_img, 44100, 16)
        
        width = getattr(instance, "WIDTH", 320)
        height = getattr(instance, "HEIGHT", 240)
        vis_code = getattr(instance, "VIS_CODE", 0)
        
        return width, height, vis_code
    
    @staticmethod
    def recommend_mode(image_path):
        """根据图像特征推荐合适的SSTV模式"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # 根据图像分辨率推荐模式
                if width <= 320 and height <= 240:
                    # 低分辨率图像推荐Robot36
                    return 'Robot36'
                elif width <= 640 and height <= 496:
                    # 中等分辨率图像推荐PD120
                    return 'PD120'
                else:
                    # 高分辨率图像推荐PD290
                    return 'PD290'
        except Exception as e:
            print(f"推荐模式时出错: {e}")
            return 'PD90'  # 默认推荐
    
    @staticmethod
    def resize_image(img, target_width, target_height):
        """调整图片尺寸"""
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def encode_image(image_path, output_path, mode_name, sample_rate=44100, bits=16):
        """将图像编码为SSTV音频"""
        try:
            # 查找对应的模式类
            mode_class = None
            for name, cls in SUPPORTED_MODES:
                if name == mode_name:
                    mode_class = cls
                    break
            
            if not mode_class:
                raise ValueError(f"不支持的模式: {mode_name}")
            
            # 处理图片
            with Image.open(image_path) as img:
                # 确保转换为RGB模式
                img_rgb = img.convert("RGB")
                
                # 创建临时实例获取目标尺寸
                temp_instance = mode_class(img_rgb, sample_rate, bits)
                target_w = getattr(temp_instance, "WIDTH", 320)
                target_h = getattr(temp_instance, "HEIGHT", 240)
                
                # 调整图片尺寸
                resized_img = SSTVEncoder.resize_image(img_rgb, target_w, target_h)
                
                # 使用调整后的图片创建最终实例
                instance = mode_class(resized_img, sample_rate, bits)
                
                # 生成音频数据
                print(f"正在使用{mode_name}模式生成SSTV音频...")
                audio_data = instance.gen_samples()
                
                # 处理生成器类型的结果
                if hasattr(audio_data, '__iter__') and not isinstance(audio_data, (list, np.ndarray)):
                    print("正在处理音频生成器...")
                    audio_data = list(audio_data)
                
                # 格式转换
                if isinstance(audio_data, list):
                    audio_data = np.array(audio_data, dtype=np.float32)
                
                # 确保数据类型正确
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                
                # 归一化和裁剪
                audio_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # 保存音频
                sf.write(output_path, audio_data, sample_rate, subtype=f"PCM_{bits}")
                print(f"音频生成成功，路径：{output_path}")
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'mode': mode_name,
                    'sample_rate': sample_rate,
                    'bits': bits
                }
                
        except Exception as e:
            print(f"编码失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }