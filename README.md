# Food Ordering & Delivery Management Platform

A production-ready microservices-based food delivery platform built with Django, FastAPI, React, and MySQL.

## 🏗️ Architecture

```
React (Frontend) → Nginx → FastAPI (Business Logic) → MySQL (Database)
                        → Django (Auth & Admin)    ↗
```

### Services

- **Frontend**: React 18 + Vite + TailwindCSS
- **Auth Service**: Django 4.2 + DRF + SimpleJWT
- **Core API**: FastAPI + SQLAlchemy
- **Database**: MySQL 8.0
- **Reverse Proxy**: Nginx

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ankur-kaushik11/food-delivery-system.git
   cd food-delivery-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

4. **Wait for services to be healthy** (30-60 seconds)

5. **Access the application**
   - Frontend: http://localhost
   - FastAPI Docs: http://localhost/api/docs
   - Django Admin: http://localhost/admin

## 📁 Project Structure

```
food-delivery-system/
├── django_auth_service/       # Django authentication & admin
├── fastapi_core_service/      # FastAPI business logic
├── frontend-react/            # React frontend
├── nginx/                     # Nginx reverse proxy
├── mysql/                     # Database initialization
└── docker-compose.yml         # Docker orchestration
```

## 🔑 Features

### Customer Features
- Browse restaurants by PIN code
- View restaurant menu
- Add items to cart (single restaurant restriction)
- Apply offers and discounts
- Checkout with payment modes
- Track order status
- Reorder from past orders
- File complaints

### Restaurant Owner Features
- Manage dishes (CRUD)
- View and manage orders
- Toggle ordering on/off

### Delivery Partner Features
- Toggle availability
- View assigned orders
- Update delivery status

### Customer Care Features
- View and resolve complaints

### Admin Features
- Manage restaurants, offers, and fees

## 🔒 Security Features

- JWT authentication
- Password hashing
- Role-based access control
- SQL injection prevention
- CORS configuration
- Input validation

## 🧪 API Documentation

- **FastAPI**: http://localhost/api/docs
- **Django Admin**: http://localhost/admin

## 📝 License

MIT License