// 主JavaScript文件

// 模式状态管理
let currentMode = 'encrypt'; // 初始为加密模式
let currentStep = 1; // 当前操作步骤
let supportedModes = []; // 支持的SSTV模式列表
let recommendedMode = null; // 推荐的加密模式

// DOM元素缓存
const elements = {
  encryptTab: null,
  decryptTab: null,
  encryptContent: null,
  decryptContent: null,
  fileUploadArea: null,
  fileInput: null,
  imagePreview: null,
  modeSelector: null,
  recommendedModeContainer: null,
  encodeButton: null,
  decodeButton: null,
  recordButton: null,
  recordingIndicator: null,
  recordTimer: null,
  progressBar: null,
  progressSteps: null,
  audioPlayer: null,
  audioDownload: null,
  resultImage: null,
  resultContainer: null,
  fileListContainer: null
};

// 初始化函数
document.addEventListener('DOMContentLoaded', function() {
  // 初始化DOM元素缓存
  cacheDOMElements();
  
  // 加载支持的SSTV模式
  loadSupportedModes();
  
  // 设置事件监听器
  setupEventListeners();
  
  // 检查URL参数，可能包含从文件管理页面返回的状态
  checkUrlParams();
  
  // 初始化进度显示
  updateProgressSteps(currentStep);
});

// 缓存DOM元素
function cacheDOMElements() {
  elements.encryptTab = document.getElementById('encrypt-tab');
  elements.decryptTab = document.getElementById('decrypt-tab');
  elements.encryptContent = document.getElementById('encrypt-content');
  elements.decryptContent = document.getElementById('decrypt-content');
  elements.fileUploadArea = document.getElementById('file-upload-area');
  elements.fileInput = document.getElementById('file-input');
  elements.imagePreview = document.getElementById('image-preview');
  elements.modeSelector = document.getElementById('sstv-mode');
  elements.recommendedModeContainer = document.getElementById('recommended-mode');
  elements.encodeButton = document.getElementById('encode-button');
  elements.decodeButton = document.getElementById('decode-button');
  elements.recordButton = document.getElementById('record-button');
  elements.recordingIndicator = document.getElementById('recording-indicator');
  elements.recordTimer = document.getElementById('record-timer');
  elements.progressBar = document.getElementById('progress-bar');
  elements.progressSteps = document.querySelectorAll('.progress-card .step');
  elements.audioPlayer = document.getElementById('audio-player');
  elements.audioDownload = document.getElementById('audio-download');
  elements.resultImage = document.getElementById('result-image');
  elements.resultContainer = document.getElementById('result-container');
  elements.fileListContainer = document.getElementById('file-list');
}

// 设置事件监听器
function setupEventListeners() {
  // 模式切换事件
  if (elements.encryptTab) elements.encryptTab.addEventListener('click', () => switchMode('encrypt'));
  if (elements.decryptTab) elements.decryptTab.addEventListener('click', () => switchMode('decrypt'));
  
  // 文件上传区域点击事件
  if (elements.fileUploadArea && elements.fileInput) elements.fileUploadArea.addEventListener('click', () => elements.fileInput.click());
  
  // 文件选择变化事件
  if (elements.fileInput) elements.fileInput.addEventListener('change', handleFileSelect);
  
  // 拖放事件
  if (elements.fileUploadArea) {
    elements.fileUploadArea.addEventListener('dragover', handleDragOver);
    elements.fileUploadArea.addEventListener('dragleave', handleDragLeave);
    elements.fileUploadArea.addEventListener('drop', handleDrop);
  }
  
  // 加密按钮点击事件
  if (elements.encodeButton) elements.encodeButton.addEventListener('click', handleEncode);
  
  // 解密按钮点击事件
  if (elements.decodeButton) elements.decodeButton.addEventListener('click', handleDecode);
  
  // 录音按钮点击事件
  if (elements.recordButton) elements.recordButton.addEventListener('click', toggleRecording);
  
  // 文件管理按钮已移除，相关事件监听代码也已删除
  
  // 模式切换按钮点击事件（加密/解密）
  const encryptionModeBtn = document.getElementById('encryption-mode-btn');
  const decryptionModeBtn = document.getElementById('decryption-mode-btn');
  
  if (encryptionModeBtn) {
    encryptionModeBtn.addEventListener('click', () => {
      window.location.href = '/switch_mode/encryption';
    });
  }
  
  if (decryptionModeBtn) {
    decryptionModeBtn.addEventListener('click', () => {
      window.location.href = '/switch_mode/decryption';
    });
  }
}

