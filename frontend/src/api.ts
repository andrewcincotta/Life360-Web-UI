// api.ts - API service for Life360

import axios, { AxiosInstance } from 'axios';
import { CircleInfo, MemberSummary } from './types';

const API_BASE_URL = process.env.REACT_APP_FAST_API_URL || 'http://localhost:8000';

class Life360Api {
  private api: AxiosInstance;

  constructor(token?: string) {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token is invalid or expired
          localStorage.removeItem('life360_token');
          window.location.href = '/';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.api.defaults.headers.Authorization = `Bearer ${token}`;
  }

  async validateToken(token: string): Promise<boolean> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/validate`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data.valid;
    } catch {
      return false;
    }
  }

  async getCircles(): Promise<CircleInfo[]> {
    const response = await this.api.get<CircleInfo[]>('/circles');
    return response.data;
  }

  async getCircleMembers(circleId: string): Promise<MemberSummary[]> {
    const response = await this.api.get<MemberSummary[]>(
      `/circles/${circleId}/members`
    );
    return response.data;
  }

  async getAllMembers(): Promise<Record<string, MemberSummary[]>> {
    const response = await this.api.get<Record<string, MemberSummary[]>>(
      '/members/all'
    );
    return response.data;
  }
}

export default Life360Api;