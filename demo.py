#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSTV音频生成器
用于将图片转换为Slow Scan Television (SSTV)音频信号
支持多种SSTV模式
"""

import os
import sys
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

def get_sstv_mode_info(mode_class):
    """
    获取SSTV模式信息
    
    Args:
        mode_class: SSTV模式类
    
    Returns:
        tuple: (宽度, 高度, VIS码)
    """
    try:
        # 创建临时空白图像用于获取模式信息
        temp_img = Image.new('RGB', (10, 10), color='black')
        # 使用位置参数实例化，避免关键字参数不兼容问题
        instance = mode_class(temp_img, 44100, 16)
        
        width = getattr(instance, "WIDTH", 320)
        height = getattr(instance, "HEIGHT", 240)
        vis_code = getattr(instance, "VIS_CODE", 0)
        
        return width, height, vis_code
    except Exception as e:
        print(f"获取模式信息时出错: {e}")
        return 320, 240, 0

def resize_image(img, target_width, target_height):
    """
    调整图片尺寸
    
    Args:
        img: PIL Image对象
        target_width: 目标宽度
        target_height: 目标高度
    
    Returns:
        PIL Image对象: 调整后的图片
    """
    try:
        # 使用LANCZOS滤镜进行高质量缩放
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"调整图片尺寸时出错: {e}")
        raise

def generate_sstv_audio(image_path, output_path, mode_class):
    """
    生成SSTV音频
    
    Args:
        image_path: 输入图片路径
        output_path: 输出音频路径
        mode_class: SSTV模式类
    
    Returns:
        bool: 是否成功生成
    """
    sample_rate = 44100
    bits = 16
    
    try:
        # 处理图片
        with Image.open(image_path) as img:
            # 确保转换为RGB模式
            img_rgb = img.convert("RGB")
            
            # 创建临时实例获取目标尺寸
            temp_instance = mode_class(img_rgb, sample_rate, bits)
            target_w = getattr(temp_instance, "WIDTH", 320)
            target_h = getattr(temp_instance, "HEIGHT", 240)
            
            # 调整图片尺寸
            resized_img = resize_image(img_rgb, target_w, target_h)
            
            # 使用调整后的图片创建最终实例
            instance = mode_class(resized_img, sample_rate, bits)
            
            # 生成音频数据
            print("正在生成SSTV音频...")
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
            return True
            
    except FileNotFoundError as e:
        print(f"错误：找不到文件 - {e}")
        return False
    except Exception as e:
        print(f"生成失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    主函数，处理用户输入并执行音频生成
    """
    try:
        # 显示支持的模式列表
        print("支持的SSTV加密模式列表：")
        for i, (mode_name, mode_class) in enumerate(SUPPORTED_MODES, 1):
            width, height, vis_code = get_sstv_mode_info(mode_class)
            print(f"{i}. {mode_name}: {mode_name} (分辨率: {width}x{height}, VIS码: {vis_code})")
        
        # 获取用户输入的模式编号
        while True:
            try:
                mode_idx = int(input("\n请输入模式编号（1-17）：")) - 1
                if 0 <= mode_idx < len(SUPPORTED_MODES):
                    break
                print("错误：模式编号无效，请重新输入")
            except ValueError:
                print("错误：请输入有效的数字")
        
        mode_name, mode_class = SUPPORTED_MODES[mode_idx]
        
        # 获取用户输入的图片路径
        while True:
            image_path = input("\n请输入图片文件路径：")
            if os.path.isfile(image_path):
                break
            print("错误：图片文件不存在，请重新输入")
        
        # 获取用户输入的输出音频路径
        while True:
            output_path = input("\n请输入输出音频路径（建议.wav）：")
            if output_path.strip():
                # 确保输出路径有.wav扩展名
                if not output_path.lower().endswith('.wav'):
                    output_path += '.wav'
                break
            print("错误：输出路径不能为空")
        
        # 生成音频
        success = generate_sstv_audio(image_path, output_path, mode_class)
        
        if success:
            print("\n程序执行成功！")
        else:
            print("\n程序执行失败！")
            return 1
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 2
    except Exception as e:
        print(f"\n程序发生意外错误：{e}")
        import traceback
        traceback.print_exc()
        return 3
    
    return 0

if __name__ == "__main__":
    sys.exit(main())