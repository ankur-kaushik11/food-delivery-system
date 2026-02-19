# System Architecture Documentation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│                    (React 18 + Vite + TailwindCSS)              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Nginx Reverse Proxy                        │
│  Routes:                                                         │
│  - /api/auth/*  → Django (Port 8000)                            │
│  - /api/admin/* → Django (Port 8000)                            │
│  - /api/*       → FastAPI (Port 8001)                           │
│  - /*           → React Frontend (Port 80)                      │
└─────────────────┬──────────────────────┬────────────────────────┘
                  │                      │
        ┌─────────┴────────┐   ┌────────┴──────────┐
        ▼                  ▼   ▼                   ▼
┌────────────────┐  ┌──────────────────────┐  ┌───────────────┐
│ Django Auth    │  │  FastAPI Core        │  │ React         │
│ Service        │  │  Service             │  │ Frontend      │
│                │  │                      │  │               │
│ - JWT Auth     │  │ - Business Logic     │  │ - UI Pages    │
│ - SimpleJWT    │  │ - Order Management   │  │ - State Mgmt  │
│ - User Mgmt    │  │ - Cart Service       │  │ - API Client  │
│ - Admin CRUD   │  │ - Delivery Service   │  │ - Auth Flow   │
│                │  │ - Offer Service      │  │               │
│ Port: 8000     │  │ Port: 8001           │  │ Port: 80      │
└────────┬───────┘  └──────────┬───────────┘  └───────────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
         ┌──────────────────────┐
         │   MySQL Database     │
         │   Port: 3306         │
         │                      │
         │  Tables:             │
         │  - users_user        │
         │  - restaurants       │
         │  - dishes            │
         │  - orders            │
         │  - order_items       │
         │  - delivery_partners │
         │  - complaints        │
         │  - offers            │
         │  - fees              │
         │  - notifications     │
         └──────────────────────┘
```

## Service Responsibilities

### 1. Django Auth Service (Port 8000)

**Responsibility**: Authentication, Authorization, and Administrative Management

**Components**:
- `users` app: User model, signup, login, JWT token management
- `admin_panel` app: CRUD for restaurants, offers, fees

**Technologies**:
- Django 4.2
- Django REST Framework
- SimpleJWT for JWT tokens
- mysqlclient for database

**Endpoints**:
```
POST /api/auth/signup          - Register new user
POST /api/auth/login           - Login and get JWT tokens
POST /api/auth/token/refresh   - Refresh access token
GET  /api/auth/users/me        - Get current user profile
GET  /api/admin/restaurants    - List restaurants (Admin)
POST /api/admin/restaurants    - Create restaurant (Admin)
GET  /api/admin/offers         - List offers (Admin)
POST /api/admin/offers         - Create offer (Admin)
GET  /api/admin/fees           - List fees (Admin)
POST /api/admin/fees           - Create fee (Admin)
GET  /api/admin/users          - List all users (Admin)
```

### 2. FastAPI Core Service (Port 8001)

**Responsibility**: All Business Logic and Order Management

**Components**:
- `models`: SQLAlchemy ORM models
- `schemas`: Pydantic validation schemas
- `routers`: API endpoint definitions
- `services`: Business logic (cart, order, offer, delivery)
- `dependencies`: JWT validation and role-based access
- `utils`: Notification simulation

**Technologies**:
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose for JWT validation

**Key Business Logic**:
1. **Cart Management**: Multi-restaurant restriction validation
2. **Offer Application**: Best offer selection, eligibility checking
3. **Order Creation**: Fee calculation, discount application
4. **Delivery Assignment**: Pin code matching, availability checking
5. **Order Lifecycle**: Status transitions, validation rules
6. **Notification System**: Event-driven notifications

**Endpoints**:
```
# Customer
GET  /api/restaurants                     - Browse restaurants
GET  /api/restaurants/{id}/menu           - View menu
POST /api/cart/add                        - Add to cart
POST /api/checkout                        - Create order
GET  /api/orders/history                  - Order history
POST /api/orders/{id}/reorder             - Reorder
POST /api/complaints                      - File complaint

# Restaurant Owner
POST /api/restaurant/dishes               - Create dish
PUT  /api/restaurant/dishes/{id}          - Update dish
GET  /api/restaurant/orders               - View orders
PUT  /api/restaurant/orders/{id}/status   - Update order status
PUT  /api/restaurant/toggle-ordering      - Enable/disable ordering

# Delivery Partner
PUT  /api/delivery/toggle-availability    - Set availability
GET  /api/delivery/assigned-orders        - View assigned orders
PUT  /api/delivery/orders/{id}/status     - Update delivery status

# Customer Care
GET  /api/support/complaints              - View complaints
PUT  /api/support/complaints/{id}/resolve - Resolve complaint
```

### 3. React Frontend (Port 80 in container, 3000 in dev)

**Responsibility**: User Interface and Client-Side Logic

**Components**:
- `pages`: Route components for different views
- `components`: Reusable UI components
- `services`: API client with axios
- `context`: Auth state management
- `utils`: Protected routes, helpers

**Technologies**:
- React 18
- Vite (build tool)
- TailwindCSS (styling)
- React Router (routing)
- Axios (HTTP client)

**Pages**:
```
/login                    - Login page
/signup                   - Registration page
/                         - Restaurant listing (Customer)
/restaurant/:id           - Restaurant menu (Customer)
/cart                     - Shopping cart (Customer)
/orders                   - Order history (Customer)
/restaurant/dashboard     - Dish management (Restaurant Owner)
/delivery/dashboard       - Delivery management (Delivery Partner)
/support/complaints       - Complaint management (Customer Care)
/admin/dashboard          - Admin panel (Admin)
```

### 4. MySQL Database (Port 3306)

**Tables and Relationships**:

```
users_user (Django-managed)
├── restaurants (owner_id FK)
│   ├── dishes (restaurant_id FK)
│   ├── offers (restaurant_id FK, nullable)
│   └── fees (restaurant_id FK, nullable)
├── orders (customer_id, delivery_partner_id FK)
│   ├── order_items (order_id FK)
│   └── complaints (order_id FK)
└── delivery_partners (user_id FK)
```

### 5. Nginx Reverse Proxy (Port 80)

**Responsibility**: Request routing and load balancing

**Routing Rules**:
- `/api/auth/*` → Django Auth Service
- `/api/admin/*` → Django Auth Service
- `/api/*` → FastAPI Core Service
- `/*` → React Frontend

## Authentication Flow

```
1. User submits credentials to Django /api/auth/login
   ↓
2. Django validates credentials
   ↓
3. Django generates JWT tokens (access + refresh) using SimpleJWT
   ↓
4. Tokens include: user_id, email, role, exp, iat
   ↓
5. React stores tokens in localStorage
   ↓
6. React sends Authorization: Bearer <token> to FastAPI
   ↓
7. FastAPI validates JWT using shared SECRET_KEY
   ↓
8. FastAPI extracts user_id and role from token
   ↓
9. FastAPI enforces role-based access control
   ↓
10. On token expiry, React refreshes via Django /api/auth/token/refresh
```

## Business Logic Workflows

### Order Creation Workflow

```
1. Customer browses restaurants by PIN code
2. Customer adds dishes to cart (validates single restaurant)
3. Customer proceeds to checkout
4. System validates:
   - Cart is not empty
   - Restaurant is active
   - Ordering is enabled
   - All dishes are available
5. System calculates fees (restaurant-specific or platform-level)
6. System applies best applicable offer
7. System calculates total amount
8. System creates order with status "placed"
9. System sends notifications to customer and restaurant
10. Cart is cleared
```

### Delivery Assignment Workflow

```
1. Restaurant owner marks order as "preparing"
2. System sends notification to customer
3. Delivery partner moves order to "out_for_delivery"
4. System assigns delivery partner (if not already assigned):
   - Finds available delivery partner
   - Matches by PIN code
   - Marks partner as unavailable
5. System sends notification to customer and delivery partner
6. Delivery partner marks order as "delivered"
7. System marks delivery partner as available again
8. System sends delivery confirmation notification
```

### Offer Application Workflow

```
1. Get all active offers
2. Filter by minimum order value
3. Filter by first-time user condition
4. Separate restaurant-specific and platform offers
5. Restaurant-specific offers take precedence
6. Select offer with highest discount percentage
7. Calculate discount amount
8. Apply to order total
```

## Data Flow Examples

### Example: Customer Places Order

```
1. POST /api/cart/add → FastAPI
   - Validates dish exists and is available
   - Validates restaurant is accepting orders
   - Checks multi-restaurant restriction
   - Stores in in-memory cart

2. POST /api/checkout → FastAPI
   - Validates cart
   - Queries fees from MySQL
   - Queries offers from MySQL
   - Calculates totals
   - Inserts order into MySQL
   - Inserts order_items into MySQL
   - Clears cart
   - Sends notifications

3. GET /api/orders/history → FastAPI
   - Queries orders from MySQL
   - Returns order list to React
```

## Security Measures

1. **JWT Authentication**: All protected endpoints require valid JWT
2. **Password Hashing**: bcrypt via Django's authentication system
3. **Role-Based Access Control**: Dependencies enforce user roles
4. **SQL Injection Prevention**: ORM (SQLAlchemy & Django ORM)
5. **Input Validation**: Pydantic schemas validate all inputs
6. **CORS Configuration**: Controlled in both Django and FastAPI
7. **Environment Variables**: Secrets stored in .env file
8. **Token Expiration**: Access tokens expire in 60 minutes

## Scalability Considerations

1. **Database Connection Pooling**: SQLAlchemy pool configuration
2. **Stateless Services**: JWT eliminates session storage
3. **Microservices**: Independent scaling of auth and core services
4. **Nginx Load Balancing**: Can distribute to multiple instances
5. **Docker Containers**: Easy horizontal scaling
6. **In-Memory Cart**: Can be moved to Redis for persistence

## Monitoring and Logging

- Console logging for notifications
- Database storage for notification history
- Docker logs for service debugging
- Health check endpoints for monitoring
- Structured logging format

## Future Enhancements

1. Redis for cart persistence
2. WebSocket for real-time order tracking
3. Payment gateway integration
4. Email/SMS notification service
5. Image upload to S3/cloud storage
6. Search and filtering improvements
7. Rating and review system
8. Analytics dashboard
9. CI/CD pipeline
10. Kubernetes deployment
