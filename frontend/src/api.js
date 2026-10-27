import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
});

export function formatApiError(error, fallback = 'Something went wrong. Please try again.') {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => typeof item === 'string' ? item : item?.msg)
      .filter((message) => typeof message === 'string' && message.trim());
    if (messages.length) return messages.join(' ');
  }
  if (detail && typeof detail === 'object') {
    const messages = [detail.message, detail.error, ...(Array.isArray(detail.errors) ? detail.errors : [])]
      .filter((message) => typeof message === 'string' && message.trim());
    if (messages.length) return messages.join(' ');
  }
  return fallback;
}

export default api;
