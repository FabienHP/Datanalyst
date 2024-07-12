"use client";
import axios from 'axios';
import { redirect } from "next/navigation";
import { deleteTokens } from '../utils/tokens';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  config => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  response => {
    return response;
  },
  async error => {
    const originalRequest = error.config;
    if (error.response) {
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          const refreshToken = document.cookie.split(';').find(cookie => cookie.startsWith('refreshToken'))?.split('=')[1];
          if (!refreshToken) {
            deleteTokens();
            redirect('/login');
          }
          const response = await api.post('/token/refresh/', {
            refresh: refreshToken,
          });
          const newAccessToken = response.data.access;
          localStorage.setItem('accessToken', newAccessToken);
          api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          deleteTokens();
          redirect('/login');
        }
      }
    }
    return Promise.reject(error);
  }
)

export default api;
