// types.ts - TypeScript interfaces matching your API

export interface CircleInfo {
  id: string;
  name: string;
  created_at: string;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
  name?: string;
  address1?: string;
  address2?: string;
  battery?: number;
  timestamp: string;
  speed?: number;
  is_driving?: boolean;
}

export interface MemberSummary {
  id: string;
  first_name: string;
  last_name?: string;
  full_name: string;
  status: string;
  location?: LocationData;
  avatar?: string;
  phone?: string;
  email?: string;
}

export interface ApiError {
  error: string;
  detail: string;
  status_code: number;
}