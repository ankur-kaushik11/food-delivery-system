import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { customerAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const RestaurantList = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [pinCode, setPinCode] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.pin_code) {
      setPinCode(user.pin_code);
      loadRestaurants(user.pin_code);
    }
  }, [user]);

  const loadRestaurants = async (pc) => {
    setLoading(true);
    try {
      const response = await customerAPI.getRestaurants(pc || null);
      setRestaurants(response.data);
    } catch (error) {
      console.error('Error loading restaurants:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadRestaurants(pinCode);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">Food Delivery</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/cart')}
                className="text-gray-700 hover:text-gray-900"
              >
                Cart
              </button>
              <button
                onClick={() => navigate('/orders')}
                className="text-gray-700 hover:text-gray-900"
              >
                Orders
              </button>
              <span className="text-gray-700">{user?.name}</span>
              <button
                onClick={logout}
                className="text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Enter PIN code"
              value={pinCode}
              onChange={(e) => setPinCode(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Search
            </button>
          </div>
        </form>

        {loading ? (
          <div className="text-center">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {restaurants.map((restaurant) => (
              <div
                key={restaurant.id}
                onClick={() => navigate(`/restaurant/${restaurant.id}`)}
                className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition"
              >
                <h3 className="text-lg font-semibold mb-2">{restaurant.name}</h3>
                <p className="text-gray-600">PIN: {restaurant.pin_code}</p>
                <p className="text-gray-600">
                  Status: <span className="text-green-600">{restaurant.status}</span>
                </p>
              </div>
            ))}
          </div>
        )}

        {!loading && restaurants.length === 0 && (
          <div className="text-center text-gray-600">
            No restaurants found in this area
          </div>
        )}
      </div>
    </div>
  );
};

export default RestaurantList;
