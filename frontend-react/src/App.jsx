import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './utils/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import RestaurantList from './pages/RestaurantList';
import RestaurantMenu from './pages/RestaurantMenu';
import Cart from './pages/Cart';
import OrderHistory from './pages/OrderHistory';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Customer routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute allowedRoles={['Customer']}>
                <RestaurantList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/restaurant/:id"
            element={
              <ProtectedRoute allowedRoles={['Customer']}>
                <RestaurantMenu />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cart"
            element={
              <ProtectedRoute allowedRoles={['Customer']}>
                <Cart />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute allowedRoles={['Customer']}>
                <OrderHistory />
              </ProtectedRoute>
            }
          />

          {/* Restaurant Owner routes */}
          <Route
            path="/restaurant/dashboard"
            element={
              <ProtectedRoute allowedRoles={['Restaurant Owner']}>
                <div className="p-8">
                  <h1 className="text-2xl font-bold">Restaurant Dashboard</h1>
                  <p>Manage your dishes and orders here</p>
                </div>
              </ProtectedRoute>
            }
          />

          {/* Delivery Partner routes */}
          <Route
            path="/delivery/dashboard"
            element={
              <ProtectedRoute allowedRoles={['Delivery Partner']}>
                <div className="p-8">
                  <h1 className="text-2xl font-bold">Delivery Dashboard</h1>
                  <p>View assigned orders here</p>
                </div>
              </ProtectedRoute>
            }
          />

          {/* Customer Care routes */}
          <Route
            path="/support/complaints"
            element={
              <ProtectedRoute allowedRoles={['Customer Care']}>
                <div className="p-8">
                  <h1 className="text-2xl font-bold">Support Dashboard</h1>
                  <p>Manage complaints here</p>
                </div>
              </ProtectedRoute>
            }
          />

          {/* Admin routes */}
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute allowedRoles={['Admin']}>
                <div className="p-8">
                  <h1 className="text-2xl font-bold">Admin Dashboard</h1>
                  <p>Manage restaurants, offers, and fees here</p>
                </div>
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
