import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
});

export function formatApiError(error, fallback = 'Something went wrong. Please try again.') {
  const data = error?.response?.data;
  const detail = data?.detail;
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
  const responseMessage = [data?.message, data?.error]
    .find((message) => typeof message === 'string' && message.trim());
  if (responseMessage) return responseMessage;
  if (error?.response?.status) return `${fallback} (API returned HTTP ${error.response.status}.)`;
  if (error?.code === 'ERR_NETWORK' || error?.request) {
    return 'Could not reach the FinSight API. Check the Vercel /api rewrite and Render service logs.';
  }
  return fallback;
}

export default api;
