import axios from 'axios'

const API_BASE = 'http://127.0.0.1:5000'

export function predictImage(file) {
  const formData = new FormData()
  formData.append('image', file)
  return axios.post(`${API_BASE}/predict`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000
  })
}

export function checkServer() {
  return axios.get(`${API_BASE}/`)
}