// 切换加密/解密模式
function switchMode(mode) {
  // 如果已经是当前模式，则不执行任何操作
  if (currentMode === mode) return;
  
  currentMode = mode;
  
  // 更新UI状态
  if (mode === 'encrypt') {
    elements.encryptTab.classList.add('active');
    elements.decryptTab.classList.remove('active');
    elements.encryptContent.classList.remove('hidden');
    elements.decryptContent.classList.add('hidden');
  } else {
    elements.encryptTab.classList.remove('active');
    elements.decryptTab.classList.add('active');
    elements.encryptContent.classList.add('hidden');
    elements.decryptContent.classList.remove('hidden');
  }
  
  // 重置UI状态
  resetUI();
}

// 重置UI状态
function resetUI() {
  // 重置进度状态
  currentStep = 1;
  updateProgressSteps(currentStep);
  updateProgressBar(0);
  
  // 重置文件上传区域
  elements.fileUploadArea.classList.remove('active');
  elements.fileInput.value = '';
  
  // 重置预览
  elements.imagePreview.innerHTML = '';
  elements.resultImage.src = '';
  elements.resultContainer.classList.add('hidden');
  
  // 重置音频播放器
  elements.audioPlayer.src = '';
  elements.audioDownload.href = '';
  elements.audioPlayer.classList.add('hidden');
  
  // 重置录音状态
  if (window.recording) {
    stopRecording();
  }
}

// 加载支持的SSTV模式
function loadSupportedModes() {
  try {
    // 从后端API获取完整的SSTV模式列表
    fetch('/api/encryption/get_modes')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // 转换后端返回的模式数据格式为前端所需格式
          supportedModes = data.modes.map(mode => {
            // 根据模式名称添加描述
            let description = 'SSTV模式';
            
            // 添加更详细的描述信息
            if (mode.name.includes('Martin')) {
              description = '标准彩色模式';
              if (mode.name.includes('M2')) {
                description += '，更高分辨率';
              }
            } else if (mode.name.includes('Scottie')) {
              description = '彩色模式';
              if (mode.name.includes('S2')) {
                description += '，更高分辨率';
              } else if (mode.name.includes('DX')) {
                description += '，扩展版本';
              }
            } else if (mode.name.includes('Robot')) {
              description = '灰度模式';
              if (mode.name.includes('72')) {
                description += '，更高分辨率';
              }
            } else if (mode.name.includes('Pasokon')) {
              description = '日式SSTV模式';
            } else if (mode.name.startsWith('PD')) {
              description = 'PD系列彩色模式';
              // 添加分辨率信息
              description += ` (${mode.width}x${mode.height})`;
            } else if (mode.name.includes('Wraase')) {
              description = 'Wraase系列模式';
            }
            
            return {
              code: mode.name,
              name: mode.name,
              description: description
            };
          });
          
          // 设置默认推荐模式
          const defaultMode = supportedModes.find(mode => mode.code === 'MartinM1');
          recommendedMode = defaultMode || supportedModes[0];
          
          // 填充模式选择下拉框
          populateModeSelector(supportedModes);
          
          // 显示推荐模式
          displayRecommendedMode();
        } else {
          console.error('Error loading modes:', data.error);
          // 加载失败时使用回退的基础模式列表
          fallbackToBasicModes();
        }
      })
      .catch(error => {
        console.error('Error fetching SSTV modes:', error);
        // 网络错误时使用回退的基础模式列表
        fallbackToBasicModes();
      });
  } catch (error) {
    console.error('Error loading SSTV modes:', error);
    fallbackToBasicModes();
  }
}

