# Shelfly - Online Bookstore

A full-featured Django-based online bookstore application demonstrating modern software engineering practices through the integration of five major design patterns.

## Features

- User authentication and registration
- Book browsing and search
- Shopping cart management
- Multiple discount system (coupon, order value, first-time buyer)
- Multiple payment methods (Cash on Delivery, Card Payment)
- Order tracking and history
- Order cancellation with inventory restoration
- Contact form for customer inquiries

## Technology Stack

- **Backend**: Django 5.2
- **Database**: MySQL
- **Python**: 3.13+
- **Frontend**: HTML/CSS (Bootstrap)

## Design Patterns Implemented

This project demonstrates five major design patterns integrated throughout the application:

### 1. Strategy Pattern
**Location**: `bookstore/strategies/`

Flexible discount calculation system with multiple strategies:
- `CouponDiscountStrategy` - Coupon-based discounts
- `OrderValueDiscountStrategy` - Tiered discounts based on order value
- `FirstTimeBuyerDiscountStrategy` - Discount for new customers

```python
# Usage example
from bookstore.services.discount_service import DiscountService

discount_result = DiscountService.calculate_all_discounts_for(
    subtotal=cart.subtotal,
    customer=customer,
    coupon=cart.applied_coupon
)
```

### 2. Factory Pattern
**Location**: `bookstore/payments/`

Payment processor factory creating payment gateways dynamically:
- `CashOnDeliveryProcessor` - Cash on delivery processing
- `CardPaymentProcessor` - Credit/debit card processing

```python
# Usage example
from bookstore.payments.payment_factory import PaymentFactory

processor = PaymentFactory.get_processor('Card')
success, message, details = processor.process_payment(order, data)
```

### 3. Repository Pattern
**Location**: `bookstore/repositories/`

Data access abstraction layer:
- `BookRepository` - Book data operations
- `OrderRepository` - Order data operations
- `CustomerRepository` - Customer data operations
- `CouponRepository` - Coupon data operations

```python
# Usage example
from bookstore.repositories.book_repository import BookRepository

book_repo = BookRepository()
books = book_repo.search("python")
book = book_repo.get_by_id(book_id)
```

### 4. Observer Pattern
**Location**: `bookstore/observers/`

Event notification system for order events:
- `EmailObserver` - Email notifications
- `InventoryObserver` - Inventory updates
- `LogObserver` - Activity logging

```python
# Usage example
from bookstore.managers.notification_manager import NotificationManager

notification_manager = NotificationManager()
notification_manager.notify_order_placed(order)
notification_manager.notify_payment_received(order, payment)
```

### 5. Singleton Pattern
**Location**: `bookstore/managers/`

Centralized configuration and state management:
- `ConfigManager` - Application configuration (thread-safe)
- `NotificationManager` - Notification coordinator (singleton)

```python
# Usage example
from bookstore.managers.config_manager import ConfigManager

config = ConfigManager()
free_shipping = config.get_free_shipping_threshold()
cancellable_statuses = config.get_cancellable_statuses()
```

## Project Structure

```
shelfly/                    # Project root
├── bookstore/              # Main application
│   ├── management/         # Design pattern implementations
│   │   ├── managers/      # Singleton managers
│   │   ├── observers/     # Observer pattern
│   │   ├── payments/      # Factory pattern
│   │   ├── repositories/  # Repository pattern
│   │   └── strategies/    # Strategy pattern
│   ├── migrations/        # Database migrations
│   ├── models.py          # Database models
│   ├── views.py           # View controllers
│   ├── urls.py            # URL routing
│   ├── admin.py          # Admin interface
│   ├── tests.py          # Unit tests
│   ├── tests/             # Pattern-specific tests
│   └── templates/         # HTML templates
│       └── bookstore/
├── shelfly/               # Django project settings
│   ├── settings.py       # Project settings
│   ├── urls.py           # Root URLs
│   ├── wsgi.py           # WSGI config
│   └── asgi.py           # ASGI config
├── manage.py              # Django management script
└── requirements.txt      # Python dependencies
```

## Database Models

- **Customer** - User profile with contact info
- **Book** - Book inventory with title, author, price, stock
- **Order** - Customer orders with status tracking
- **OrderItem** - Individual items in an order
- **Cart/CartItem** - Shopping cart functionality
- **Coupon** - Discount coupons with usage limits
- **Payment** - Payment records (method, status, transaction)
- **Delivery** - Delivery address and notes
- **ContactMessage** - Customer inquiries

## Discount System

The application supports multiple concurrent discounts:

| Discount Type | Condition | Value |
|-------------|-----------|-------|
| First-Time Buyer | New customer | 15% off |
| Order Value (5%) | Order >= Rs. 1,000 | 5% off |
| Order Value (10%) | Order >= Rs. 2,000 | 10% off |
| Order Value (15%) | Order >= Rs. 5,000 | 15% off |
| Coupon | Valid coupon code | Fixed or % |

## Shipping Fees

| Order Amount | Shipping |
|-------------|----------|
| Rs. 5,000+ | Free |
| Below Rs. 5,000 | Rs. 50 |
| 5+ books | +Rs. 10 per additional book |

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd shelfly
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate    # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure database in `.env`:
```
DB_NAME=shelfly
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Testing

Run all tests:
```bash
python manage.py test
```

Or run pattern-specific tests:
```bash
python run_all_pattern_tests.py
```

## URL Routes

| Endpoint | Description |
|----------|-------------|
| `/` | Home page |
| `/books/` | Book listing with search |
| `/book/<id>/` | Book details |
| `/register/` | User registration |
| `/login/` | User login |
| `/cart/` | Shopping cart |
| `/checkout/` | Checkout page |
| `/orders/` | Order history |
| `/orders/<id>/cancel/` | Cancel order |
| `/payment/card-form/` | Card payment form |
| `/contact/` | Contact form |
| `/about/` | About page |
| `/admin/` | Admin panel |


## Author

Created as a Software Engineering project demonstrating design patterns in Django.