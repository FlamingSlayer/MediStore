# 💊 MediStore - Online Pharmacy Platform

> A full-stack e-pharmacy solution that allows users to browse medicines, upload prescriptions, manage orders, and track deliveries. The system provides separate dashboards for customers and administrators and manages authentication, ordering, and prescription review efficiently.

![Build](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/FlamingSlayer/MediStore?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/FlamingSlayer/MediStore?style=flat-square)
![GitHub license](https://img.shields.io/github/license/FlamingSlayer/MediStore?style=flat-square)

---

## ✨ Features

### 👤 For Customers
- Secure user registration and login with token-based authentication
- Browse and filter medicines by category, type (Rx/OTC), and price range
- View detailed product information with reviews and ratings
- Search with autocomplete suggestions
- Add to cart, adjust quantities, and manage shopping cart
- Apply coupon codes for discounts
- Upload prescriptions and track review status
- Manage saved delivery addresses
- Place orders using COD or online payment (Razorpay)
- Track order lifecycle through dashboard
- Request order cancellation and returns
- View order history and order details

### 👑 For Administrators
- Comprehensive system overview dashboard with key metrics
- Full product management (CRUD operations)
- Manage all orders and process cancellations/returns
- User management: list all users, grant/revoke staff access
- Prescription review and approval workflow with notes
- System configuration and settings
- View analytics and performance metrics

### 🛠️ Additional Capabilities
- Email notifications (welcome, order confirmation, status changes, prescription review)
- Password reset via secure email link
- Progressive Web App (PWA) – installable on mobile devices
- Admin dashboard charts (monthly orders/revenue) using Chart.js
- Product reviews (purchaser-gated)

---

## 🏗️ System Architecture

```
Frontend (HTML/CSS/JS)
        │
        ▼
REST API (Token Auth)
        │
        ▼
Django Backend (DRF)
        │
        ▼
MySQL Database
```

---

## 🛠️ Tech Stack

| Layer              | Technology                    | Purpose                        |
|--------------------|-------------------------------|--------------------------------|
| **Frontend**       | HTML5, CSS3, Vanilla JavaScript | User interface and interactions |
| **Backend**        | Django, Django REST Framework | API development                |
| **Database**       | MySQL                         | Data persistence and storage   |
| **Authentication** | DRF Token Authentication      | Secure API access              |
| **Payments**       | Razorpay                      | Online payment processing      |
| **Styling**        | Custom CSS, Bootstrap Icons   | Modern responsive UI           |
| **PWA**            | Service Worker + Manifest     | Offline support, installability |

---

## 📁 Project Structure

```
MediStore/
├── medicare_backend/           # Django backend application
│   ├── api/                    # REST API endpoints
│   │   ├── models.py           # Data models (Product, Order, etc.)
│   │   ├── serializers.py      # DRF serializers
│   │   ├── api_views.py        # API viewsets
│   │   ├── views.py            # Template views
│   │   ├── authentication.py   # Auth utilities
│   │   └── migrations/         # Database migrations
│   ├── accounts/               # User authentication app
│   ├── config/                 # Django settings
│   ├── manage.py               # Django CLI
│   ├── requirements.txt        # Python dependencies
│   ├── start-dev.ps1           # PowerShell launcher
│   └── .env                    # Environment variables (not committed)
├── templates/                  # HTML templates
│   ├── index.html              # Landing page
│   ├── products.html           # Product listings
│   ├── product-detail.html     # Single product view
│   ├── cart.html               # Shopping cart
│   ├── checkout.html           # Checkout flow
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Customer dashboard
│   ├── admin.html              # Admin dashboard
│   ├── upload-prescription.html # Prescription upload
│   ├── order-detail.html       # Order details & tracking
│   └── order-success.html      # Order confirmation
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   │   └── styles.css          # Main stylesheet
│   ├── js/                     # JavaScript files
│   │   ├── app.js              # Core application logic
│   │   ├── config.js           # API configuration
│   │   └── init.js             # Global initialization
│   ├── manifest.json           # PWA manifest
│   ├── service-worker.js       # Offline support
│   └── icons/                  # App icons (192x192, 512x512)
├── .gitignore                  # Git exclusion rules
├── LICENSE                     # MIT License
├── RUN.md                      # Detailed setup & run guide
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- MySQL 5.7+ (or use environment configuration)
- Git

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/FlamingSlayer/MediStore.git
cd MediStore/medicare_backend
```

### 2️⃣ Set Up Backend Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment
```bash
# Create .env file in medicare_backend/
# Set SECRET_KEY, DEBUG, DATABASE_URL, and RAZORPAY credentials
```

### 5️⃣ Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6️⃣ Seed Sample Data (Optional)
```bash
python manage.py seed_sample_data --if-empty
```

### 7️⃣ Run Development Server
```bash
python manage.py runserver
```

- Access: [http://localhost:8000](http://localhost:8000)
- Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 📚 API Documentation

### Authentication Endpoints
| Method | Endpoint           | Description                        |
|--------|--------------------|------------------------------------|
| POST   | /api/auth/login/   | User login, returns auth token     |
| POST   | /api/auth/register/| Register new user                  |

### Medicine & Product Endpoints
| Method | Endpoint                           | Description                  | Access         |
|--------|------------------------------------|-----------------------------|-----------------|
| GET    | /api/products/                    | List all medicines          | All users       |
| GET    | /api/products/{id}/               | Get product details         | All users       |
| GET    | /api/products/featured/           | List featured/discounted    | All users       |
| GET    | /api/products/autocomplete/       | Search autocomplete         | All users       |
| GET    | /api/categories/                  | List medicine categories    | All users       |

### Cart & Order Endpoints
| Method | Endpoint                      | Description                | Access       |
|--------|-------------------------------|-----------------------------|---------------|
| GET    | /api/cart/                   | View user's cart            | Authenticated |
| POST   | /api/cart/add_item/          | Add item to cart            | Authenticated |
| POST   | /api/cart/update_item/       | Update item quantity        | Authenticated |
| POST   | /api/cart/remove_item/       | Remove item from cart       | Authenticated |
| GET    | /api/orders/                 | List user's orders          | Authenticated |
| POST   | /api/orders/                 | Create order from cart      | Authenticated |
| POST   | /api/orders/{id}/payment/    | Create Razorpay payment     | Authenticated |
| POST   | /api/orders/{id}/callback/   | Razorpay payment callback   | Public        |
| PATCH  | /api/orders/{id}/status/     | Update order status         | Admin         |
| POST   | /api/orders/{id}/return/     | Request return              | Authenticated |

### Additional Endpoints
| Method | Endpoint                    | Description                       | Access        |
|--------|-----------------------------|------------------------------------|----------------|
| POST   | /api/prescriptions/         | Upload prescription                | Authenticated |
| PATCH  | /api/prescriptions/{id}/    | Review prescription (admin)        | Admin         |
| GET    | /api/addresses/             | List user's addresses              | Authenticated |
| POST   | /api/addresses/             | Add new address                    | Authenticated |
| GET    | /api/reviews/               | List product reviews               | All users     |
| POST   | /api/reviews/               | Create review (purchaser only)     | Authenticated |
| POST   | /api/apply_coupon/          | Apply and validate coupon          | Authenticated |

### Admin Endpoints
| Method | Endpoint              | Description                    | Access |
|--------|------------------------|-------------------------------|--------|
| GET    | /api/admin/users/     | List all users                 | Admin  |
| GET    | /api/admin/stats/     | Dashboard statistics           | Admin  |
| GET    | /api/admin/stats/chart/ | Monthly orders/revenue chart  | Admin  |

---

## 🧪 Testing
```bash
python manage.py check              # Django system check
python manage.py test               # Run all tests
python manage.py test api           # Run API tests only
```

---

## 🚢 Deployment

### Deploy to Render
1. Push code to GitHub
2. Create Web Service on Render
3. Connect GitHub repository
4. Build Command:
```bash
cd medicare_backend && pip install -r requirements.txt && python manage.py migrate
```
5. Start Command:
```bash
cd medicare_backend && gunicorn config.wsgi:application
```

### Deploy to Railway
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

---

## 👥 Default Users for Testing
| Role    | Email                  | Password      | Access Level         |
|---------|------------------------|---------------|----------------------|
| Admin   | admin@example.com      | admin123      | Full system access   |
| Customer| customer@example.com   | customer123   | Customer features    |

---

## 🐛 Troubleshooting
| Issue                      | Solution                                      |
|----------------------------|-----------------------------------------------|
| ModuleNotFoundError        | Activate virtual environment, run pip install |
| Database connection error  | Check .env file, verify MySQL is running      |
| Port 8000 in use           | Use `python manage.py runserver 8001`         |
| Static files not loading   | Run `python manage.py collectstatic`          |
| CORS errors                | Check CORS_ALLOWED_ORIGINS in settings        |
| Prescriptions not uploading | Verify media folder exists and has permissions |

---

## 🤝 Contributing
1. Fork the repository
2. Create feature branch:
```bash
git checkout -b feature/AmazingFeature
```
3. Commit changes:
```bash
git commit -m 'Add AmazingFeature'
```
4. Push branch:
```bash
git push origin feature/AmazingFeature
```
5. Open a Pull Request

---

## 🙏 Acknowledgments
- Django team for the excellent framework
- Django REST Framework community
- Razorpay for payment gateway
- Contributors and beta testers
- Open source community for invaluable tools

---

## 📞 Support
- Report Issues: [GitHub Issues](https://github.com/FlamingSlayer/MediStore/issues)
- Discussion: [GitHub Discussions](https://github.com/FlamingSlayer/MediStore/discussions)
- Contact: [Telegram](https://t.me/FlamingSlayer_Bot)

---

Built with ❤️ by **VidhyanJha**  
If you find this project helpful, please give it a ⭐ on GitHub!
