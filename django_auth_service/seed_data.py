"""
Seed data script for Food Delivery System.
Run this script to populate the database with sample data.

Usage:
    docker exec -it food_delivery_django python manage.py shell
    >>> exec(open('seed_data.py').read())
"""

from users.models import User
from admin_panel.models import Restaurant, Offer, Fee
from django.db import connection

print("Starting database seeding...")

# Create Admin user
admin, created = User.objects.get_or_create(
    email='admin@food.com',
    defaults={
        'name': 'Admin User',
        'role': 'Admin',
        'pin_code': '110001',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("✓ Admin user created: admin@food.com / admin123")
else:
    print("✓ Admin user already exists")

# Create Restaurant Owners
owner1, created = User.objects.get_or_create(
    email='owner1@food.com',
    defaults={
        'name': 'Pizza Palace Owner',
        'role': 'Restaurant Owner',
        'pin_code': '110001'
    }
)
if created:
    owner1.set_password('owner123')
    owner1.save()
    print("✓ Restaurant Owner 1 created: owner1@food.com / owner123")

owner2, created = User.objects.get_or_create(
    email='owner2@food.com',
    defaults={
        'name': 'Burger Hub Owner',
        'role': 'Restaurant Owner',
        'pin_code': '110002'
    }
)
if created:
    owner2.set_password('owner123')
    owner2.save()
    print("✓ Restaurant Owner 2 created: owner2@food.com / owner123")

# Create Customers
customer1, created = User.objects.get_or_create(
    email='customer1@food.com',
    defaults={
        'name': 'John Doe',
        'role': 'Customer',
        'pin_code': '110001'
    }
)
if created:
    customer1.set_password('customer123')
    customer1.save()
    print("✓ Customer 1 created: customer1@food.com / customer123")

customer2, created = User.objects.get_or_create(
    email='customer2@food.com',
    defaults={
        'name': 'Jane Smith',
        'role': 'Customer',
        'pin_code': '110001'
    }
)
if created:
    customer2.set_password('customer123')
    customer2.save()
    print("✓ Customer 2 created: customer2@food.com / customer123")

customer3, created = User.objects.get_or_create(
    email='customer3@food.com',
    defaults={
        'name': 'Bob Wilson',
        'role': 'Customer',
        'pin_code': '110002'
    }
)
if created:
    customer3.set_password('customer123')
    customer3.save()
    print("✓ Customer 3 created: customer3@food.com / customer123")

# Create Delivery Partners
delivery1, created = User.objects.get_or_create(
    email='delivery1@food.com',
    defaults={
        'name': 'Mike Rider',
        'role': 'Delivery Partner',
        'pin_code': '110001'
    }
)
if created:
    delivery1.set_password('delivery123')
    delivery1.save()
    print("✓ Delivery Partner 1 created: delivery1@food.com / delivery123")

delivery2, created = User.objects.get_or_create(
    email='delivery2@food.com',
    defaults={
        'name': 'Sarah Fast',
        'role': 'Delivery Partner',
        'pin_code': '110002'
    }
)
if created:
    delivery2.set_password('delivery123')
    delivery2.save()
    print("✓ Delivery Partner 2 created: delivery2@food.com / delivery123")

# Create Customer Care
care, created = User.objects.get_or_create(
    email='care@food.com',
    defaults={
        'name': 'Support Team',
        'role': 'Customer Care',
        'pin_code': '110001'
    }
)
if created:
    care.set_password('care123')
    care.save()
    print("✓ Customer Care created: care@food.com / care123")

# Create Restaurants (using raw SQL to avoid Django's managed=False restriction)
with connection.cursor() as cursor:
    # Check if restaurants exist
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO restaurants (name, owner_id, pin_code, status, is_ordering_enabled, created_at)
            VALUES
            ('Pizza Palace', %s, '110001', 'active', 1, NOW()),
            ('Burger Hub', %s, '110002', 'active', 1, NOW()),
            ('Sushi World', %s, '110001', 'active', 1, NOW())
        """, [owner1.id, owner2.id, owner1.id])
        print("✓ 3 Restaurants created")
    else:
        print("✓ Restaurants already exist")

# Insert sample dishes
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM dishes")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO dishes (restaurant_id, name, price, available, created_at)
            VALUES
            (1, 'Margherita Pizza', 299.00, 1, NOW()),
            (1, 'Pepperoni Pizza', 399.00, 1, NOW()),
            (1, 'Garlic Bread', 99.00, 1, NOW()),
            (2, 'Classic Burger', 199.00, 1, NOW()),
            (2, 'Cheese Burger', 249.00, 1, NOW()),
            (2, 'French Fries', 89.00, 1, NOW()),
            (3, 'California Roll', 349.00, 1, NOW()),
            (3, 'Salmon Nigiri', 299.00, 1, NOW())
        """)
        print("✓ 8 Dishes created")
    else:
        print("✓ Dishes already exist")

# Create Platform-level offers
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM offers WHERE restaurant_id IS NULL")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO offers (restaurant_id, discount_percentage, min_order_value, first_time_user_only, active, created_at)
            VALUES
            (NULL, 20.00, 500.00, 1, 1, NOW()),
            (NULL, 10.00, 300.00, 0, 1, NOW())
        """)
        print("✓ 2 Platform-level offers created")
    else:
        print("✓ Platform offers already exist")

# Create Restaurant-specific offer
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM offers WHERE restaurant_id IS NOT NULL")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO offers (restaurant_id, discount_percentage, min_order_value, first_time_user_only, active, created_at)
            VALUES
            (1, 15.00, 400.00, 0, 1, NOW())
        """)
        print("✓ Restaurant-specific offer created")
    else:
        print("✓ Restaurant offers already exist")

# Create Platform-level fees
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM fees WHERE restaurant_id IS NULL")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO fees (restaurant_id, delivery_fee, platform_fee, created_at)
            VALUES
            (NULL, 30.00, 5.00, NOW())
        """)
        print("✓ Platform-level fees created")
    else:
        print("✓ Platform fees already exist")

# Create Restaurant-specific fees
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM fees WHERE restaurant_id IS NOT NULL")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO fees (restaurant_id, delivery_fee, platform_fee, created_at)
            VALUES
            (1, 25.00, 5.00, NOW())
        """)
        print("✓ Restaurant-specific fees created")
    else:
        print("✓ Restaurant fees already exist")

# Create Delivery Partner records
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM delivery_partners")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO delivery_partners (user_id, available, pin_code, created_at)
            VALUES
            (%s, 1, '110001', NOW()),
            (%s, 1, '110002', NOW())
        """, [delivery1.id, delivery2.id])
        print("✓ 2 Delivery Partner records created")
    else:
        print("✓ Delivery partners already exist")

print("\n" + "="*50)
print("Database seeding completed successfully!")
print("="*50)
print("\nTest Accounts:")
print("-" * 50)
print("Admin:            admin@food.com / admin123")
print("Restaurant Owner: owner1@food.com / owner123")
print("Customer:         customer1@food.com / customer123")
print("Delivery Partner: delivery1@food.com / delivery123")
print("Customer Care:    care@food.com / care123")
print("-" * 50)
