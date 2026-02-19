import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { customerAPI } from '../../services/api';

const Cart = () => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paymentMode, setPaymentMode] = useState('cash');
  const navigate = useNavigate();

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const response = await customerAPI.getCart();
      setCart(response.data);
    } catch (error) {
      console.error('Error loading cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeItem = async (dishId) => {
    try {
      await customerAPI.removeFromCart({ dish_id: dishId });
      loadCart();
    } catch (error) {
      console.error('Error removing item:', error);
    }
  };

  const handleCheckout = async () => {
    try {
      await customerAPI.checkout({ payment_mode: paymentMode });
      navigate('/orders');
    } catch (error) {
      alert(error.response?.data?.detail || 'Checkout failed');
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="text-indigo-600 hover:text-indigo-800"
              >
                ← Continue Shopping
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto py-8 px-4">
        <h2 className="text-2xl font-bold mb-6">Shopping Cart</h2>

        {!cart || cart.items.length === 0 ? (
          <div className="text-center py-8 text-gray-600">
            Your cart is empty
          </div>
        ) : (
          <div>
            {cart.restaurant_name && (
              <div className="mb-4 p-4 bg-blue-50 rounded">
                <p className="font-semibold">Restaurant: {cart.restaurant_name}</p>
              </div>
            )}

            <div className="bg-white rounded-lg shadow">
              {cart.items.map((item) => (
                <div
                  key={item.dish_id}
                  className="flex justify-between items-center p-4 border-b"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold">{item.dish_name}</h3>
                    <p className="text-gray-600">
                      ₹{parseFloat(item.price).toFixed(2)} x {item.quantity}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <p className="font-bold">
                      ₹{parseFloat(item.subtotal).toFixed(2)}
                    </p>
                    <button
                      onClick={() => removeItem(item.dish_id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}

              <div className="p-4">
                <div className="flex justify-between mb-4">
                  <span className="font-bold">Subtotal:</span>
                  <span className="font-bold">
                    ₹{parseFloat(cart.subtotal).toFixed(2)}
                  </span>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">
                    Payment Mode
                  </label>
                  <select
                    value={paymentMode}
                    onChange={(e) => setPaymentMode(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="cash">Cash</option>
                    <option value="card">Card</option>
                    <option value="upi">UPI</option>
                  </select>
                </div>

                <button
                  onClick={handleCheckout}
                  className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 font-semibold"
                >
                  Proceed to Checkout
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Cart;
