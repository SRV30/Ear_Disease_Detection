let isRefreshing = false;
let refreshSubscribers = [];

const notifySubscribers = (token) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

const addSubscriber = (cb) => {
  refreshSubscribers.push(cb);
};

export const isTokenExpired = (token) => {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (!payload?.exp) return true;
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
};

export const refreshAccessToken = async (api) => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) throw new Error('Missing refresh token');

  const res = await api.post('/refresh', null, {
    headers: { Authorization: `Bearer ${refreshToken}` },
    _skipAuthRefresh: true,
  });

  const newAccessToken = res?.data?.access_token;
  if (!newAccessToken) throw new Error('Invalid refresh response');

  localStorage.setItem('access_token', newAccessToken);
  return newAccessToken;
};

export const handle401WithRefresh = async (error, api) => {
  const originalRequest = error.config;
  if (!originalRequest || originalRequest._retry || originalRequest._skipAuthRefresh) {
    throw error;
  }

  originalRequest._retry = true;

  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      addSubscriber((token) => {
        if (!token) return reject(error);
        originalRequest.headers.Authorization = `Bearer ${token}`;
        resolve(api(originalRequest));
      });
    });
  }

  isRefreshing = true;
  try {
    const token = await refreshAccessToken(api);
    notifySubscribers(token);
    originalRequest.headers.Authorization = `Bearer ${token}`;
    return api(originalRequest);
  } catch (refreshError) {
    notifySubscribers(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    throw refreshError;
  } finally {
    isRefreshing = false;
  }
};

export const logoutSession = async (api) => {
  try {
    await api.post('/logout', null, { _skipAuthRefresh: true });
  } catch {
    // ignore network/logout failures and clear local session anyway
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};
