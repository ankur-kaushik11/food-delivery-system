import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost/api';
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_BASE_URL || 'http://localhost/api/auth';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${AUTH_BASE_URL}/token/refresh`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: (data) => axios.post(`${AUTH_BASE_URL}/signup`, data),
  login: (data) => axios.post(`${AUTH_BASE_URL}/login`, data),
  getCurrentUser: () => api.get(`${AUTH_BASE_URL}/users/me`),
};

export const customerAPI = {
  getRestaurants: (pinCode) => api.get('/restaurants', { params: { pin_code: pinCode } }),
  getMenu: (restaurantId) => api.get(`/restaurants/${restaurantId}/menu`),
  addToCart: (data) => api.post('/cart/add', data),
  removeFromCart: (data) => api.post('/cart/remove', data),
  getCart: () => api.get('/cart'),
  checkout: (data) => api.post('/checkout', data),
  getOrders: () => api.get('/orders/history'),
  getOrder: (orderId) => api.get(`/orders/${orderId}`),
  cancelOrder: (orderId) => api.post(`/orders/${orderId}/cancel`),
  reorder: (orderId) => api.post(`/orders/${orderId}/reorder`),
  createComplaint: (data) => api.post('/complaints', data),
  getComplaints: () => api.get('/complaints'),
};

export const restaurantAPI = {
  createDish: (data) => api.post('/restaurant/dishes', data),
  updateDish: (dishId, data) => api.put(`/restaurant/dishes/${dishId}`, data),
  deleteDish: (dishId) => api.delete(`/restaurant/dishes/${dishId}`),
  getDishes: () => api.get('/restaurant/dishes'),
  getOrders: () => api.get('/restaurant/orders'),
  updateOrderStatus: (orderId, status) => api.put(`/restaurant/orders/${orderId}/status`, { status }),
  toggleOrdering: (enabled) => api.put('/restaurant/toggle-ordering', { is_ordering_enabled: enabled }),
};

export const deliveryAPI = {
  toggleAvailability: (available) => api.put('/delivery/toggle-availability', { available }),
  getAssignedOrders: () => api.get('/delivery/assigned-orders'),
  updateOrderStatus: (orderId, status) => api.put(`/delivery/orders/${orderId}/status`, { status }),
};

export const supportAPI = {
  getComplaints: (status) => api.get('/support/complaints', { params: { status_filter: status } }),
  resolveComplaint: (complaintId, notes) => api.put(`/support/complaints/${complaintId}/resolve`, { resolution_notes: notes }),
};

export const adminAPI = {
  getRestaurants: () => axios.get(`${AUTH_BASE_URL.replace('/auth', '/admin')}/restaurants`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
  createRestaurant: (data) => axios.post(`${AUTH_BASE_URL.replace('/auth', '/admin')}/restaurants`, data, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
  getOffers: () => axios.get(`${AUTH_BASE_URL.replace('/auth', '/admin')}/offers`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
  createOffer: (data) => axios.post(`${AUTH_BASE_URL.replace('/auth', '/admin')}/offers`, data, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
  getFees: () => axios.get(`${AUTH_BASE_URL.replace('/auth', '/admin')}/fees`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
  createFee: (data) => axios.post(`${AUTH_BASE_URL.replace('/auth', '/admin')}/fees`, data, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
  getUsers: () => axios.get(`${AUTH_BASE_URL.replace('/auth', '/admin')}/users`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
  }),
};

export default api;
