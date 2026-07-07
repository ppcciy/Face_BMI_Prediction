<template>
  <div class="app-container">
    <div class="header">
      <h1 class="title">Face BMI Prediction System</h1>
      <p class="subtitle">Upload a face image to predict BMI</p>
    </div>

    <div class="main-card">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
        accept="image/*"
        drag
        class="upload-area"
      >
        <div v-if="!previewUrl" class="upload-placeholder">
          <el-icon class="upload-icon"><Upload /></el-icon>
          <div class="upload-text">Drop image here or <em>click to upload</em></div>
          <div class="upload-tip">Supports JPG / PNG / WEBP</div>
        </div>
        <div v-else class="preview-wrapper">
          <img :src="previewUrl" alt="Preview" class="preview-image" />
        </div>
      </el-upload>

      <div class="action-row">
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          :disabled="!selectedFile"
          @click="handlePredict"
          class="predict-btn"
        >
          <el-icon v-if="!loading"><Cpu /></el-icon>
          {{ loading ? 'Predicting...' : 'Predict BMI' }}
        </el-button>
        <el-button
          v-if="selectedFile"
          size="large"
          @click="handleReset"
        >
          Reset
        </el-button>
      </div>

      <transition name="el-fade-in">
        <div v-if="result !== null" class="result-section" :class="result.success ? 'result-success' : 'result-error'">
          <template v-if="result.success">
            <div class="result-label">Predicted BMI</div>
            <div class="result-value">{{ result.bmi.toFixed(2) }}</div>
            <div class="result-category">
              Category: <strong>{{ bmiCategory(result.bmi) }}</strong>
            </div>
          </template>
          <template v-else>
            <el-icon class="error-icon"><CircleClose /></el-icon>
            <div class="error-text">{{ result.message }}</div>
          </template>
        </div>
      </transition>
    </div>

    <div class="footer">
      Face BMI Prediction System &copy; 2026
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef } from 'vue'
import { Upload, Cpu, CircleClose } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { predictImage } from './api.js'

const uploadRef = ref(null)
const selectedFile = shallowRef(null)
const previewUrl = ref('')
const loading = ref(false)
const result = ref(null)

function handleFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw
  previewUrl.value = URL.createObjectURL(uploadFile.raw)
  result.value = null
}

async function handlePredict() {
  if (!selectedFile.value) return

  loading.value = true
  result.value = null

  try {
    const { data } = await predictImage(selectedFile.value)
    if (data.success) {
      result.value = { success: true, bmi: Number(data.bmi) }
      ElMessage.success(`BMI: ${Number(data.bmi).toFixed(2)}`)
    } else {
      result.value = { success: false, message: data.message || 'Prediction failed' }
      ElMessageBox.alert(data.message || 'Prediction failed', 'Prediction Failed', {
        type: 'error',
        confirmButtonText: 'OK'
      })
    }
  } catch (err) {
    const msg = err.response?.data?.message || err.message || 'Request failed'
    result.value = { success: false, message: msg }
    ElMessageBox.alert(msg, 'Error', {
      type: 'error',
      confirmButtonText: 'OK'
    })
  } finally {
    loading.value = false
  }
}

function handleReset() {
  selectedFile.value = null
  previewUrl.value = ''
  result.value = null
}

function bmiCategory(bmi) {
  if (bmi < 18.5) return 'Underweight'
  if (bmi < 25) return 'Normal'
  if (bmi < 30) return 'Overweight'
  return 'Obese'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #e0ecff 0%, #f5f8ff 50%, #e8eef8 100%);
  min-height: 100vh;
}

.app-container {
  max-width: 640px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #1a3a6b;
  letter-spacing: 0.5px;
}

.subtitle {
  margin-top: 8px;
  font-size: 15px;
  color: #6b8299;
}

.main-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(26, 58, 107, 0.08);
  flex: 1;
}

.upload-area {
  width: 100%;
}

.upload-area .el-upload-dragger {
  width: 100%;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  border: 2px dashed #c0d4ee;
  background: #f8faff;
  transition: border-color 0.3s;
}

.upload-area .el-upload-dragger:hover {
  border-color: #4080e8;
}

.upload-placeholder {
  text-align: center;
  color: #8ea4c4;
}

.upload-icon {
  font-size: 48px;
  color: #4080e8;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 15px;
  color: #5a7799;
}

.upload-text em {
  color: #4080e8;
  font-style: normal;
}

.upload-tip {
  font-size: 13px;
  color: #a0b4cc;
  margin-top: 6px;
}

.preview-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
}

.preview-image {
  max-width: 100%;
  max-height: 256px;
  border-radius: 8px;
  object-fit: contain;
}

.action-row {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: center;
}

.predict-btn {
  min-width: 160px;
  --el-button-bg-color: #4080e8;
  --el-button-border-color: #4080e8;
  --el-button-hover-bg-color: #2a66d4;
  --el-button-hover-border-color: #2a66d4;
}

.result-section {
  margin-top: 28px;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
}

.result-success {
  background: linear-gradient(135deg, #eef5ff, #dbe8fc);
  border: 1px solid #c0d4ee;
}

.result-error {
  background: #fff5f5;
  border: 1px solid #fdd;
}

.result-label {
  font-size: 14px;
  color: #6b8299;
  margin-bottom: 4px;
}

.result-value {
  font-size: 52px;
  font-weight: 800;
  color: #1a3a6b;
  line-height: 1.2;
}

.result-category {
  margin-top: 8px;
  font-size: 15px;
  color: #5a7799;
}

.error-icon {
  font-size: 40px;
  color: #f56c6c;
  margin-bottom: 8px;
}

.error-text {
  font-size: 15px;
  color: #f56c6c;
}

.footer {
  text-align: center;
  margin-top: 32px;
  font-size: 13px;
  color: #a0b4cc;
  padding-bottom: 16px;
}

@media (max-width: 480px) {
  .app-container {
    padding: 20px 12px;
  }
  .main-card {
    padding: 20px 16px;
  }
  .title {
    font-size: 22px;
  }
  .result-value {
    font-size: 40px;
  }
  .upload-area .el-upload-dragger {
    height: 220px;
  }
}
</style>
