# Deployment and Testing Guide

## Quick Start Guide

### Step 1: Environment Setup

1. Copy environment file:
```bash
cp .env.example .env
```

2. (Optional) Modify `.env` with your preferred credentials

### Step 2: Build and Start Services

```bash
# Build all services
docker-compose build

# Start all services in detached mode
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 3: Wait for Services to Initialize

Services take approximately 30-60 seconds to fully start. Monitor logs:

```bash
# Watch all logs
docker-compose logs -f

# Watch specific service
docker-compose logs -f django_auth
docker-compose logs -f fastapi_core
```

### Step 4: Seed Database

```bash
# Enter Django container
docker exec -it food_delivery_django bash

# Run seed script
python manage.py shell < seed_data.py

# Exit container
exit
```

### Step 5: Access Services

- **Frontend**: http://localhost
- **FastAPI Docs**: http://localhost/api/docs
- **Django Admin**: http://localhost/admin
- **MySQL**: localhost:3306

## Testing Authentication Flow

### 1. Test Signup

Navigate to http://localhost/signup

Create a new account:
- Name: Test User
- Email: test@example.com
- Password: test12345
- Confirm Password: test12345
- Role: Customer
- PIN Code: 110001

### 2. Test Login

Navigate to http://localhost/login

Login with:
- Email: test@example.com
- Password: test12345

You should be redirected to the restaurant listing page.

### 3. Test Customer Flow

After login:
1. Browse restaurants in PIN code 110001
2. Click on "Pizza Palace"
3. Add items to cart
4. View cart
5. Proceed to checkout
6. View order history

### 4. Test Other Roles

Login with seeded accounts:

**Restaurant Owner**:
- Email: owner1@food.com
- Password: owner123
- Access: http://localhost/restaurant/dashboard

**Delivery Partner**:
- Email: delivery1@food.com
- Password: delivery123
- Access: http://localhost/delivery/dashboard

**Customer Care**:
- Email: care@food.com
- Password: care123
- Access: http://localhost/support/complaints

**Admin**:
- Email: admin@food.com
- Password: admin123
- Access: http://localhost/admin/dashboard or http://localhost/admin

## API Testing with curl

### 1. User Signup
```bash
curl -X POST http://localhost/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test User",
    "email": "apitest@example.com",
    "password": "test12345",
    "password_confirm": "test12345",
    "role": "Customer",
    "pin_code": "110001"
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "apitest@example.com",
    "password": "test12345"
  }'
```

Save the `access` token from the response.

### 3. Get Restaurants (Authenticated)
```bash
curl -X GET "http://localhost/api/restaurants?pin_code=110001" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Get Restaurant Menu
```bash
curl -X GET "http://localhost/api/restaurants/1/menu" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Add to Cart
```bash
curl -X POST http://localhost/api/cart/add \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dish_id": 1,
    "quantity": 2
  }'
```

### 6. View Cart
```bash
curl -X GET http://localhost/api/cart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Checkout
```bash
curl -X POST http://localhost/api/checkout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_mode": "cash"
  }'
```

## Troubleshooting

### Services Not Starting

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

### MySQL Connection Issues

```bash
# Check MySQL is running
docker exec food_delivery_mysql mysqladmin ping -h localhost

# Connect to MySQL
docker exec -it food_delivery_mysql mysql -u food_user -p
# Password: food_password

# Check database
SHOW DATABASES;
USE food_delivery;
SHOW TABLES;
```

### Django Migrations

```bash
# Enter Django container
docker exec -it food_delivery_django bash

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f django_auth
docker-compose logs -f fastapi_core
docker-compose logs -f mysql
docker-compose logs -f nginx
```

### Restart Specific Service

```bash
docker-compose restart django_auth
docker-compose restart fastapi_core
docker-compose restart react_frontend
```

## Performance Verification

### Check Service Health

```bash
# Django health (via admin page)
curl http://localhost/admin/

# FastAPI health
curl http://localhost/health

# Or check via docker
docker-compose ps
```

### Database Verification

```bash
# Check tables
docker exec -it food_delivery_mysql mysql -u food_user -pfood_password -e "USE food_delivery; SHOW TABLES;"

# Check user count
docker exec -it food_delivery_mysql mysql -u food_user -pfood_password -e "USE food_delivery; SELECT COUNT(*) FROM users_user;"

# Check restaurants
docker exec -it food_delivery_mysql mysql -u food_user -pfood_password -e "USE food_delivery; SELECT * FROM restaurants;"
```

## Clean Shutdown

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Production Considerations

Before deploying to production:

1. **Change all secrets** in `.env` file
2. **Set DEBUG=False** for Django and FastAPI
3. **Configure ALLOWED_HOSTS** properly
4. **Use environment-specific database credentials**
5. **Enable HTTPS** with SSL certificates
6. **Configure CORS** for specific origins only
7. **Set up proper logging** and monitoring
8. **Enable rate limiting**
9. **Configure database backups**
10. **Use production-grade WSGI server** (Gunicorn is already configured)

## Additional Resources

- FastAPI Interactive Docs: http://localhost/api/docs
- FastAPI ReDoc: http://localhost/api/redoc
- Django Admin: http://localhost/admin