// 回退到基础模式列表
function fallbackToBasicModes() {
  supportedModes = [
    { code: 'MartinM1', name: 'Martin M1', description: '标准彩色模式' },
    { code: 'MartinM2', name: 'Martin M2', description: '标准彩色模式，更高分辨率' },
    { code: 'ScottieS1', name: 'Scottie S1', description: '彩色模式' },
    { code: 'ScottieS2', name: 'Scottie S2', description: '彩色模式，更高分辨率' },
    { code: 'Robot36', name: 'Robot 36', description: '灰度模式' },
    { code: 'Robot72', name: 'Robot 72', description: '灰度模式，更高分辨率' }
  ];
  
  recommendedMode = supportedModes[0];
  populateModeSelector(supportedModes);
  displayRecommendedMode();
}

// 显示推荐模式
function displayRecommendedMode() {
  if (recommendedMode && elements.recommendedModeContainer) {
    elements.recommendedModeContainer.innerHTML = 
      `<div class="recommended-mode-info">
        <strong>推荐模式：</strong>${recommendedMode.name} (${recommendedMode.description})
      </div>`;
  }
}

// 填充模式选择下拉框
function populateModeSelector(modes) {
  if (!elements.modeSelector) return;
  
  elements.modeSelector.innerHTML = '<option value="">请选择SSTV模式</option>';
  
  modes.forEach(mode => {
    const option = document.createElement('option');
    option.value = mode.code;
    option.textContent = `${mode.name} (${mode.description})`;
    elements.modeSelector.appendChild(option);
  });
}

// 处理文件选择
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    processFile(file);
  }
}

// 处理拖放事件
function handleDragOver(event) {
  event.preventDefault();
  elements.fileUploadArea.classList.add('active');
}

function handleDragLeave(event) {
  elements.fileUploadArea.classList.remove('active');
}

function handleDrop(event) {
  event.preventDefault();
  elements.fileUploadArea.classList.remove('active');
  
  const file = event.dataTransfer.files[0];
  if (file) {
    processFile(file);
  }
}

// 处理文件
function processFile(file) {
  // 根据当前模式验证文件类型
  if (currentMode === 'encrypt') {
    if (!file.type.match('image.*')) {
      showNotification('请上传有效的图片文件', 'error');
      return;
    }
    displayImagePreview(file);
    // 获取推荐模式
    getRecommendedMode(file);
  } else {
    if (!file.type.match('audio.*')) {
      showNotification('请上传有效的音频文件', 'error');
      return;
    }
    displayAudioFileInfo(file);
  }
  
  // 更新进度
  currentStep = 2;
  updateProgressSteps(currentStep);
}

// 显示图片预览
function displayImagePreview(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = document.createElement('img');
    img.src = e.target.result;
    img.className = 'result-image';
    
    elements.imagePreview.innerHTML = '';
    elements.imagePreview.appendChild(img);
    elements.imagePreview.classList.remove('hidden');
  };
  reader.readAsDataURL(file);
}

// 显示音频文件信息
function displayAudioFileInfo(file) {
  elements.imagePreview.innerHTML = `
    <div class="audio-file-preview">
      <div class="audio-file-icon">🎵</div>
      <div class="file-name">${file.name}</div>
      <div class="file-meta">大小: ${formatFileSize(file.size)}</div>
    </div>
  `;
  elements.imagePreview.classList.remove('hidden');
}

