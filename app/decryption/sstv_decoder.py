import os
import numpy as np
import wave
from PIL import Image
import soundfile as sf
import pysstv

class SSTVDecoder:
    """SSTV解码器类"""
    
    @staticmethod
    def decode_audio(audio_path, output_path):
        """从SSTV音频解码图像"""
        try:
            # 读取音频文件
            audio_data, sample_rate = sf.read(audio_path)
            
            # 如果是立体声，转换为单声道
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # 转换为16位整数
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # 使用通用的解码方式
            # 尝试直接使用pysstv中的核心功能
            from pysstv import SSTV
            
            # 尝试解码（简化版本）
            # 实际使用时可能需要根据具体pysstv版本调整
            sstv = SSTV(44100, 16)
            sstv.write_audio(audio_data)
            img = sstv.render()
            
            # 保存解码后的图像
            img.save(output_path)
            
            return {
                "success": True,
                "message": "成功解码音频",
                "output_path": output_path
            }
            
        except Exception as e:
            # 如果直接解码失败，返回错误信息
            return {
                "success": False,
                "message": f"解码过程出错: {str(e)}"
            }
    
    @staticmethod
    def record_and_decode(output_image_path, duration=10):
        """通过麦克风录制音频并解码图像"""
        try:
            # 检查系统并导入适当的录音模块
            import platform
            system = platform.system()
            
            audio_data = None
            sample_rate = 44100
            
            if system == 'Windows':
                # Windows系统使用pyaudio
                import pyaudio
                
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=sample_rate,
                                input=True,
                                frames_per_buffer=1024)
                
                print(f"开始录制{duration}秒...")
                frames = []
                for _ in range(0, int(sample_rate / 1024 * duration)):
                    data = stream.read(1024)
                    frames.append(data)
                
                print("录制完成，正在处理...")
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                # 转换为numpy数组
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                audio_data = audio_data.astype(np.float32) / 32767.0
            elif system == 'Linux':
                # Linux系统使用sounddevice
                import sounddevice as sd
                
                print(f"开始录制{duration}秒...")
                audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
                sd.wait()
                print("录制完成，正在处理...")
            elif system == 'Darwin':  # macOS
                # macOS系统使用sounddevice
                import sounddevice as sd
                
                print(f"开始录制{duration}秒...")
                audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
                sd.wait()
                print("录制完成，正在处理...")
            else:
                return {
                    'success': False,
                    'error': f'不支持的操作系统: {system}'
                }
            
            if audio_data is None:
                return {
                    'success': False,
                    'error': '无法录制音频'
                }
            
            # 保存临时音频文件
            temp_audio_path = os.path.join(os.path.dirname(output_image_path), 'temp_recording.wav')
            sf.write(temp_audio_path, audio_data, sample_rate)
            
            # 解码录制的音频
            result = SSTVDecoder.decode_audio(temp_audio_path, output_image_path)
            
            # 删除临时文件
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            
            return result
        except Exception as e:
            print(f"录音解码失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }