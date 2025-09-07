import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = async (username: string, password: string) => {
  try {
    const response = await api.post('/api/login', { username, password });
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export const getSystemStatus = async () => {
  try {
    const response = await api.get('/status');
    return response.data;
  } catch (error) {
    console.error('System status check failed:', error);
    throw error;
  }
};

export const getApiKeys = async () => {
  try {
    const response = await api.get('/api/keys');
    return response.data;
  } catch (error) {
    console.error('Failed to load API keys:', error);
    // Return empty keys if endpoint doesn't exist yet
    return {
      binanceApiKey: '',
      binanceApiSecret: '',
      bybitApiKey: '',
      bybitApiSecret: '',
      okxApiKey: '',
      okxApiSecret: '',
      okxPassphrase: '',
    };
  }
};

export const saveApiKeys = async (keys: any) => {
  try {
    const response = await api.post('/api/keys', keys);
    return response.data;
  } catch (error) {
    console.error('Failed to save API keys:', error);
    throw error;
  }
};

export const testApiConnection = async (exchange: string, keys: any) => {
  try {
    const response = await api.post(`/api/test-connection/${exchange}`, keys);
    return response.data;
  } catch (error) {
    console.error(`Failed to test ${exchange} connection:`, error);
    throw error;
  }
};

export default api;