// 获取推荐模式
async function getRecommendedMode(file) {
  try {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await fetch('/api/recommended-mode', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Failed to get recommended mode');
    }
    
    const data = await response.json();
    recommendedMode = data.recommended_mode;
    
    // 显示推荐模式
    if (recommendedMode && elements.recommendedModeContainer) {
      elements.recommendedModeContainer.innerHTML = `
        <div class="recommended-mode-title">推荐模式</div>
        <div class="recommended-mode-text">
          基于您的图片特征，我们推荐使用 <strong>${recommendedMode.name}</strong> 模式，
          它${recommendedMode.description}。
        </div>
      `;
      elements.recommendedModeContainer.classList.remove('hidden');
      
      // 自动选择推荐模式
      if (elements.modeSelector) {
        elements.modeSelector.value = recommendedMode.code;
      }
    }
  } catch (error) {
    console.error('Error getting recommended mode:', error);
    // 即使获取推荐模式失败，也不阻止用户继续操作
  }
}

// 处理加密
async function handleEncode() {
  const file = elements.fileInput.files[0];
  const mode = elements.modeSelector.value;
  
  if (!file) {
    showNotification('请先选择图片文件', 'error');
    return;
  }
  
  if (!mode) {
    showNotification('请选择SSTV模式', 'error');
    return;
  }
  
  try {
    // 显示进度
    currentStep = 3;
    updateProgressSteps(currentStep);
    updateProgressBar(33);
    
    const formData = new FormData();
    formData.append('image_file', file);
    formData.append('mode', mode);
    
    // 发送加密请求
    const response = await fetch('/api/encryption/encode_image', {
      method: 'POST',
      body: formData
    });
    
    updateProgressBar(66);
    
    if (!response.ok) {
      throw new Error('加密失败');
    }
    
    const data = await response.json();
    
    updateProgressBar(100);
    currentStep = 4;
    updateProgressSteps(currentStep);
    
    // 显示结果
    displayEncodeResult(data);
    
    showNotification('加密成功', 'success');
  } catch (error) {
    console.error('Error during encoding:', error);
    showNotification('加密失败: ' + error.message, 'error');
    // 重置进度
    updateProgressBar(0);
  }
}

// 处理解密
async function handleDecode() {
  const file = elements.fileInput.files[0];
  
  if (!file) {
    showNotification('请先选择音频文件', 'error');
    return;
  }
  
  try {
    // 显示进度
    currentStep = 3;
    updateProgressSteps(currentStep);
    updateProgressBar(33);
    
    const formData = new FormData();
    formData.append('audio_file', file);
    
    // 发送解密请求
    const response = await fetch('/api/decryption/decode_audio', {
      method: 'POST',
      body: formData
    });
    
    updateProgressBar(66);
    
    if (!response.ok) {
      throw new Error('解密失败');
    }
    
    const data = await response.json();
    
    updateProgressBar(100);
    currentStep = 4;
    updateProgressSteps(currentStep);
    
    // 显示结果
    displayDecodeResult(data);
    
    showNotification('解密成功', 'success');
  } catch (error) {
    console.error('Error during decoding:', error);
    showNotification('解密失败: ' + error.message, 'error');
    // 重置进度
    updateProgressBar(0);
  }
}

// 显示加密结果
function displayEncodeResult(data) {
  if (data.audio_url) {
    elements.audioPlayer.src = data.audio_url;
    elements.audioDownload.href = data.audio_url;
    elements.audioPlayer.classList.remove('hidden');
  }
}

// 显示解密结果
function displayDecodeResult(data) {
  if (data.image_url) {
    elements.resultImage.src = data.image_url;
    elements.resultContainer.classList.remove('hidden');
  }
}

// 更新进度条
function updateProgressBar(percentage) {
  if (elements.progressBar) {
    elements.progressBar.style.width = percentage + '%';
  }
}

// 更新进度步骤
function updateProgressSteps(activeStep) {
  elements.progressSteps.forEach((step, index) => {
    const stepNumber = index + 1;
    
    if (stepNumber < activeStep) {
      // 已完成的步骤
      step.classList.remove('active');
      step.classList.add('completed');
    } else if (stepNumber === activeStep) {
      // 当前活动步骤
      step.classList.add('active');
      step.classList.remove('completed');
    } else {
      // 未完成的步骤
      step.classList.remove('active', 'completed');
    }
  });
}

// 录音相关变量
let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let recordingTimerInterval = null;

// 切换录音状态
async function toggleRecording() {
  if (window.recording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

// 开始录音
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    
    mediaRecorder.addEventListener('dataavailable', event => {
      audioChunks.push(event.data);
    });
    
    mediaRecorder.addEventListener('stop', async () => {
      // 停止所有音轨
      stream.getTracks().forEach(track => track.stop());
      
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      await processRecordedAudio(audioBlob);
    });
    
    // 开始录音
    mediaRecorder.start();
    window.recording = true;
    
    // 更新UI
    elements.recordButton.classList.add('recording');
    elements.recordButton.innerHTML = '⏹️';
    elements.recordingIndicator.classList.remove('hidden');
    
    // 开始计时器
    startRecordingTimer();
    
    showNotification('开始录音', 'info');
  } catch (error) {
    console.error('Error starting recording:', error);
    showNotification('无法访问麦克风，请检查权限设置', 'error');
  }
}

// 停止录音
function stopRecording() {
  if (mediaRecorder && window.recording) {
    mediaRecorder.stop();
    window.recording = false;
    
    // 更新UI
    elements.recordButton.classList.remove('recording');
    elements.recordButton.innerHTML = '🎤';
    elements.recordingIndicator.classList.add('hidden');
    
    // 停止计时器
    stopRecordingTimer();
    
    showNotification('录音已停止，正在处理...', 'info');
  }
}

// 开始录音计时器
function startRecordingTimer() {
  recordingStartTime = Date.now();
  
  recordingTimerInterval = setInterval(() => {
    const duration = Date.now() - recordingStartTime;
    elements.recordTimer.textContent = formatDuration(duration);
  }, 1000);
}

// 停止录音计时器
function stopRecordingTimer() {
  clearInterval(recordingTimerInterval);
}

// 处理录制的音频
async function processRecordedAudio(audioBlob) {
  try {
    // 显示进度
    currentStep = 3;
    updateProgressSteps(currentStep);
    updateProgressBar(33);
    
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    formData.append('from_mic', 'true');
    
    // 发送录音解码请求
    const response = await fetch('/api/decryption/record_and_decode', {
      method: 'POST',
      body: formData
    });
    
    updateProgressBar(66);
    
    if (!response.ok) {
      throw new Error('解密失败');
    }
    
    const data = await response.json();
    
    updateProgressBar(100);
    currentStep = 4;
    updateProgressSteps(currentStep);
    
    // 显示结果
    displayDecodeResult(data);
    
    showNotification('录音解密成功', 'success');
  } catch (error) {
    console.error('Error processing recorded audio:', error);
    showNotification('录音解密失败: ' + error.message, 'error');
    // 重置进度
    updateProgressBar(0);
  }
}

// 检查URL参数
function checkUrlParams() {
  const urlParams = new URLSearchParams(window.location.search);
  const mode = urlParams.get('mode');
  
  if (mode === 'decrypt') {
    switchMode('decrypt');
  }
}

// 工具函数

// 显示通知
function showNotification(message, type = 'info') {
  // 创建通知元素
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // 添加到页面
  document.body.appendChild(notification);
  
  // 自动移除
  setTimeout(() => {
    notification.classList.add('fade-out');
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化时间
function formatDuration(ms) {
  const seconds = Math.floor((ms / 1000) % 60);
  const minutes = Math.floor((ms / (1000 * 60)) % 60);
  
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// 为通知添加样式
const style = document.createElement('style');
style.textContent = `
  .notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    animation: slideIn 0.3s ease;
  }
  
  .notification-success {
    background-color: var(--success-color);
  }
  
  .notification-error {
    background-color: var(--error-color);
  }
  
  .notification-info {
    background-color: var(--primary-color);
  }
  
  .notification-warning {
    background-color: var(--warning-color);
  }
  
  .notification.fade-out {
    animation: slideOut 0.3s ease;
  }
  
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);